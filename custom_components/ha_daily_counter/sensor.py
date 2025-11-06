import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_point_in_utc_time,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HA Daily Counter sensors from config entry."""
    counters = entry.options.get("counters", [])
    entities: list[HADailyCounterEntity] = []

    for cfg in counters:
        entity = HADailyCounterEntity(hass, entry.entry_id, cfg)
        entities.append(entity)

    if entities:
        async_add_entities(entities)


class HADailyCounterEntity(SensorEntity, RestoreEntity):
    """Sensor that counts trigger events and resets daily at local midnight."""

    _attr_icon = "mdi:counter"
    _attr_state_class = "total_increasing"
    _attr_native_unit_of_measurement = None
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        counter_config: Dict[str, Any],
    ) -> None:
        self.hass = hass
        self._entry_id = entry_id

        # === Retrocompatibilidad ===
        # v1.3.0 → usa trigger_entity / trigger_state
        # v1.3.1+ → usa triggers (lista)
        if "trigger_entity" in counter_config:
            self._trigger_entity: str = counter_config["trigger_entity"]
            self._trigger_state: str = counter_config["trigger_state"]
        elif "triggers" in counter_config and isinstance(counter_config["triggers"], list):
            first = counter_config["triggers"][0] if counter_config["triggers"] else {}
            self._trigger_entity = first.get("entity", "")
            self._trigger_state = first.get("state", "")
        else:
            _LOGGER.warning("Invalid counter config: %s", counter_config)
            self._trigger_entity = ""
            self._trigger_state = ""

        self._unique_id = f"{entry_id}_{counter_config.get('id', 'unknown')}"
        self._name: str = counter_config.get("name", "Unnamed Counter")
        self._attr_native_value: int = 0
        self._cancel_reset: Any = None

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def native_value(self) -> int:
        return self._attr_native_value

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information for Home Assistant UI."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            name=self._name,
            manufacturer="Geek-MD",
            model="HA Daily Counter",
        )

    async def async_added_to_hass(self) -> None:
        """Restore state, subscribe to triggers, schedule reset, and cache entity."""
        await super().async_added_to_hass()

        # Restore last state
        if (last := await self.async_get_last_state()) and last.state.isdigit():
            self._attr_native_value = int(last.state)
            _LOGGER.debug("Restored state for '%s': %d", self._name, self._attr_native_value)

        # Subscribe to state change events
        if self._trigger_entity:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._trigger_entity],
                    self._handle_trigger_state_change,
                )
            )
            _LOGGER.debug("Subscribed to trigger '%s' for '%s'", self._trigger_entity, self._name)
        else:
            _LOGGER.warning("Counter '%s' has no valid trigger entity", self._name)

        # Schedule daily reset
        next_reset = self._get_next_reset_time()
        self._cancel_reset = async_track_point_in_utc_time(
            self.hass,
            self._reset_counter,
            next_reset,
        )
        _LOGGER.debug("Scheduled reset for '%s' at %s", self._name, next_reset)

        # Cache this entity for service access
        self.hass.data.setdefault(DOMAIN, {})[self.entity_id] = self
        _LOGGER.debug("Cached entity '%s' for services", self.entity_id)

    @callback
    def _handle_trigger_state_change(self, event: Any) -> None:
        """Increment counter when trigger entity reaches specified state."""
        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, None):
            return
        if new_state.state == self._trigger_state:
            self._attr_native_value += 1
            self.async_write_ha_state()
            _LOGGER.debug(
                "Counter '%s' incremented to %d", self._name, self._attr_native_value
            )

    @callback
    def _reset_counter(self, now: datetime) -> None:
        """Reset the counter to 0 and reschedule next reset."""
        self._attr_native_value = 0
        self.async_write_ha_state()
        _LOGGER.info("Counter '%s' reset to 0", self._name)

        next_reset = self._get_next_reset_time()
        self._cancel_reset = async_track_point_in_utc_time(
            self.hass,
            self._reset_counter,
            next_reset,
        )
        _LOGGER.debug("Next reset for '%s' scheduled at %s", self._name, next_reset)

    def _get_next_reset_time(self) -> datetime:
        """Return the next local midnight for reset."""
        now: datetime = dt_util.now()
        reset: datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if reset <= now:
            reset += timedelta(days=1)
        return reset
