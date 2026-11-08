"""Tests for source-to-counter device-link synchronization."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from custom_components.ha_daily_counter.device_link import (
    replacement_device_id,
    source_registry_update_requires_sync,
    sync_device_link,
)


@pytest.mark.parametrize(
    ("event_data", "expected"),
    [
        ({"action": "create"}, True),
        ({"action": "update", "changes": {"device_id": "new-device"}}, True),
        ({"action": "update", "changes": {"name": "New name"}}, False),
        ({"action": "remove"}, False),
    ],
)
def test_source_registry_update_requires_sync(
    event_data: dict[str, object],
    expected: bool,
) -> None:
    """Only creation and device changes require a relink attempt."""
    assert source_registry_update_requires_sync(event_data) is expected


@pytest.mark.parametrize(
    ("source_device_id", "counter_device_id", "expected"),
    [
        ("new-device", None, "new-device"),
        ("new-device", "old-device", "new-device"),
        ("same-device", "same-device", None),
        (None, "virtual-fallback", None),
    ],
)
def test_replacement_device_id(
    source_device_id: str | None,
    counter_device_id: str | None,
    expected: str | None,
) -> None:
    """Relink to a real source device without discarding the fallback device."""
    assert replacement_device_id(source_device_id, counter_device_id) == expected


def test_sync_device_link_updates_target_registry_entry() -> None:
    """The target entity is moved to a replacement source device."""
    registry = Mock()
    registry.async_get.side_effect = [
        SimpleNamespace(device_id="new-device"),
        SimpleNamespace(device_id="old-device"),
    ]

    assert sync_device_link(registry, "sensor.source", "sensor.counter") is True
    registry.async_update_entity.assert_called_once_with(
        "sensor.counter",
        device_id="new-device",
    )


@pytest.mark.parametrize(
    ("source_entry", "target_entry"),
    [
        (None, SimpleNamespace(device_id="old-device")),
        (SimpleNamespace(device_id="new-device"), None),
        (SimpleNamespace(device_id=None), SimpleNamespace(device_id="fallback")),
        (
            SimpleNamespace(device_id="same-device"),
            SimpleNamespace(device_id="same-device"),
        ),
    ],
)
def test_sync_device_link_skips_when_no_relink_is_needed(
    source_entry: object,
    target_entry: object,
) -> None:
    """Missing, unassigned, and already-matching entries are left unchanged."""
    registry = Mock()
    registry.async_get.side_effect = [source_entry, target_entry]

    assert sync_device_link(registry, "sensor.source", "sensor.counter") is False
    registry.async_update_entity.assert_not_called()
