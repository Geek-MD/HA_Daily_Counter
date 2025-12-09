"""Init file for HA Daily Counter integration."""

import logging
from typing import Any, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the integration from configuration.yaml (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Daily Counter from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Compatibilidad con diferentes versiones de HA/stubs:
    # intentamos usar la API plural si existe; para evitar errores de mypy
    # hacemos un cast a Any en la llamada.
    hass.async_create_task(
        cast(Any, hass.config_entries).async_forward_entry_setups(entry, ["sensor"])
    )

    async def handle_reset_counter(call: ServiceCall) -> None:
        """Handle the reset_counter service call."""
        entity_id = call.data.get("entity_id")
        if not entity_id:
            _LOGGER.warning("No entity_id provided in reset_counter service call.")
            return

        entity = hass.data[DOMAIN].get(entity_id)
        if entity:
            entity._attr_native_value = 0  # noqa: SLF001 (private access is fine here)
            entity.async_write_ha_state()
            _LOGGER.info("Manual reset of counter '%s'", entity_id)
        else:
            _LOGGER.warning("Entity '%s' not found for reset.", entity_id)

    async def handle_set_counter(call: ServiceCall) -> None:
        """Handle the set_counter service call."""
        entity_id = call.data.get("entity_id")
        value = call.data.get("value")

        if not entity_id or value is None:
            _LOGGER.warning(
                "Both 'entity_id' and 'value' are required for set_counter service call."
            )
            return

        entity = hass.data[DOMAIN].get(entity_id)
        if entity:
            try:
                int_value = int(value)
            except (ValueError, TypeError):
                _LOGGER.warning("Invalid value '%s' for set_counter.", value)
                return

            entity._attr_native_value = int_value  # noqa: SLF001
            entity.async_write_ha_state()
            _LOGGER.info("Counter '%s' manually set to %s", entity_id, int_value)
        else:
            _LOGGER.warning("Entity '%s' not found for set_counter.", entity_id)

    # ✅ Register services
    hass.services.async_register(DOMAIN, "reset_counter", handle_reset_counter)
    hass.services.async_register(DOMAIN, "set_counter", handle_set_counter)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Llamada a la versión plural de unload si existe; usar cast para evitar chequeos estáticos.
    unloaded = await cast(Any, hass.config_entries).async_forward_entry_unloads(entry, ["sensor"])
    return all(unloaded)
