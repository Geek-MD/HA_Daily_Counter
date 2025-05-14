import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounter
from .const import DEFAULT_NAME, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("HADailyCounter: sensor.py async_setup_entry called for entry: %s", entry.entry_id)
    
    name = entry.data.get("name", DEFAULT_NAME)
    trigger_entity = entry.data.get(ATTR_TRIGGER_ENTITY)
    trigger_state = entry.data.get(ATTR_TRIGGER_STATE)

    if not trigger_entity or not trigger_state:
        _LOGGER.error("HADailyCounter: Missing trigger_entity or trigger_state in config entry: %s", entry.data)
        return

    _LOGGER.info(
        "HADailyCounter: Creating counter entity - Name: %s | Trigger Entity: %s | Trigger State: %s",
        name, trigger_entity, trigger_state
    )

    entity = HADailyCounter(name, trigger_entity, trigger_state, entry.entry_id)
    async_add_entities([entity], True)

    _LOGGER.info("HADailyCounter: Entity %s successfully added", name)
