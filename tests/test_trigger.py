"""Tests for trigger transition evaluation."""

import pytest

from custom_components.ha_daily_counter.trigger import entered_target_state


@pytest.mark.parametrize(
    ("old_state", "new_state", "target_state", "expected"),
    [
        ("off", "on", "on", True),
        (None, "on", "on", True),
        ("on", "on", "on", False),
        ("on", "off", "on", False),
        ("off", None, "on", False),
    ],
)
def test_entered_target_state(
    old_state: str | None,
    new_state: str | None,
    target_state: str,
    expected: bool,
) -> None:
    """Only a genuine transition into the configured state is counted."""
    assert entered_target_state(old_state, new_state, target_state) is expected
