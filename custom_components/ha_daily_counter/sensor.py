from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .counter import HADailyCounterEntity
from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up HA Daily Counter sensors from config entry."""
    counters = entry.options.get("counters", [])
    entities = []

    hass.data.setdefault(DOMAIN, {})

    for counter in counters:
        entity = HADailyCounterEntity(hass, entry.entry_id, counter)
        hass.data[DOMAIN][entity.entity_id] = entity
        entities.append(entity)

    if entities:
        async_add_entities(entities)
