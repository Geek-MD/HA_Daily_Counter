from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up HA Daily Counter sensors from config entry."""
    counters = entry.options.get("counters", [])
    entities = [HADailyCounterEntity(hass, entry.entry_id, counter) for counter in counters]
    async_add_entities(entities)
