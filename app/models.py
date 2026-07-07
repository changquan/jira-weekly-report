"""Pydantic response models for the weekly report API.

All models serialize to camelCase JSON (e.g. ``status_category`` -> ``statusCategory``)
while keeping snake_case field names in Python.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class IssueSummary(CamelModel):
    """A single JIRA issue rendered for the report."""

    key: str
    summary: str
    status: str
    status_category: str
    issue_type: str
    assignee: str | None = None
    priority: str | None = None
    due_date: date | None = None
    resolution_date: datetime | None = None
    updated: datetime | None = None
    url: str
    # AI-generated blurb of recent activity (comments across the issue and its
    # subtasks); only populated for in-progress issues when summaries are enabled.
    activity_summary: str | None = None


class RiskItem(IssueSummary):
    """An initiative flagged as at risk of missing its due date."""

    days_until_due: int | None = None
    overdue: bool = False


class MilestoneItem(CamelModel):
    """An initiative shown in the milestones & deadlines column."""

    key: str
    summary: str
    status: str
    status_category: str
    due_date: date | None = None
    overdue: bool = False
    url: str


class ReportWindow(CamelModel):
    """The date windows the report was computed against."""

    today: date
    this_week_start: date
    this_week_end: date
    last_week_start: date
    last_week_end: date


class WeeklyReport(CamelModel):
    """The full three-column weekly report for management.

    - ``progress`` + ``risks`` form column 1 (Progress & Risk).
    - ``this_week`` is column 2 (what the team is working on this week).
    - ``milestones`` is column 3 (key milestones & deadlines).
    """

    generated_at: datetime
    project_key: str
    window: ReportWindow
    progress: list[IssueSummary] = []
    risks: list[RiskItem] = []
    this_week: list[IssueSummary] = []
    milestones: list[MilestoneItem] = []
