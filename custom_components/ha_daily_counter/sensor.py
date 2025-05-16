import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounter

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up HA Daily Counter sensor from a config entry."""
    _LOGGER.debug("Setting up sensor for entry: %s", entry.entry_id)

    entity = HADailyCounter(hass, entry)
    async_add_entities([entity], update_before_add=True)
