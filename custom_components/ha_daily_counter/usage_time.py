"""Pure helpers for accumulating time spent in a monitored state."""

from datetime import datetime


def usage_time_cache_key(counter_unique_id: str) -> str:
    """Return the private cache key for a counter's usage-time sensor."""
    return f"usage_time::{counter_unique_id}"


def current_duration_seconds(
    accumulated_seconds: float,
    active_since: datetime | None,
    now: datetime,
) -> float:
    """Return accumulated duration including the currently active interval."""
    if active_since is None:
        return accumulated_seconds
    return accumulated_seconds + max(0.0, now.timestamp() - active_since.timestamp())


def apply_usage_transition(
    accumulated_seconds: float,
    active_since: datetime | None,
    old_state: str | None,
    new_state: str | None,
    target_state: str,
    now: datetime,
) -> tuple[float, datetime | None]:
    """Start or close an interval when the source enters or leaves its target."""
    if new_state == target_state and old_state != target_state:
        return accumulated_seconds, active_since or now
    if old_state == target_state and new_state != target_state:
        return current_duration_seconds(accumulated_seconds, active_since, now), None
    return accumulated_seconds, active_since


def reset_usage_interval(
    source_is_active: bool,
    now: datetime,
) -> tuple[float, datetime | None]:
    """Start a fresh period, retaining an active source from the boundary."""
    return 0.0, now if source_is_active else None
