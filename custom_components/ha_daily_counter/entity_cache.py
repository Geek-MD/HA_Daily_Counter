"""Helpers for indexing counter entities used by integration services."""

from typing import Any


def cache_entity(
    cache: dict[str, Any],
    entity_id: str,
    unique_id: str,
    entity: Any,
) -> None:
    """Index a counter by its mutable entity ID and stable unique ID."""
    cache[entity_id] = entity
    cache[unique_id] = entity


def rekey_cached_entity(
    cache: dict[str, Any],
    old_entity_id: str,
    new_entity_id: str,
    entity: Any,
) -> None:
    """Move an entity-ID cache entry after an in-place registry rename."""
    if cache.get(old_entity_id) is entity:
        cache.pop(old_entity_id)
    cache[new_entity_id] = entity


def remove_cached_entity(
    cache: dict[str, Any],
    entity_id: str,
    unique_id: str,
    entity: Any,
) -> None:
    """Remove this entity's cache entries without deleting replacements."""
    for key in (entity_id, unique_id):
        if cache.get(key) is entity:
            cache.pop(key)
