"""An in-process stand-in for JIRA Cloud, enabled with ``MOCK_JIRA=true``.

Serves canned issues shaped exactly like the real search/comment payloads —
including subtasks and ADF comment bodies — so the whole pipeline (report
assembly, comment collection, AI summaries) can be exercised without a JIRA
instance. All dates are generated relative to "now" so resolved issues always
fall in last week and comments always fall inside the activity window.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _adf(*paragraphs: str) -> dict[str, Any]:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
            for text in paragraphs
        ],
    }


def _jira_ts(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%S.000%z")


def _comment(author: str, moment: datetime, *paragraphs: str) -> dict[str, Any]:
    return {
        "author": {"displayName": author},
        "created": _jira_ts(moment),
        "body": _adf(*paragraphs),
    }


def _subtask(key: str, summary: str, status: str, category: str) -> dict[str, Any]:
    return {
        "key": key,
        "fields": {
            "summary": summary,
            "status": {"name": status, "statusCategory": {"name": category}},
        },
    }


def _issue(
    key: str,
    summary: str,
    *,
    status: str = "To Do",
    category: str = "To Do",
    issue_type: str = "Story",
    assignee: str | None = None,
    priority: str | None = "Medium",
    duedate: str | None = None,
    resolutiondate: str | None = None,
    updated: str | None = None,
    subtasks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "key": key,
        "fields": {
            "summary": summary,
            "status": {"name": status, "statusCategory": {"name": category}},
            "issuetype": {"name": issue_type},
            "assignee": {"displayName": assignee} if assignee else None,
            "priority": {"name": priority} if priority else None,
            "duedate": duedate,
            "resolutiondate": resolutiondate,
            "updated": updated,
            "subtasks": subtasks or [],
        },
    }


class MockJiraClient:
    """Routes JQL queries and comment lookups to generated fixture data."""

    def __init__(self, initiative_issue_type: str = "Initiative") -> None:
        now = datetime.now(timezone.utc)
        days = lambda n: now - timedelta(days=n)  # noqa: E731
        fmt = lambda n: days(n).strftime("%Y-%m-%d")  # noqa: E731
        due_in = lambda n: (now + timedelta(days=n)).strftime("%Y-%m-%d")  # noqa: E731

        self._progress = [
            _issue(
                "ABC-10", "Roll out API rate limiter to all tenants",
                status="Done", category="Done", assignee="Dana Fox",
                resolutiondate=_jira_ts(days(4)), updated=_jira_ts(days(4)),
            ),
            _issue(
                "ABC-11", "Fix duplicate webhook deliveries on retry",
                status="Done", category="Done", issue_type="Bug",
                assignee="Lee Zhang", priority="High",
                resolutiondate=_jira_ts(days(5)), updated=_jira_ts(days(5)),
            ),
        ]

        self._risk = [
            _issue(
                "ABC-1", "Billing platform v2 GA",
                status="In Progress", category="In Progress",
                issue_type=initiative_issue_type, assignee="Dana Fox",
                priority="Highest", duedate=fmt(3),
            ),
            _issue(
                "ABC-2", "SOC 2 Type II audit readiness",
                status="In Progress", category="In Progress",
                issue_type=initiative_issue_type, assignee="Priya Nair",
                duedate=due_in(10),
            ),
        ]

        self._this_week = [
            _issue(
                "ABC-20", "Ship billing service v2 cutover",
                status="In Progress", category="In Progress",
                assignee="Dana Fox", priority="Highest",
                duedate=due_in(6), updated=_jira_ts(days(1)),
                subtasks=[
                    _subtask("ABC-21", "Write invoice data migration", "Done", "Done"),
                    _subtask("ABC-22", "Cut over invoice generation", "In Progress", "In Progress"),
                ],
            ),
            _issue(
                "ABC-23", "Migrate CI pipelines to GitHub Actions",
                status="In Progress", category="In Progress",
                assignee="Lee Zhang", updated=_jira_ts(days(2)),
            ),
            _issue(
                "ABC-24", "Acme Corp SSO integration",
                status="In Progress", category="In Progress",
                assignee="Priya Nair", priority="High",
                duedate=due_in(12), updated=_jira_ts(days(1)),
                subtasks=[
                    _subtask("ABC-25", "Rotate SAML signing certificate", "To Do", "To Do"),
                ],
            ),
        ]

        self._milestones = [
            *self._risk,
            _issue(
                "ABC-3", "Q2 infrastructure cost reduction",
                status="Done", category="Done",
                issue_type=initiative_issue_type, duedate=fmt(20),
            ),
        ]

        self._comments: dict[str, list[dict[str, Any]]] = {
            "ABC-20": [
                _comment(
                    "Dana Fox", days(5),
                    "Migration dry-run completed against a prod snapshot. "
                    "41M invoice rows migrated in 38 minutes, well inside the window.",
                ),
                _comment(
                    "Marcus Webb", days(3),
                    "Found duplicate invoice rows for tenants created before 2024 - "
                    "the migration was double-counting credit notes. Fix is up for review.",
                ),
                _comment(
                    "Dana Fox", days(1),
                    "Dedup fix merged and re-verified on staging. Cutover scheduled "
                    "for Thursday 06:00 UTC. Still waiting on finance sign-off for "
                    "the reconciliation report - that is the only remaining blocker.",
                ),
            ],
            "ABC-21": [
                _comment(
                    "Marcus Webb", days(4),
                    "Migration script merged. Added a rollback path that restores "
                    "from the pre-cutover snapshot in under 10 minutes.",
                ),
            ],
            "ABC-22": [
                _comment(
                    "Dana Fox", days(2),
                    "Invoice generation running in shadow mode - output matches the "
                    "legacy system for 99.97% of invoices. Investigating the "
                    "remaining mismatches, all in multi-currency accounts.",
                ),
            ],
            "ABC-23": [
                _comment(
                    "Lee Zhang", days(6),
                    "14 of 20 pipelines converted. Build times are down about 35% "
                    "thanks to dependency caching.",
                ),
                _comment(
                    "Lee Zhang", days(2),
                    "The e2e suite is flaky on the new runners - quarantined it and "
                    "opened a ticket with the vendor. Remaining 6 pipelines should "
                    "land early next week.",
                ),
            ],
            "ABC-24": [
                _comment(
                    "Priya Nair", days(4),
                    "SAML login working end-to-end against Acme's Okta sandbox.",
                ),
                _comment(
                    "Priya Nair", days(1),
                    "Blocked on Acme IT for the production IdP metadata - chased "
                    "again today, their change window is next Tuesday.",
                ),
            ],
            "ABC-25": [
                _comment(
                    "Sam Ortiz", days(3),
                    "New signing cert issued; rotation runbook drafted and waiting "
                    "for Priya's review before we schedule it.",
                ),
            ],
        }

    async def search(self, jql: str, fields: list[str]) -> list[dict[str, Any]]:
        if "resolutiondate >=" in jql:
            return self._progress
        if "statusCategory != Done" in jql:
            return self._risk
        if 'statusCategory = "In Progress"' in jql and "issuetype" not in jql:
            return self._this_week
        return self._milestones

    async def get_comments(self, issue_key: str) -> list[dict[str, Any]]:
        return self._comments.get(issue_key, [])
