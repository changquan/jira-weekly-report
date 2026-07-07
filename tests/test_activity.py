import asyncio
from datetime import datetime

from app.activity import adf_to_text, collect_activity
from app.models import IssueSummary
from app.report import build_report
from app.summarizer import build_activity_prompt
from tests.helpers import (
    FakeSearcher,
    FakeSummarizer,
    comment,
    issue,
    make_settings,
    subtask_stub,
)

NOW = datetime(2026, 7, 1, 9, 0, 0)  # Wednesday
SINCE = datetime(2026, 6, 24, 9, 0, 0)


def test_adf_to_text_flattens_paragraphs_mentions_and_breaks():
    doc = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Deployed to "},
                    {"type": "text", "text": "staging"},
                    {"type": "hardBreak"},
                    {"type": "mention", "attrs": {"text": "@Dana"}},
                    {"type": "text", "text": " please verify"},
                ],
            },
            {
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": "item one"}],
                            }
                        ],
                    }
                ],
            },
        ],
    }
    assert adf_to_text(doc) == "Deployed to staging\n@Dana please verify\nitem one\n"


def test_collect_activity_gathers_issue_and_subtask_comments_in_window():
    parent = issue(
        "ABC-20",
        status="In Progress",
        category="In Progress",
        subtasks=[
            subtask_stub("ABC-21", "Write migration", "Done"),
            subtask_stub("ABC-22", "Update docs", "In Progress"),
        ],
    )
    searcher = FakeSearcher(
        comments={
            "ABC-20": [
                comment("Dana", "2026-06-30T10:00:00.000+0000", "Migration deployed"),
                comment("Dana", "2026-06-01T10:00:00.000+0000", "Old kickoff note"),
            ],
            "ABC-21": [
                comment("Lee", "2026-06-29T15:00:00.000+0000", "Schema change merged"),
            ],
        }
    )

    activity = asyncio.run(collect_activity(searcher, parent, SINCE))

    assert [s.key for s in activity.subtasks] == ["ABC-21", "ABC-22"]
    assert searcher.comment_calls == ["ABC-20", "ABC-21", "ABC-22"]
    # The stale comment is filtered out; the rest are oldest-first.
    assert [(c.issue_key, c.author) for c in activity.comments] == [
        ("ABC-21", "Lee"),
        ("ABC-20", "Dana"),
    ]
    assert activity.comments[1].text == "Migration deployed"


def test_build_activity_prompt_includes_subtasks_and_comments():
    parent = issue(
        "ABC-20",
        summary="Ship billing v2",
        status="In Progress",
        category="In Progress",
        subtasks=[subtask_stub("ABC-21", "Write migration", "Done")],
    )
    searcher = FakeSearcher(
        comments={
            "ABC-21": [comment("Lee", "2026-06-29T15:00:00.000+0000", "Merged")],
        }
    )
    activity = asyncio.run(collect_activity(searcher, parent, SINCE))
    summary = IssueSummary(
        key="ABC-20", summary="Ship billing v2", status="In Progress",
        status_category="In Progress", issue_type="Story", assignee="Dana",
        url="https://example.atlassian.net/browse/ABC-20",
    )

    prompt = build_activity_prompt(summary, activity)

    assert "Issue ABC-20: Ship billing v2" in prompt
    assert "- ABC-21 [Done] Write migration" in prompt
    assert "Lee (2026-06-29): Merged" in prompt


def test_build_report_attaches_activity_summaries_to_this_week():
    settings = make_settings()
    searcher = FakeSearcher(
        this_week=[
            issue(
                "ABC-20", status="In Progress", category="In Progress",
                subtasks=[subtask_stub("ABC-21")],
            ),
            issue("ABC-30", status="In Progress", category="In Progress"),
        ],
        comments={
            "ABC-20": [comment("Dana", "2026-06-30T10:00:00.000+0000", "Deployed")],
        },
    )
    summarizer = FakeSummarizer("Deployed the migration to staging.")

    report = asyncio.run(build_report(searcher, settings, NOW, summarizer=summarizer))

    by_key = {i.key: i for i in report.this_week}
    assert by_key["ABC-20"].activity_summary == "Deployed the migration to staging."
    # ABC-30 has subtask-less, comment-less activity -> summarizer returns None.
    assert by_key["ABC-30"].activity_summary is None
    # Comments were fetched for the parent and its subtask, plus the bare issue.
    assert sorted(searcher.comment_calls) == ["ABC-20", "ABC-21", "ABC-30"]


def test_build_report_without_summarizer_skips_comment_fetching():
    settings = make_settings()
    searcher = FakeSearcher(
        this_week=[issue("ABC-20", status="In Progress", category="In Progress")],
    )

    report = asyncio.run(build_report(searcher, settings, NOW))

    assert report.this_week[0].activity_summary is None
    assert searcher.comment_calls == []
