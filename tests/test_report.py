import asyncio
from datetime import datetime

from app.report import (
    build_report,
    milestones_jql,
    progress_jql,
    risk_jql,
    this_week_jql,
    to_risk_item,
)
from app.dates import compute_windows
from tests.helpers import FakeSearcher, issue, make_settings

NOW = datetime(2026, 7, 1, 9, 0, 0)  # Wednesday
TODAY = NOW.date()


def test_jql_builders_use_config():
    settings = make_settings(jira_project_key="OPS", initiative_issue_type="Epic")
    windows = compute_windows(TODAY)

    assert 'project = "OPS"' in progress_jql(settings, windows)
    assert 'resolutiondate >= "2026-06-22"' in progress_jql(settings, windows)
    assert 'resolutiondate < "2026-06-29"' in progress_jql(settings, windows)

    risk = risk_jql(settings, TODAY.replace(day=15))
    assert 'issuetype = "Epic"' in risk
    assert "statusCategory != Done" in risk
    assert 'duedate <= "2026-07-15"' in risk

    # This-week = the active sprint; sprints can span projects, so the
    # default query must not be scoped to the configured project.
    assert "sprint in openSprints()" in this_week_jql(settings)
    assert "project" not in this_week_jql(settings)
    assert 'issuetype = "Epic"' in milestones_jql(settings)


def test_jql_override_is_used_verbatim():
    settings = make_settings(progress_jql="project = X AND foo = bar")
    windows = compute_windows(TODAY)
    assert progress_jql(settings, windows) == "project = X AND foo = bar"


def test_to_risk_item_flags_overdue_and_countdown():
    settings = make_settings()
    overdue = issue(
        "ABC-1", issue_type="Initiative", status="In Progress",
        category="In Progress", duedate="2026-06-25",
    )
    upcoming = issue(
        "ABC-2", issue_type="Initiative", status="To Do",
        category="To Do", duedate="2026-07-10",
    )

    r1 = to_risk_item(overdue, settings.jira_base_url, TODAY)
    r2 = to_risk_item(upcoming, settings.jira_base_url, TODAY)

    assert r1.overdue is True
    assert r1.days_until_due == -6
    assert r1.url == "https://example.atlassian.net/browse/ABC-1"

    assert r2.overdue is False
    assert r2.days_until_due == 9


def test_build_report_assembles_all_columns():
    settings = make_settings()
    searcher = FakeSearcher(
        progress=[
            issue("ABC-10", status="Done", category="Done",
                  resolutiondate="2026-06-25T13:45:00.000+0000"),
        ],
        risk=[
            issue("ABC-1", issue_type="Initiative", category="In Progress",
                  duedate="2026-06-25"),
            issue("ABC-2", issue_type="Initiative", category="To Do",
                  duedate="2026-07-10"),
        ],
        this_week=[
            issue("ABC-20", status="In Progress", category="In Progress",
                  assignee="Dana"),
        ],
        milestones=[
            issue("ABC-1", issue_type="Initiative", category="In Progress",
                  duedate="2026-06-25"),
            issue("ABC-2", issue_type="Initiative", category="To Do",
                  duedate="2026-07-10"),
            issue("ABC-3", issue_type="Initiative", status="Done",
                  category="Done", duedate="2026-05-01"),
        ],
    )

    report = asyncio.run(build_report(searcher, settings, NOW))

    assert report.project_key == "ABC"
    assert report.generated_at == NOW
    assert report.window.last_week_start.isoformat() == "2026-06-22"

    # The progress query must fetch subtask stubs for the activity summaries;
    # the this-week query no longer needs them.
    assert "subtasks" in searcher.fields_by_column["progress"]
    assert "subtasks" not in searcher.fields_by_column["this_week"]

    assert [i.key for i in report.progress] == ["ABC-10"]
    assert report.progress[0].resolution_date is not None

    assert [r.key for r in report.risks] == ["ABC-1", "ABC-2"]
    assert report.risks[0].overdue is True

    assert [i.key for i in report.this_week] == ["ABC-20"]
    assert report.this_week[0].assignee == "Dana"

    # Done initiative in the past is not flagged overdue.
    done_milestone = next(m for m in report.milestones if m.key == "ABC-3")
    assert done_milestone.overdue is False
    overdue_milestone = next(m for m in report.milestones if m.key == "ABC-1")
    assert overdue_milestone.overdue is True
