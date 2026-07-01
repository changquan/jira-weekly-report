from fastapi.testclient import TestClient

from app.main import app, get_searcher, get_settings
from tests.helpers import FakeSearcher, issue, make_settings


def build_client(searcher: FakeSearcher) -> TestClient:
    app.dependency_overrides[get_settings] = lambda: make_settings()
    app.dependency_overrides[get_searcher] = lambda: searcher
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_report_endpoint_returns_camelcase_columns():
    searcher = FakeSearcher(
        progress=[issue("ABC-10", status="Done", category="Done",
                        resolutiondate="2026-06-25T13:45:00.000+0000")],
        risk=[issue("ABC-1", issue_type="Initiative", category="To Do",
                    duedate="2026-07-10")],
        this_week=[issue("ABC-20", status="In Progress", category="In Progress")],
        milestones=[issue("ABC-1", issue_type="Initiative", category="To Do",
                          duedate="2026-07-10")],
    )
    client = build_client(searcher)

    response = client.get("/api/report", params={"as_of": "2026-07-01"})
    assert response.status_code == 200

    body = response.json()
    assert body["projectKey"] == "ABC"
    assert body["window"]["lastWeekStart"] == "2026-06-22"
    assert body["progress"][0]["key"] == "ABC-10"
    assert body["risks"][0]["daysUntilDue"] == 9
    assert body["thisWeek"][0]["key"] == "ABC-20"
    assert body["milestones"][0]["dueDate"] == "2026-07-10"
    # Four JIRA queries were issued (progress, risk, this-week, milestones).
    assert len(searcher.calls) == 4
