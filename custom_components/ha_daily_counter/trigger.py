"""Helpers for evaluating counter trigger transitions."""


def entered_target_state(
    old_state: str | None,
    new_state: str | None,
    target_state: str,
) -> bool:
    """Return whether an entity has just transitioned into its target state.

    Home Assistant also emits state-change events when only an entity attribute
    changes.  In those events the old and new state strings are identical and
    must not be counted as a new occurrence.
    """
    return new_state == target_state and old_state != target_state
