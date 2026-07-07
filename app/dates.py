"""Week-window arithmetic and JIRA datetime parsing for the report.

Weeks run Monday -> Sunday. "This week" is the ISO week containing the
reference date; "last week" is the immediately preceding Monday->Sunday week.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

_TZ_NO_COLON = re.compile(r"(.*)([+-]\d{2})(\d{2})$")


def parse_jira_datetime(value: str | None) -> datetime | None:
    """Parse a JIRA datetime such as ``2026-06-25T13:45:00.000+0000``."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        match = _TZ_NO_COLON.match(value)
        if match:
            normalized = f"{match.group(1)}{match.group(2)}:{match.group(3)}"
            return datetime.fromisoformat(normalized)
        raise


@dataclass(frozen=True)
class WeekWindows:
    today: date
    this_week_start: date  # Monday of the current week
    this_week_end: date  # Sunday of the current week
    last_week_start: date  # Monday of the previous week
    last_week_end: date  # Sunday of the previous week


def compute_windows(today: date) -> WeekWindows:
    """Compute this-week / last-week windows relative to ``today``."""
    this_week_start = today - timedelta(days=today.weekday())  # Monday
    this_week_end = this_week_start + timedelta(days=6)  # Sunday
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)
    return WeekWindows(
        today=today,
        this_week_start=this_week_start,
        this_week_end=this_week_end,
        last_week_start=last_week_start,
        last_week_end=last_week_end,
    )
