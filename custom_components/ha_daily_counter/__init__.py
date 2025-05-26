import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Daily Counter from a config entry, and register services."""
    hass.data.setdefault(DOMAIN, {})

    # Forward setup to sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    async def handle_reset_counter(call: ServiceCall) -> None:
        _LOGGER.debug("Called reset_counter service with data: %s", call.data)
        entity_id = call.data.get("entity_id")
        _LOGGER.debug("hass.data[%r] keys: %s", DOMAIN, list(hass.data[DOMAIN].keys()))

        if not entity_id:
            _LOGGER.warning("reset_counter: no 'entity_id' provided")
            return

        entity = hass.data[DOMAIN].get(entity_id)
        if not entity:
            _LOGGER.warning("reset_counter: Entity '%s' not found in hass.data[%r]", entity_id, DOMAIN)
            return

        # 1) Internal value
        entity._attr_native_value = 0
        # 2) State machine
        hass.states.async_set(entity_id, 0)
        # 3) Notify entity
        entity.async_write_ha_state()
        _LOGGER.info("reset_counter: Counter '%s' reset to 0", entity_id)

    async def handle_set_counter(call: ServiceCall) -> None:
        _LOGGER.debug("Called set_counter service with data: %s", call.data)
        entity_id = call.data.get("entity_id")
        value = call.data.get("value")
        _LOGGER.debug("hass.data[%r] keys: %s", DOMAIN, list(hass.data[DOMAIN].keys()))

        if not entity_id or value is None:
            _LOGGER.warning("set_counter: both 'entity_id' and 'value' are required")
            return

        entity = hass.data[DOMAIN].get(entity_id)
        if not entity:
            _LOGGER.warning("set_counter: Entity '%s' not found in hass.data[%r]", entity_id, DOMAIN)
            return

        try:
            val = int(value)
        except (ValueError, TypeError):
            _LOGGER.error("set_counter: invalid 'value' %r; must be integer", value)
            return

        entity._attr_native_value = val
        hass.states.async_set(entity_id, val)
        entity.async_write_ha_state()
        _LOGGER.info("set_counter: Counter '%s' set to %d", entity_id, val)

    # Register services
    hass.services.async_register(
        DOMAIN,
        "reset_counter",
        handle_reset_counter,
        schema=vol.Schema({vol.Required("entity_id"): cv.entity_id}),
    )
    hass.services.async_register(
        DOMAIN,
        "set_counter",
        handle_set_counter,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("value"): cv.positive_int,
        }),
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return bool(await hass.config_entries.async_forward_entry_unload(entry, "sensor"))
