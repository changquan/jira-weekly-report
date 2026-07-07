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
    # Never read the developer's real .env (or OPENAI_API_KEY) in tests.
    return Settings(_env_file=None, **values)


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
    subtasks: list[dict[str, Any]] | None = None,
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
            "subtasks": subtasks or [],
        },
    }


def subtask_stub(key: str, summary: str = "Subtask", status: str = "To Do") -> dict[str, Any]:
    """The abbreviated subtask payload JIRA embeds in a parent issue."""
    return {
        "key": key,
        "fields": {
            "summary": summary,
            "status": {"name": status, "statusCategory": {"name": status}},
        },
    }


def comment(author: str, created: str, text: str) -> dict[str, Any]:
    """A raw JIRA comment with an ADF body."""
    return {
        "author": {"displayName": author},
        "created": created,
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": text}]}
            ],
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
        comments: dict[str, list[dict[str, Any]]] | None = None,
        comment_errors: set[str] | None = None,
    ) -> None:
        self.progress = progress or []
        self.risk = risk or []
        self.this_week = this_week or []
        self.milestones = milestones or []
        self.comments = comments or {}
        self.comment_errors = comment_errors or set()
        self.calls: list[str] = []
        self.fields_by_column: dict[str, list[str]] = {}
        self.comment_calls: list[str] = []

    async def search(self, jql: str, fields: list[str]) -> list[dict[str, Any]]:
        self.calls.append(jql)
        if "resolutiondate >=" in jql:
            self.fields_by_column["progress"] = fields
            return self.progress
        if "statusCategory != Done" in jql:
            self.fields_by_column["risk"] = fields
            return self.risk
        if "openSprints()" in jql:
            self.fields_by_column["this_week"] = fields
            return self.this_week
        self.fields_by_column["milestones"] = fields
        return self.milestones

    async def get_comments(self, issue_key: str) -> list[dict[str, Any]]:
        self.comment_calls.append(issue_key)
        if issue_key in self.comment_errors:
            raise RuntimeError(f"comment fetch failed for {issue_key}")
        return self.comments.get(issue_key, [])


class FakeSummarizer:
    """Records what it was asked to summarize and returns a canned blurb."""

    def __init__(self, text: str | None = "AI summary") -> None:
        self.text = text
        self.requests: list[tuple[Any, Any]] = []

    async def summarize(self, issue: Any, activity: Any) -> str | None:
        self.requests.append((issue, activity))
        if not activity.comments:
            return None
        return self.text
