import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback, State
from homeassistant.helpers.event import (
    async_track_state_change,
    async_track_point_in_utc_time,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


class HADailyCounterEntity(SensorEntity, RestoreEntity):
    """Sensor that increments when another entity hits a specific state."""

    _attr_state_class = "total"
    _attr_device_class = None
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:counter"

    def __init__(self, hass: HomeAssistant, entry_id: str, counter_config: dict) -> None:
        self.hass = hass
        self._entry_id = entry_id
        self._unique_id: str = f"{entry_id}_{counter_config['id']}"
        self._name: str = counter_config["name"]
        self._trigger_entity: str = counter_config["trigger_entity"]
        self._trigger_state: str = counter_config["trigger_state"]
        self._device_id: str = counter_config["id"]
        self._device_name: str = counter_config["name"]
        self._attr_native_value: int = 0

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(self._entry_id, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Geek-MD",
            "model": "HA Daily Counter",
        }

    @property
    def native_value(self) -> int:
        return self._attr_native_value

    async def async_added_to_hass(self) -> None:
        """Restore state, set up trigger listener and reset timer."""
        if (last_state := await self.async_get_last_state()) and last_state.state.isdigit():
            self._attr_native_value = int(last_state.state)
            _LOGGER.debug("Restored state for %s: %s", self._name, self._attr_native_value)

        self.async_on_remove(
            async_track_state_change(
                self.hass,
                self._trigger_entity,
                self._handle_trigger_state_change,
            )
        )

        next_reset = self._get_next_reset_time()
        self.async_on_remove(
            async_track_point_in_utc_time(self.hass, self._reset_counter, next_reset)
        )

    @callback
    def _handle_trigger_state_change(
        self,
        entity_id: str,
        old_state: State | None,
        new_state: State | None,
    ) -> None:
        """Handle a trigger state change."""
        if new_state and new_state.state == self._trigger_state:
            self._attr_native_value += 1
            self.async_write_ha_state()
            _LOGGER.debug("Counter '%s' incremented to %s", self._name, self._attr_native_value)

    @callback
    def _reset_counter(self, now: datetime) -> None:
        """Reset the counter to 0 and reschedule the next reset."""
        self._attr_native_value = 0
        self.async_write_ha_state()
        _LOGGER.debug("Counter '%s' reset to 0 at scheduled hour", self._name)

        # 🛠️ FIX: Re-schedule the reset properly using `async_on_remove`
        next_reset = self._get_next_reset_time()
        self.async_on_remove(
            async_track_point_in_utc_time(self.hass, self._reset_counter, next_reset)
        )
        _LOGGER.debug("Next reset for '%s' scheduled at %s", self._name, next_reset)

    def _get_next_reset_time(self) -> datetime:
        """Calculate the next reset time at 00:00 UTC."""
        now = dt_util.utcnow()
        next_reset: datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if next_reset <= now:
            next_reset += timedelta(days=1)
        return next_reset
