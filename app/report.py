"""Builds the three-column weekly report from JIRA search results.

Columns:
1. Progress & Risk
   - progress: issues completed (resolved) during the previous week.
   - risks: initiatives that are not Done and are overdue or due within
     ``risk_window_days``.
2. This week: issues currently in progress (what the team is working on now),
   optionally enriched with an AI summary of recent comments across the issue
   and its subtasks.
3. Milestones: every initiative and its deadline.
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
from typing import Any, Protocol

from .activity import CommentSource, collect_activity
from .config import Settings
from .dates import WeekWindows, compute_windows, parse_jira_datetime
from .models import (
    IssueSummary,
    MilestoneItem,
    ReportWindow,
    RiskItem,
    WeeklyReport,
)
from .summarizer import ActivitySummarizer

ISSUE_FIELDS = [
    "summary",
    "status",
    "issuetype",
    "duedate",
    "resolutiondate",
    "assignee",
    "priority",
    "updated",
]

# The "this week" query also needs subtask stubs for the activity summary.
THIS_WEEK_FIELDS = [*ISSUE_FIELDS, "subtasks"]

_DONE_CATEGORY = "Done"


class IssueSearcher(Protocol):
    async def search(self, jql: str, fields: list[str]) -> list[dict[str, Any]]: ...


# --------------------------------------------------------------------------- #
# JQL builders                                                                 #
# --------------------------------------------------------------------------- #
def _fmt(value: date) -> str:
    return value.strftime("%Y-%m-%d")


def progress_jql(settings: Settings, windows: WeekWindows) -> str:
    if settings.progress_jql:
        return settings.progress_jql
    return (
        f'project = "{settings.jira_project_key}" '
        f'AND resolutiondate >= "{_fmt(windows.last_week_start)}" '
        f'AND resolutiondate < "{_fmt(windows.this_week_start)}" '
        f"ORDER BY resolutiondate DESC"
    )


def risk_jql(settings: Settings, cutoff: date) -> str:
    if settings.risk_jql:
        return settings.risk_jql
    return (
        f'project = "{settings.jira_project_key}" '
        f'AND issuetype = "{settings.initiative_issue_type}" '
        f"AND statusCategory != Done "
        f'AND duedate <= "{_fmt(cutoff)}" '
        f"ORDER BY duedate ASC"
    )


def this_week_jql(settings: Settings) -> str:
    if settings.this_week_jql:
        return settings.this_week_jql
    return (
        f'project = "{settings.jira_project_key}" '
        f'AND statusCategory = "{settings.in_progress_status_category}" '
        f"ORDER BY updated DESC"
    )


def milestones_jql(settings: Settings) -> str:
    if settings.milestones_jql:
        return settings.milestones_jql
    return (
        f'project = "{settings.jira_project_key}" '
        f'AND issuetype = "{settings.initiative_issue_type}" '
        f"ORDER BY duedate ASC"
    )


# --------------------------------------------------------------------------- #
# Field parsing / mapping                                                      #
# --------------------------------------------------------------------------- #
def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _fields(raw: dict[str, Any]) -> dict[str, Any]:
    return raw.get("fields") or {}


def _name(node: Any) -> str | None:
    return node.get("name") if isinstance(node, dict) else None


def to_issue_summary(raw: dict[str, Any], base_url: str) -> IssueSummary:
    fields = _fields(raw)
    status = fields.get("status") or {}
    category = status.get("statusCategory") or {}
    assignee = fields.get("assignee") or {}
    key = raw.get("key") or ""
    return IssueSummary(
        key=key,
        summary=fields.get("summary") or "",
        status=status.get("name") or "",
        status_category=category.get("name") or "",
        issue_type=_name(fields.get("issuetype")) or "",
        assignee=assignee.get("displayName"),
        priority=_name(fields.get("priority")),
        due_date=_parse_date(fields.get("duedate")),
        resolution_date=parse_jira_datetime(fields.get("resolutiondate")),
        updated=parse_jira_datetime(fields.get("updated")),
        url=f"{base_url.rstrip('/')}/browse/{key}",
    )


def to_risk_item(raw: dict[str, Any], base_url: str, today: date) -> RiskItem:
    summary = to_issue_summary(raw, base_url)
    due = summary.due_date
    return RiskItem(
        **summary.model_dump(),
        days_until_due=(due - today).days if due else None,
        overdue=bool(due and due < today),
    )


def to_milestone(raw: dict[str, Any], base_url: str, today: date) -> MilestoneItem:
    fields = _fields(raw)
    status = fields.get("status") or {}
    category = status.get("statusCategory") or {}
    key = raw.get("key") or ""
    due = _parse_date(fields.get("duedate"))
    is_done = category.get("name") == _DONE_CATEGORY
    return MilestoneItem(
        key=key,
        summary=fields.get("summary") or "",
        status=status.get("name") or "",
        status_category=category.get("name") or "",
        due_date=due,
        overdue=bool(due and due < today and not is_done),
        url=f"{base_url.rstrip('/')}/browse/{key}",
    )


# --------------------------------------------------------------------------- #
# Report assembly                                                              #
# --------------------------------------------------------------------------- #
async def _summarize_one(
    semaphore: asyncio.Semaphore,
    comments: CommentSource,
    summarizer: ActivitySummarizer,
    issue: IssueSummary,
    raw: dict[str, Any],
    since: datetime,
) -> None:
    async with semaphore:
        activity = await collect_activity(comments, raw, since)
        issue.activity_summary = await summarizer.summarize(issue, activity)


async def _add_activity_summaries(
    comments: CommentSource,
    summarizer: ActivitySummarizer,
    issues: list[IssueSummary],
    raw_issues: list[dict[str, Any]],
    settings: Settings,
    now: datetime,
) -> None:
    """Attach an AI activity summary to each in-progress issue, in place."""
    since = now - timedelta(days=settings.activity_lookback_days)
    semaphore = asyncio.Semaphore(settings.summary_max_concurrency)
    await asyncio.gather(
        *(
            _summarize_one(semaphore, comments, summarizer, issue, raw, since)
            for issue, raw in zip(issues, raw_issues)
        )
    )


async def build_report(
    searcher: IssueSearcher,
    settings: Settings,
    now: datetime,
    summarizer: ActivitySummarizer | None = None,
) -> WeeklyReport:
    """Fetch the four JIRA queries concurrently and assemble the report.

    When ``summarizer`` is provided, ``searcher`` must also implement
    ``CommentSource`` so recent comments (issue + subtasks) can be summarized.
    """
    today = now.date()
    windows = compute_windows(today)
    cutoff = today + timedelta(days=settings.risk_window_days)
    base_url = settings.jira_base_url

    progress_raw, risk_raw, this_week_raw, milestones_raw = await asyncio.gather(
        searcher.search(progress_jql(settings, windows), ISSUE_FIELDS),
        searcher.search(risk_jql(settings, cutoff), ISSUE_FIELDS),
        searcher.search(this_week_jql(settings), THIS_WEEK_FIELDS),
        searcher.search(milestones_jql(settings), ISSUE_FIELDS),
    )

    this_week = [to_issue_summary(r, base_url) for r in this_week_raw]
    if summarizer is not None and this_week:
        await _add_activity_summaries(
            searcher,  # type: ignore[arg-type]  # JiraClient implements CommentSource
            summarizer,
            this_week,
            this_week_raw,
            settings,
            now,
        )

    return WeeklyReport(
        generated_at=now,
        project_key=settings.jira_project_key,
        window=ReportWindow(
            today=windows.today,
            this_week_start=windows.this_week_start,
            this_week_end=windows.this_week_end,
            last_week_start=windows.last_week_start,
            last_week_end=windows.last_week_end,
        ),
        progress=[to_issue_summary(r, base_url) for r in progress_raw],
        risks=[to_risk_item(r, base_url, today) for r in risk_raw],
        this_week=this_week,
        milestones=[to_milestone(r, base_url, today) for r in milestones_raw],
    )
