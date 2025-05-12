import logging
from datetime import datetime, time

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change, async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, DEFAULT_NAME, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

_LOGGER = logging.getLogger(__name__)

class HADailyCounter(SensorEntity, RestoreEntity):
    def __init__(self, name, trigger_entity, trigger_state):
        self._attr_name = name
        self._attr_native_unit_of_measurement = "count"
        self._attr_icon = "mdi:counter"
        self._attr_should_poll = False

        self._state = 0
        self._trigger_entity = trigger_entity
        self._trigger_state = trigger_state

    async def async_added_to_hass(self):
        # Restaurar estado si existe
        last_state = await self.async_get_last_state()
        if last_state and last_state.state != STATE_UNKNOWN:
            try:
                self._state = int(last_state.state)
                _LOGGER.debug("Restored state for %s: %s", self._attr_name, self._state)
            except ValueError:
                _LOGGER.warning("Invalid state value on restore for %s: %s", self._attr_name, last_state.state)
        else:
            _LOGGER.debug("No previous state found for %s, starting at 0", self._attr_name)

        self.async_write_ha_state()

        # Escuchar cambios en el disparador
        async_track_state_change(
            self.hass, self._trigger_entity, self._handle_trigger_change
        )

        # Programar reinicio a medianoche
        async_track_time_change(
            self.hass, self._reset_counter, hour=0, minute=0, second=0
        )

    @callback
    def _handle_trigger_change(self, entity_id, old_state, new_state):
        if new_state is None:
            return

        _LOGGER.debug("Trigger entity %s changed from %s to %s", entity_id, old_state.state if old_state else "None", new_state.state)

        if new_state.state == self._trigger_state:
            self._state += 1
            _LOGGER.debug("Counter %s incremented to %d", self._attr_name, self._state)
            self.async_write_ha_state()

    @callback
    def _reset_counter(self, now=None):
        _LOGGER.debug("Resetting counter %s to 0", self._attr_name)
        self._state = 0
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._state

    @property
    def device_info(self):
        """Return device info to group entities under a device."""
        return {
            "identifiers": {(DOMAIN, f"counter_{self._attr_name.lower().replace(' ', '_')}")},
            "name": f"{self._attr_name} Counter",
            "manufacturer": "HA Daily Counter",
            "model": "Daily Increment Counter"
        }
