import asyncio
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app, get_settings
from app.mock_jira import MockJiraClient
from app.report import build_report
from tests.helpers import FakeSummarizer, make_settings


def teardown_function():
    app.dependency_overrides.clear()


def test_mock_client_feeds_every_column_and_the_summarizer():
    settings = make_settings()
    summarizer = FakeSummarizer("Mock AI summary")
    now = datetime.now(timezone.utc)

    report = asyncio.run(
        build_report(MockJiraClient(), settings, now, summarizer=summarizer)
    )

    assert report.progress and report.risks and report.this_week and report.milestones

    # Every completed issue has recent mock comments, so all get summaries.
    assert all(i.activity_summary == "Mock AI summary" for i in report.progress)
    # The "this week" column no longer carries summaries.
    assert all(i.activity_summary is None for i in report.this_week)

    # The summarizer saw comments from parents and their subtasks.
    by_key = {issue.key: activity for issue, activity in summarizer.requests}
    rate_limiter = by_key["ABC-10"]
    assert {s.key for s in rate_limiter.subtasks} == {"ABC-12", "ABC-13"}
    assert {c.issue_key for c in rate_limiter.comments} == {"ABC-10", "ABC-12", "ABC-13"}


def test_mock_mode_serves_the_api_without_jira():
    app.dependency_overrides[get_settings] = lambda: make_settings(mock_jira=True)
    client = TestClient(app)

    response = client.get("/api/report")
    assert response.status_code == 200

    body = response.json()
    # The sprint column includes cross-project and not-yet-started issues.
    assert [i["key"] for i in body["thisWeek"]] == ["ABC-20", "ABC-23", "ABC-24", "OPS-31"]
    # No OPENAI_API_KEY in test settings -> summaries disabled, field is null.
    assert all(i["activitySummary"] is None for i in body["thisWeek"])
