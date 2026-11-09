"""Tests for per-cycle counting limits."""

import pytest

from custom_components.ha_daily_counter.counting import can_increment
from custom_components.ha_daily_counter.const import (
    DEFAULT_COUNT_MODE,
    DEFAULT_MAX_CHANGES,
)


def test_legacy_defaults_remain_unlimited() -> None:
    """Entries without the new options keep counting every matching change."""
    assert can_increment(5, DEFAULT_COUNT_MODE, DEFAULT_MAX_CHANGES)


@pytest.mark.parametrize("current_value", [0, 1, 10])
def test_all_mode_never_limits_matching_changes(current_value: int) -> None:
    """The backward-compatible default continues counting every change."""
    assert can_increment(current_value, "all", 1)


@pytest.mark.parametrize(
    ("current_value", "max_changes", "expected"),
    [(0, 1, True), (1, 1, False), (2, 3, True), (3, 3, False)],
)
def test_limited_mode_stops_at_configured_maximum(
    current_value: int, max_changes: int, expected: bool
) -> None:
    """Limited mode counts at most the configured number per reset cycle."""
    assert can_increment(current_value, "limited", max_changes) is expected


def test_unknown_mode_preserves_unlimited_behavior() -> None:
    """Unknown values fail open so old or future entries are not capped."""
    assert can_increment(5, "future-mode", 1)
