import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.event import async_track_state_change, async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import callback

from .const import DOMAIN, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

_LOGGER = logging.getLogger(__name__)

class HADailyCounter(SensorEntity, RestoreEntity):
    def __init__(self, hass, entry):
        """Initialize the daily counter sensor."""
        self.hass = hass
        self._entry = entry

        self._attr_name = entry.data.get("name")
        self._trigger_entity = entry.data.get(ATTR_TRIGGER_ENTITY)
        self._trigger_state = entry.data.get(ATTR_TRIGGER_STATE)

        # Unique ID per entry
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}"

        self._state = 0
        self._attr_icon = "mdi:counter"
        self._attr_should_poll = False
        self._attr_native_unit_of_measurement = None  # No units

    async def async_added_to_hass(self):
        """Handle entity addition."""
        _LOGGER.debug("Adding sensor entity: %s", self._attr_unique_id)

        last_state = await self.async_get_last_state()
        if last_state and last_state.state != STATE_UNKNOWN:
            self._state = int(last_state.state)
            _LOGGER.debug("Restored state: %s", self._state)

        # Listen to trigger entity changes
        async_track_state_change(
            self.hass, self._trigger_entity, self._handle_trigger_change
        )

        # Reset counter at midnight
        async_track_time_change(
            self.hass, self._reset_counter, hour=0, minute=0, second=0
        )

    @callback
    def _handle_trigger_change(self, entity_id, old_state, new_state):
        if new_state is None:
            return

        if new_state.state == self._trigger_state:
            self._state += 1
            _LOGGER.debug("Incremented counter %s to %d", self._attr_unique_id, self._state)
            self.async_write_ha_state()

    @callback
    def _reset_counter(self, now=None):
        _LOGGER.debug("Resetting counter %s to 0", self._attr_unique_id)
        self._state = 0
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._state
