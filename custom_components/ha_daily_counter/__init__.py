import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from configuration.yaml (not used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Daily Counter from a config entry."""
    hass.data.setdefault(DOMAIN, {})  # Ensure hass.data[DOMAIN] exists

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    async def handle_reset_counter(call: ServiceCall) -> None:
        """Handle the reset_counter service call."""
        entity_id = call.data.get("entity_id")

        if not entity_id:
            _LOGGER.warning("No entity_id provided in service call.")
            return

        entity = hass.data.get(DOMAIN, {}).get(entity_id)

        if entity:
            entity._attr_native_value = 0
            entity.async_write_ha_state()
            _LOGGER.info("Manual reset of counter '%s'", entity_id)
        else:
            _LOGGER.warning("Entity '%s' not found for reset.", entity_id)

    hass.services.async_register(
        DOMAIN,
        "reset_counter",
        handle_reset_counter,
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    result: bool = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return result
