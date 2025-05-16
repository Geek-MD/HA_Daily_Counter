from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .counter import HADailyCounterEntity
from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    counters = entry.options.get("counters", [])
    entities = []

    for counter_cfg in counters:
        entity = HADailyCounterEntity(
            name=counter_cfg["name"],
            trigger_entity=counter_cfg[ATTR_TRIGGER_ENTITY],
            trigger_state=counter_cfg[ATTR_TRIGGER_STATE]
        )
        entities.append(entity)

    if entities:
        async_add_entities(entities, True)
