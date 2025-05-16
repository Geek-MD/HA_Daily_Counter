import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

class HADailyCounterEntity(SensorEntity, RestoreEntity):
    """Representation of a daily counter sensor."""

    def __init__(self, entry_id, counter_data):
        self._entry_id = entry_id
        self._counter_data = counter_data
        self._attr_name = counter_data.get("name", "Daily Counter")
        self._state = 0

    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._attr_name.lower().replace(' ', '_')}"

    @property
    def native_value(self):
        return self._state

    async def async_added_to_hass(self):
        """Restore state when entity is added to hass."""
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) is not None:
            if state.state != STATE_UNKNOWN:
                self._state = int(state.state)

    @callback
    def increment(self):
        """Increment the counter."""
        self._state += 1
        self.async_write_ha_state()

    async def async_update(self):
        """Update the sensor state."""
        _LOGGER.debug("Updating state for %s: %d", self._attr_name, self._state)
