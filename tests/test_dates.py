from datetime import date

from app.dates import compute_windows


def test_windows_for_midweek_date():
    # 2026-07-01 is a Wednesday.
    windows = compute_windows(date(2026, 7, 1))
    assert windows.this_week_start == date(2026, 6, 29)  # Monday
    assert windows.this_week_end == date(2026, 7, 5)  # Sunday
    assert windows.last_week_start == date(2026, 6, 22)
    assert windows.last_week_end == date(2026, 6, 28)


def test_windows_on_monday():
    windows = compute_windows(date(2026, 6, 29))  # Monday
    assert windows.this_week_start == date(2026, 6, 29)
    assert windows.last_week_start == date(2026, 6, 22)
    assert windows.last_week_end == date(2026, 6, 28)


def test_windows_on_sunday():
    windows = compute_windows(date(2026, 7, 5))  # Sunday
    assert windows.this_week_start == date(2026, 6, 29)
    assert windows.this_week_end == date(2026, 7, 5)
