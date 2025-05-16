from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import callback
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.event import async_track_state_change, async_track_time_change
import logging

_LOGGER = logging.getLogger(__name__)

class HADailyCounterEntity(RestoreEntity):
    """Representation of a Daily Counter entity."""

    def __init__(self, name: str, trigger_entity: str, trigger_state: str):
        self._attr_name = name
        self._attr_icon = "mdi:counter"
        self._attr_should_poll = False
        self._attr_native_value = 0

        self._trigger_entity = trigger_entity
        self._trigger_state = trigger_state

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state and last_state.state != STATE_UNKNOWN:
            self._attr_native_value = int(last_state.state)

        async_track_state_change(
            self.hass, self._trigger_entity, self._handle_trigger
        )

        async_track_time_change(
            self.hass, self._reset_counter, hour=0, minute=0, second=0
        )

        self.async_write_ha_state()

    @callback
    def _handle_trigger(self, entity_id, old_state, new_state):
        if new_state and new_state.state == self._trigger_state:
            self._attr_native_value += 1
            self.async_write_ha_state()

    @callback
    def _reset_counter(self, now):
        self._attr_native_value = 0
        self.async_write_ha_state()
