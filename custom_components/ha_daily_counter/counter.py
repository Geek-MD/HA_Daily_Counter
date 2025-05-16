import logging
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change, async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.const import STATE_UNKNOWN

_LOGGER = logging.getLogger(__name__)

class HADailyCounterEntity(RestoreEntity):
    """Representation of a HA Daily Counter entity."""

    def __init__(self, name, trigger_entity, trigger_state):
        self._attr_name = name
        self._trigger_entity = trigger_entity
        self._trigger_state = trigger_state
        self._attr_should_poll = False
        self._state = 0

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state and last_state.state != STATE_UNKNOWN:
            self._state = int(last_state.state)

        async_track_state_change(
            self.hass, self._trigger_entity, self._handle_trigger
        )

        async_track_time_change(
            self.hass, self._reset_counter, hour=0, minute=0, second=0
        )

        self.async_write_ha_state()

    @callback
    def _handle_trigger(self, entity_id, old_state, new_state):
        if new_state is None:
            return

        if new_state.state == self._trigger_state:
            self._state += 1
            self.async_write_ha_state()

    @callback
    def _reset_counter(self, _now):
        self._state = 0
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._state
