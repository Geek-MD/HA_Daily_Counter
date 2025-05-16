import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounter

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up counters from config entry."""
    counters = entry.options.get("counters", [])

    entities = []
    for idx, cfg in enumerate(counters):
        entities.append(HADailyCounter(hass, entry, idx, cfg))

    async_add_entities(entities, update_before_add=True)
