"""Tests for counter service-cache lifecycle helpers."""

from custom_components.ha_daily_counter.entity_cache import (
    cache_entity,
    rekey_cached_entity,
    remove_cached_entity,
)


def test_cache_entity_indexes_mutable_and_stable_ids() -> None:
    """Services and reset buttons can resolve the same counter."""
    entity = object()
    cache: dict[str, object] = {}

    cache_entity(cache, "sensor.counter", "entry_counter", entity)

    assert cache == {
        "sensor.counter": entity,
        "entry_counter": entity,
    }


def test_rekey_cached_entity_moves_only_entity_id_key() -> None:
    """An in-place rename keeps the stable unique-ID lookup intact."""
    entity = object()
    cache = {
        "sensor.old_counter": entity,
        "entry_counter": entity,
    }

    rekey_cached_entity(
        cache,
        "sensor.old_counter",
        "sensor.new_counter",
        entity,
    )

    assert cache == {
        "sensor.new_counter": entity,
        "entry_counter": entity,
    }


def test_rekey_does_not_remove_replacement_at_old_id() -> None:
    """A stale callback cannot remove another entity which reused the old ID."""
    entity = object()
    replacement = object()
    cache = {"sensor.old_counter": replacement}

    rekey_cached_entity(
        cache,
        "sensor.old_counter",
        "sensor.new_counter",
        entity,
    )

    assert cache == {
        "sensor.old_counter": replacement,
        "sensor.new_counter": entity,
    }


def test_remove_cached_entity_removes_only_owned_entries() -> None:
    """Unload cleanup preserves cache keys already assigned to replacements."""
    entity = object()
    replacement = object()
    cache = {
        "sensor.counter": replacement,
        "entry_counter": entity,
    }

    remove_cached_entity(cache, "sensor.counter", "entry_counter", entity)

    assert cache == {"sensor.counter": replacement}
