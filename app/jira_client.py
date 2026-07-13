"""Thin async client for JIRA Cloud's search and comment endpoints.

Search uses ``POST /rest/api/3/search/jql`` (the current Cloud search API,
which replaced the deprecated ``/rest/api/3/search``) and follows
``nextPageToken`` pagination until all matching issues are collected.
Comments use ``GET /rest/api/3/issue/{key}/comment`` with offset pagination.
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import Settings

SEARCH_PATH = "/rest/api/3/search/jql"
COMMENT_PATH = "/rest/api/3/issue/{key}/comment"


class JiraClient:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.jira_base_url.rstrip("/")
        self._auth = (settings.jira_email, settings.jira_api_token)
        self._timeout = settings.request_timeout_seconds
        self._page_size = settings.max_results_per_page

    async def search(self, jql: str, fields: list[str]) -> list[dict[str, Any]]:
        """Run a JQL search and return every matching issue (all pages)."""
        issues: list[dict[str, Any]] = []
        next_token: str | None = None

        async with httpx.AsyncClient(timeout=self._timeout, auth=self._auth) as client:
            while True:
                payload: dict[str, Any] = {
                    "jql": jql,
                    "fields": fields,
                    "maxResults": self._page_size,
                }
                if next_token:
                    payload["nextPageToken"] = next_token

                response = await client.post(
                    f"{self._base_url}{SEARCH_PATH}",
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                issues.extend(data.get("issues") or [])

                next_token = data.get("nextPageToken")
                if data.get("isLast") or not next_token:
                    break

        return issues

    async def get_comments(self, issue_key: str) -> list[dict[str, Any]]:
        """Fetch every comment on an issue, newest first (all pages)."""
        comments: list[dict[str, Any]] = []
        start_at = 0

        async with httpx.AsyncClient(timeout=self._timeout, auth=self._auth) as client:
            while True:
                response = await client.get(
                    f"{self._base_url}{COMMENT_PATH.format(key=issue_key)}",
                    params={
                        "startAt": start_at,
                        "maxResults": self._page_size,
                        "orderBy": "-created",
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                data = response.json()

                page = data.get("comments") or []
                comments.extend(page)

                start_at += len(page)
                if not page or start_at >= (data.get("total") or 0):
                    break

        return comments
