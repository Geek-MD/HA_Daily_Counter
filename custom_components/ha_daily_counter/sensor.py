from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounter  # tu clase sigue en counter.py
from .const import DOMAIN, DEFAULT_NAME, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up HA Daily Counter sensor."""
    name = entry.data.get("name", DEFAULT_NAME)
    trigger_entity = entry.data[ATTR_TRIGGER_ENTITY]
    trigger_state = entry.data[ATTR_TRIGGER_STATE]

    entity = HADailyCounter(name, trigger_entity, trigger_state)
    async_add_entities([entity], True)
