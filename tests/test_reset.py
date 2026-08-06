"""Tests for reset-cycle boundary calculations."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from custom_components.ha_daily_counter.reset import (
    current_period_start,
    next_reset_time,
)

LOCAL = ZoneInfo("Europe/Paris")


@pytest.mark.parametrize(
    ("cycle", "expected_start", "expected_next"),
    [
        ("quarter-hourly", (2026, 8, 6, 12, 30), (2026, 8, 6, 12, 45)),
        ("hourly", (2026, 8, 6, 12, 0), (2026, 8, 6, 13, 0)),
        ("daily", (2026, 8, 6, 0, 0), (2026, 8, 7, 0, 0)),
        ("weekly", (2026, 8, 3, 0, 0), (2026, 8, 10, 0, 0)),
        ("monthly", (2026, 8, 1, 0, 0), (2026, 9, 1, 0, 0)),
        ("bimonthly", (2026, 7, 1, 0, 0), (2026, 9, 1, 0, 0)),
        ("quarterly", (2026, 7, 1, 0, 0), (2026, 10, 1, 0, 0)),
        ("yearly", (2026, 1, 1, 0, 0), (2027, 1, 1, 0, 0)),
    ],
)
def test_cycle_boundaries(
    cycle: str,
    expected_start: tuple[int, int, int, int, int],
    expected_next: tuple[int, int, int, int, int],
) -> None:
    """Cycles use the expected local calendar boundaries."""
    now = datetime(2026, 8, 6, 12, 37, 42, tzinfo=LOCAL)

    assert current_period_start(now, cycle) == datetime(*expected_start, tzinfo=LOCAL)
    assert next_reset_time(now, cycle) == datetime(*expected_next, tzinfo=LOCAL)


def test_no_automatic_reset_has_no_boundaries() -> None:
    """The none cycle never schedules or expires restored state."""
    now = datetime(2026, 8, 6, 12, 37, tzinfo=LOCAL)
    assert current_period_start(now, "none") is None
    assert next_reset_time(now, "none") is None


def test_unknown_cycle_falls_back_to_daily() -> None:
    """Corrupt or future cycle values retain the safe daily behaviour."""
    now = datetime(2026, 8, 6, 12, 37, tzinfo=LOCAL)
    assert current_period_start(now, "unexpected") == datetime(
        2026, 8, 6, tzinfo=LOCAL
    )
    assert next_reset_time(now, "unexpected") == datetime(
        2026, 8, 7, tzinfo=LOCAL
    )
