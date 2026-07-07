"""FastAPI application exposing the weekly report as JSON."""

from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query

from .config import Settings
from .jira_client import JiraClient
from .mock_jira import MockJiraClient
from .models import WeeklyReport
from .report import build_report
from .summarizer import OpenAIActivitySummarizer

app = FastAPI(
    title="JIRA Weekly Report API",
    version="0.1.0",
    description=(
        "Backend that assembles a three-column weekly management report "
        "(Progress & Risk, This Week, Milestones & Deadlines) from JIRA Cloud."
    ),
)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from env/.env


def get_searcher(
    settings: Settings = Depends(get_settings),
) -> JiraClient | MockJiraClient:
    if settings.mock_jira:
        return MockJiraClient(settings.initiative_issue_type)
    return JiraClient(settings)


def get_summarizer(
    settings: Settings = Depends(get_settings),
) -> OpenAIActivitySummarizer | None:
    if not settings.openai_api_key:
        return None
    return OpenAIActivitySummarizer(settings)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/report", response_model=WeeklyReport)
async def get_report(
    as_of: date | None = Query(
        default=None,
        description=(
            "Generate the report as of this date (YYYY-MM-DD). "
            "Defaults to today; windows are computed relative to it."
        ),
    ),
    settings: Settings = Depends(get_settings),
    searcher: JiraClient | MockJiraClient = Depends(get_searcher),
    summarizer: OpenAIActivitySummarizer | None = Depends(get_summarizer),
) -> WeeklyReport:
    now = datetime.now().astimezone()
    if as_of is not None:
        now = datetime.combine(as_of, datetime.min.time()).astimezone()

    try:
        return await build_report(searcher, settings, now, summarizer=summarizer)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"JIRA request failed: {exc.response.status_code} {exc.response.text[:200]}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach JIRA: {exc}") from exc
