import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from configuration.yaml (not used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Daily Counter from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Forward sensor setup
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Service: reset counter
    async def handle_reset_counter(call: ServiceCall) -> None:
        entity_id = call.data.get("entity_id")
        if not entity_id:
            _LOGGER.warning("No entity_id provided for reset_counter service.")
            return
        entity = hass.data[DOMAIN].get(entity_id)
        if entity:
            entity._attr_native_value = 0
            entity.async_write_ha_state()
            _LOGGER.info("Counter '%s' manually reset to 0", entity_id)
        else:
            _LOGGER.warning("Entity '%s' not found for reset.", entity_id)

    # Service: set counter value
    async def handle_set_counter(call: ServiceCall) -> None:
        entity_id = call.data.get("entity_id")
        value = call.data.get("value")
        if entity_id is None or value is None:
            _LOGGER.warning("entity_id and value are required for set_counter service.")
            return
        entity = hass.data[DOMAIN].get(entity_id)
        if entity:
            try:
                val = int(value)
            except (ValueError, TypeError):
                _LOGGER.error("Invalid value '%s' for set_counter; must be integer.", value)
                return
            entity._attr_native_value = val
            entity.async_write_ha_state()
            _LOGGER.info("Counter '%s' manually set to %s", entity_id, val)
        else:
            _LOGGER.warning("Entity '%s' not found for set_counter.", entity_id)

    # Register both services
    hass.services.async_register(
        DOMAIN,
        'reset_counter',
        handle_reset_counter,
        schema=vol.Schema({
            vol.Required('entity_id'): cv.entity_id
        })
    )

    hass.services.async_register(
        DOMAIN,
        'set_counter',
        handle_set_counter,
        schema=vol.Schema({
            vol.Required('entity_id'): cv.entity_id,
            vol.Required('value'): cv.positive_int
        })
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    result: bool = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return result
