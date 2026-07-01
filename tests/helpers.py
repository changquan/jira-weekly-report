"""Shared test fixtures: a fake searcher and a JIRA issue factory."""

from __future__ import annotations

from typing import Any

from app.config import Settings


def make_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "jira_base_url": "https://example.atlassian.net",
        "jira_email": "reporter@example.com",
        "jira_api_token": "token",
        "jira_project_key": "ABC",
    }
    values.update(overrides)
    return Settings(**values)


def issue(
    key: str,
    *,
    summary: str = "Summary",
    status: str = "To Do",
    category: str = "To Do",
    issue_type: str = "Story",
    duedate: str | None = None,
    resolutiondate: str | None = None,
    assignee: str | None = None,
    priority: str | None = None,
    updated: str | None = None,
) -> dict[str, Any]:
    return {
        "key": key,
        "fields": {
            "summary": summary,
            "status": {"name": status, "statusCategory": {"name": category}},
            "issuetype": {"name": issue_type},
            "duedate": duedate,
            "resolutiondate": resolutiondate,
            "assignee": {"displayName": assignee} if assignee else None,
            "priority": {"name": priority} if priority else None,
            "updated": updated,
        },
    }


class FakeSearcher:
    """Routes each JQL query to a canned issue list based on its shape."""

    def __init__(
        self,
        *,
        progress: list[dict[str, Any]] | None = None,
        risk: list[dict[str, Any]] | None = None,
        this_week: list[dict[str, Any]] | None = None,
        milestones: list[dict[str, Any]] | None = None,
    ) -> None:
        self.progress = progress or []
        self.risk = risk or []
        self.this_week = this_week or []
        self.milestones = milestones or []
        self.calls: list[str] = []

    async def search(self, jql: str, fields: list[str]) -> list[dict[str, Any]]:
        self.calls.append(jql)
        if "resolutiondate >=" in jql:
            return self.progress
        if "statusCategory != Done" in jql:
            return self.risk
        if 'statusCategory = "In Progress"' in jql:
            return self.this_week
        return self.milestones
