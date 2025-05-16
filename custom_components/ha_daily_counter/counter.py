from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.event import async_track_state_change, async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import callback

class HADailyCounter(SensorEntity, RestoreEntity):
    def __init__(self, hass, entry, idx, cfg):
        """Initialize."""
        self.hass = hass
        self._entry = entry
        self._idx = idx

        self._attr_name = cfg.get("name")
        self._trigger_entity = cfg.get("trigger_entity")
        self._trigger_state = cfg.get("trigger_state")

        self._attr_unique_id = f"{entry.entry_id}_{idx}"
        self._state = 0
        self._attr_icon = "mdi:counter"
        self._attr_should_poll = False
        self._attr_native_unit_of_measurement = None

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state and last_state.state != STATE_UNKNOWN:
            self._state = int(last_state.state)

        async_track_state_change(self.hass, self._trigger_entity, self._handle_trigger_change)
        async_track_time_change(self.hass, self._reset_counter, hour=0, minute=0, second=0)

    @callback
    def _handle_trigger_change(self, entity_id, old_state, new_state):
        if new_state and new_state.state == self._trigger_state:
            self._state += 1
            self.async_write_ha_state()

    @callback
    def _reset_counter(self, now=None):
        self._state = 0
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._state
