"""Helpers for applying per-cycle counting limits."""

from .const import COUNT_MODE_LIMITED


def can_increment(current_value: int, count_mode: str, max_changes: int) -> bool:
    """Return whether another matching transition may be counted this cycle."""
    return count_mode != COUNT_MODE_LIMITED or current_value < max_changes
