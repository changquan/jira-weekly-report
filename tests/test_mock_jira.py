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

    # Every in-progress issue has recent mock activity, so all get summaries.
    assert all(i.activity_summary == "Mock AI summary" for i in report.this_week)

    # The summarizer saw comments from parents and their subtasks.
    by_key = {issue.key: activity for issue, activity in summarizer.requests}
    billing = by_key["ABC-20"]
    assert {s.key for s in billing.subtasks} == {"ABC-21", "ABC-22"}
    assert {c.issue_key for c in billing.comments} == {"ABC-20", "ABC-21", "ABC-22"}
    assert any("finance sign-off" in c.text for c in billing.comments)


def test_mock_mode_serves_the_api_without_jira():
    app.dependency_overrides[get_settings] = lambda: make_settings(mock_jira=True)
    client = TestClient(app)

    response = client.get("/api/report")
    assert response.status_code == 200

    body = response.json()
    assert [i["key"] for i in body["thisWeek"]] == ["ABC-20", "ABC-23", "ABC-24"]
    # No OPENAI_API_KEY in test settings -> summaries disabled, field is null.
    assert all(i["activitySummary"] is None for i in body["thisWeek"])
