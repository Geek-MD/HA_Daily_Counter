import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import async_get_platform
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Daily Counter from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    async def handle_reset_counter(call: ServiceCall) -> None:
        entity_id = call.data.get("entity_id")
        platform = async_get_platform(hass, "sensor", DOMAIN)

        entity = next(
            (e for e in platform.entities if e.entity_id == entity_id), None
        )

        if entity:
            entity._attr_native_value = 0
            entity.async_write_ha_state()
            _LOGGER.info("Manual reset of counter '%s'", entity_id)
        else:
            _LOGGER.warning("Entity %s not found in platform '%s'", entity_id, DOMAIN)

    hass.services.async_register(
        DOMAIN,
        "reset_counter",
        handle_reset_counter,
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
