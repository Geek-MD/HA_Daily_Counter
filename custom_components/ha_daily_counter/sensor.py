import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_NAME

from .counter import HADailyCounterEntity
from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up HA Daily Counter sensors from config entry."""
    counters = entry.options.get("counters", [])

    entities = []
    for counter in counters:
        name = counter.get(CONF_NAME)
        trigger_entity = counter.get(ATTR_TRIGGER_ENTITY)
        trigger_state = counter.get(ATTR_TRIGGER_STATE)

        if name and trigger_entity and trigger_state:
            _LOGGER.debug("Adding counter: %s", name)
            entities.append(HADailyCounterEntity(name, trigger_entity, trigger_state))

    async_add_entities(entities)
