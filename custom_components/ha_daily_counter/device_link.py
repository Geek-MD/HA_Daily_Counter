"""Helpers for keeping counter and source device links in sync."""

from collections.abc import Mapping
from typing import Any


def source_registry_update_requires_sync(data: Mapping[str, Any]) -> bool:
    """Return whether a source registry event can change its device link."""
    return data["action"] == "create" or (
        data["action"] == "update" and "device_id" in data["changes"]
    )


def replacement_device_id(
    source_device_id: str | None,
    counter_device_id: str | None,
) -> str | None:
    """Return a new source device to apply, or None when no relink is needed."""
    if source_device_id is None or source_device_id == counter_device_id:
        return None
    return source_device_id


def sync_device_link(
    entity_registry: Any,
    source_entity_id: str,
    target_entity_id: str,
) -> bool:
    """Attach a target entity to the current device of its source entity."""
    source_entry = entity_registry.async_get(source_entity_id)
    target_entry = entity_registry.async_get(target_entity_id)
    if source_entry is None or target_entry is None:
        return False

    device_id = replacement_device_id(
        source_entry.device_id,
        target_entry.device_id,
    )
    if device_id is None:
        return False

    entity_registry.async_update_entity(target_entity_id, device_id=device_id)
    return True
