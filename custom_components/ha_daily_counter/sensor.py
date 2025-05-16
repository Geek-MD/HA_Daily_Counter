from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounterEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up HA Daily Counter entities from config entry."""
    entities = []

    counters = entry.options.get("counters", [])
    if not counters:
        counters = [entry.data]  # Fallback for legacy configs

    for counter_data in counters:
        entity = HADailyCounterEntity(
            name=counter_data["name"],
            trigger_entity=counter_data["trigger_entity"],
            trigger_state=counter_data["trigger_state"],
            entry_id=entry.entry_id,
        )
        entities.append(entity)

    async_add_entities(entities)
