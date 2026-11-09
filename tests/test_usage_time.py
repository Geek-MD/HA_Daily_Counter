"""Tests for usage-time accumulation helpers."""

from datetime import datetime, timedelta, timezone

from custom_components.ha_daily_counter.usage_time import (
    apply_usage_transition,
    current_duration_seconds,
    reset_usage_interval,
    usage_time_cache_key,
)

NOW = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)


def test_usage_time_cache_key_is_separate_from_service_keys() -> None:
    """Usage sensors use a private key that cannot look like an entity ID."""
    assert usage_time_cache_key("entry_counter") == "usage_time::entry_counter"


def test_current_duration_includes_active_interval() -> None:
    """An open interval is added to previously accumulated time."""
    assert current_duration_seconds(30, NOW - timedelta(seconds=90), NOW) == 120


def test_current_duration_uses_elapsed_time_across_offset_changes() -> None:
    """Daylight-saving offset changes do not add or lose an hour."""
    before_change = datetime.fromisoformat("2026-10-25T02:30:00+02:00")
    after_change = datetime.fromisoformat("2026-10-25T02:30:00+01:00")
    assert current_duration_seconds(0, before_change, after_change) == 3600


def test_entering_target_state_starts_interval() -> None:
    """A genuine transition into the selected state starts timing."""
    accumulated, active_since = apply_usage_transition(
        45,
        None,
        "off",
        "on",
        "on",
        NOW,
    )
    assert accumulated == 45
    assert active_since == NOW


def test_attribute_only_update_does_not_restart_interval() -> None:
    """Repeated reports of the target state preserve the original start."""
    started = NOW - timedelta(minutes=5)
    accumulated, active_since = apply_usage_transition(
        10,
        started,
        "on",
        "on",
        "on",
        NOW,
    )
    assert accumulated == 10
    assert active_since == started


def test_leaving_target_state_closes_interval() -> None:
    """A transition away from the selected state commits elapsed seconds."""
    accumulated, active_since = apply_usage_transition(
        30,
        NOW - timedelta(seconds=90),
        "on",
        "off",
        "on",
        NOW,
    )
    assert accumulated == 120
    assert active_since is None


def test_reset_restarts_interval_when_source_remains_active() -> None:
    """Time after a reset boundary is counted for an already-active source."""
    assert reset_usage_interval(True, NOW) == (0, NOW)
    assert reset_usage_interval(False, NOW) == (0, None)
