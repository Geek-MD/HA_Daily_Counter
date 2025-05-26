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
    """Set up the integration (no YAML)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Daily Counter and register services."""
    # Creamos el caché (sensor.py lo irá llenando)
    hass.data.setdefault(DOMAIN, {})

    # Montamos la plataforma sensor
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    async def handle_reset_counter(call: ServiceCall) -> None:
        """Reset a counter to 0."""
        _LOGGER.debug("reset_counter called with %s", call.data)
        entity_id = call.data.get("entity_id")
        if not entity_id:
            _LOGGER.warning("reset_counter: missing entity_id")
            return

        entity = hass.data[DOMAIN].get(entity_id)
        if not entity:
            _LOGGER.warning("reset_counter: Entity '%s' not in cache", entity_id)
            return

        # 1) Actualizamos el atributo
        entity._attr_native_value = 0
        # 2) Forzamos la escritura en el State Machine
        hass.states.async_set(entity_id, 0)
        # 3) Avisamos al entity
        entity.async_write_ha_state()
        _LOGGER.info("reset_counter: '%s' reset to 0", entity_id)

    async def handle_set_counter(call: ServiceCall) -> None:
        """Set a counter to a specific value."""
        _LOGGER.debug("set_counter called with %s", call.data)
        entity_id = call.data.get("entity_id")
        value = call.data.get("value")
        if not entity_id or value is None:
            _LOGGER.warning("set_counter: missing entity_id or value")
            return

        entity = hass.data[DOMAIN].get(entity_id)
        if not entity:
            _LOGGER.warning("set_counter: Entity '%s' not in cache", entity_id)
            return

        try:
            val = int(value)
        except (ValueError, TypeError):
            _LOGGER.error("set_counter: invalid value %r", value)
            return

        entity._attr_native_value = val
        hass.states.async_set(entity_id, val)
        entity.async_write_ha_state()
        _LOGGER.info("set_counter: '%s' set to %d", entity_id, val)

    # Registramos servicios
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
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_id,
                vol.Required("value"): cv.positive_int,
            }
        ),
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return bool(
        await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    )
