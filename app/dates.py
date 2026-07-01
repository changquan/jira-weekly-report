"""Week-window arithmetic for the report.

Weeks run Monday -> Sunday. "This week" is the ISO week containing the
reference date; "last week" is the immediately preceding Monday->Sunday week.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


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
