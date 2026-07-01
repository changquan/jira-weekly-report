"""Thin async client for JIRA Cloud's enhanced JQL search endpoint.

Uses ``POST /rest/api/3/search/jql`` (the current Cloud search API, which
replaced the deprecated ``/rest/api/3/search``) and follows ``nextPageToken``
pagination until all matching issues are collected.
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import Settings

SEARCH_PATH = "/rest/api/3/search/jql"


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
