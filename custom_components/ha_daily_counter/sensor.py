from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounterEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up HA Daily Counter sensors from config entry."""
    entities = []
    counters = entry.options.get("counters", [])

    for counter in counters:
        entities.append(HADailyCounterEntity(entry.entry_id, counter))

    if entities:
        async_add_entities(entities)
