"""Collects recent activity (comments + subtasks) for an in-progress issue.

JIRA Cloud returns comment bodies in Atlassian Document Format (ADF), a
nested JSON tree; ``adf_to_text`` flattens it to plain text for the AI
summarizer. ``collect_activity`` gathers comments on the issue itself and on
every subtask, keeping only those created within the reporting window.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from .dates import parse_jira_datetime


class CommentSource(Protocol):
    async def get_comments(self, issue_key: str) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class ActivityComment:
    issue_key: str  # the issue or subtask the comment was left on
    author: str
    created: datetime
    text: str


@dataclass(frozen=True)
class SubtaskInfo:
    key: str
    summary: str
    status: str


@dataclass(frozen=True)
class IssueActivity:
    subtasks: list[SubtaskInfo] = field(default_factory=list)
    comments: list[ActivityComment] = field(default_factory=list)


# Blocks whose children should be separated by newlines when flattened.
_ADF_BLOCK_NODES = {
    "paragraph", "heading", "blockquote", "listItem", "codeBlock",
    "tableRow", "panel",
}


def adf_to_text(node: Any) -> str:
    """Flatten an ADF node (or whole document) to plain text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_to_text(child) for child in node)
    if not isinstance(node, dict):
        return ""

    node_type = node.get("type")
    if node_type == "text":
        return node.get("text") or ""
    if node_type == "hardBreak":
        return "\n"
    if node_type == "mention":
        return (node.get("attrs") or {}).get("text") or ""
    if node_type == "emoji":
        return (node.get("attrs") or {}).get("shortName") or ""

    text = "".join(adf_to_text(child) for child in node.get("content") or [])
    if node_type in _ADF_BLOCK_NODES and text and not text.endswith("\n"):
        text += "\n"
    return text


def parse_subtasks(raw_issue: dict[str, Any]) -> list[SubtaskInfo]:
    """Read the ``subtasks`` field from a raw JIRA issue payload."""
    subtasks = (raw_issue.get("fields") or {}).get("subtasks") or []
    parsed: list[SubtaskInfo] = []
    for sub in subtasks:
        fields = sub.get("fields") or {}
        status = fields.get("status") or {}
        parsed.append(
            SubtaskInfo(
                key=sub.get("key") or "",
                summary=fields.get("summary") or "",
                status=status.get("name") or "",
            )
        )
    return parsed


def _is_recent(created: datetime, since: datetime) -> bool:
    # JIRA timestamps are tz-aware; tolerate a naive reference (e.g. tests).
    if (created.tzinfo is None) != (since.tzinfo is None):
        created = created.replace(tzinfo=None)
        since = since.replace(tzinfo=None)
    return created >= since


def _to_activity_comment(
    issue_key: str, raw: dict[str, Any], since: datetime
) -> ActivityComment | None:
    created = parse_jira_datetime(raw.get("created"))
    if created is None or not _is_recent(created, since):
        return None
    author = (raw.get("author") or {}).get("displayName") or "Unknown"
    text = adf_to_text(raw.get("body")).strip()
    if not text:
        return None
    return ActivityComment(issue_key=issue_key, author=author, created=created, text=text)


async def collect_activity(
    source: CommentSource, raw_issue: dict[str, Any], since: datetime
) -> IssueActivity:
    """Gather subtasks and window-filtered comments for an issue tree."""
    issue_key = raw_issue.get("key") or ""
    subtasks = parse_subtasks(raw_issue)
    keys = [issue_key] + [s.key for s in subtasks if s.key]

    comment_pages = await asyncio.gather(*(source.get_comments(key) for key in keys))

    comments: list[ActivityComment] = []
    for key, page in zip(keys, comment_pages):
        for raw_comment in page:
            comment = _to_activity_comment(key, raw_comment, since)
            if comment is not None:
                comments.append(comment)

    comments.sort(key=lambda c: c.created)
    return IssueActivity(subtasks=subtasks, comments=comments)
