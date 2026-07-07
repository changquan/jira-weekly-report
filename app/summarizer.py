"""AI summaries of the progress made on each completed issue.

Uses the OpenAI SDK to turn the comments left during the reporting window
(including the subtasks' comments) into a 1-3 sentence plain-language blurb
of what was done, for the "Progress" column. A summarizer failure never
fails the report — the issue simply renders without a summary.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

import openai

from .activity import IssueActivity
from .config import Settings
from .models import IssueSummary

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You summarize JIRA activity for a weekly management report. Given a "
    "completed issue, its subtasks, and the comments left during the "
    "reporting window, write 1-3 sentences describing what was actually "
    "done to deliver it. Write in plain language for managers, in the past "
    "tense: lead with the concrete work that was completed, note anything "
    "notable that came up along the way, and do not repeat the issue title "
    "or restate metadata like keys and statuses. Only report work that the "
    "comments support. Respond with the summary only - no preamble, no "
    "markdown."
)

_MAX_COMMENT_CHARS = 2000
_MAX_COMMENTS = 30


class ActivitySummarizer(Protocol):
    async def summarize(
        self, issue: IssueSummary, activity: IssueActivity
    ) -> str | None: ...


def build_activity_prompt(issue: IssueSummary, activity: IssueActivity) -> str:
    """Render the issue tree and its recent comments as the user prompt."""
    lines = [
        f"Issue {issue.key}: {issue.summary}",
        f"Status: {issue.status}" + (f" | Assignee: {issue.assignee}" if issue.assignee else ""),
    ]
    if issue.resolution_date:
        lines.append(f"Resolved: {issue.resolution_date:%Y-%m-%d}")

    if activity.subtasks:
        lines.append("\nSubtasks:")
        for sub in activity.subtasks:
            lines.append(f"- {sub.key} [{sub.status}] {sub.summary}")

    if activity.comments:
        lines.append("\nComments during the reporting window (oldest first):")
        for comment in activity.comments[-_MAX_COMMENTS:]:
            text = comment.text[:_MAX_COMMENT_CHARS]
            lines.append(
                f"- [{comment.issue_key}] {comment.author} "
                f"({comment.created:%Y-%m-%d}): {text}"
            )
    else:
        lines.append("\nNo comments were left during the reporting window.")

    return "\n".join(lines)


class OpenAIActivitySummarizer:
    """Summarizes issue activity with the OpenAI API."""

    def __init__(self, settings: Settings) -> None:
        self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def summarize(
        self, issue: IssueSummary, activity: IssueActivity
    ) -> str | None:
        if not activity.comments:
            # Subtask stubs alone say nothing about what was done.
            return None
        # Reasoning models (gpt-5*, o*) spend completion tokens on hidden
        # reasoning first; keep that minimal and leave headroom so the cap is
        # never exhausted before any visible text is produced.
        extra: dict[str, Any] = (
            {"reasoning_effort": "minimal"}
            if self._model.startswith(("gpt-5", "o"))
            else {}
        )
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_completion_tokens=2000,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": build_activity_prompt(issue, activity)},
                ],
                **extra,
            )
        except openai.OpenAIError as exc:
            logger.warning("Activity summary failed for %s: %s", issue.key, exc)
            return None

        text = (response.choices[0].message.content or "").strip()
        return text or None
