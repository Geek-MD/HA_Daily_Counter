import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounter

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HA Daily Counter sensor from a config entry."""
    name = entry.data.get("name")
    trigger_entity = entry.data.get("trigger_entity")
    trigger_state = entry.data.get("trigger_state")

    if not name or not trigger_entity or not trigger_state:
        _LOGGER.error("Missing configuration data in entry: %s", entry.data)
        return

    async_add_entities(
        [HADailyCounter(name, trigger_entity, trigger_state)]
    )
