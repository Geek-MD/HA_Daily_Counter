import logging
import datetime
import asyncio
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import callback
from homeassistant.const import CONF_NAME

_LOGGER = logging.getLogger(__name__)

DOMAIN = "daily_counter"
CONF_SENSORS = "sensors"
CONF_TRIGGER_SENSOR = "trigger_sensor"

async def async_setup(hass, config):
    """Set up the Daily Counter integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass, entry):
    """Set up the integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    sensor = DailyCounterSensor(hass, entry.data)
    hass.data[DOMAIN][entry.entry_id] = sensor
    
    async def reset_counters(now):
        """Reset all counters to zero at midnight."""
        _LOGGER.info("Resetting all daily counters")
        for entity in hass.data[DOMAIN].values():
            if isinstance(entity, DailyCounterSensor):
                entity.reset_counter()
    
    async_track_time_change(hass, reset_counters, hour=0, minute=0, second=0)
    
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True

class DailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Daily Counter."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_TRIGGER_SENSOR): str,
            }),
            errors=errors,
        )

class DailyCounterSensor(RestoreEntity, Entity):
    def __init__(self, hass, config):
        """Initialize the counter sensor."""
        self.hass = hass
        self._name = config[CONF_NAME]
        self._trigger_sensor = config.get(CONF_TRIGGER_SENSOR)
        self._state = 0
        
        if self._trigger_sensor:
            hass.helpers.event.async_track_state_change_event(
                self._trigger_sensor, self._sensor_triggered
            )

    async def _sensor_triggered(self, event):
        """Increase counter when the trigger sensor changes state."""
        self._state += 1
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Restore previous state."""
        last_state = await self.async_get_last_state()
        if last_state and last_state.state.isdigit():
            self._state = int(last_state.state)
        self.async_write_ha_state()

    def reset_counter(self):
        """Reset the counter to zero."""
        self._state = 0
        self.async_write_ha_state()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"daily_counter_{self._name}"
