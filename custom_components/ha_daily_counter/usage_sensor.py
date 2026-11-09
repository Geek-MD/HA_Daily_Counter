"""Optional sensor that accumulates time spent in a configured entity state."""

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device import async_entity_id_to_device
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import (
    async_track_entity_registry_updated_event,
    async_track_point_in_utc_time,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DIAGNOSTIC,
    CONF_RESET_CYCLE,
    CONF_USAGE_STATE,
    DEFAULT_DIAGNOSTIC,
    DEFAULT_RESET_CYCLE,
    DOMAIN,
)
from .device_link import source_registry_update_requires_sync, sync_device_link
from .reset import current_period_start, next_reset_time
from .usage_time import (
    apply_usage_transition,
    current_duration_seconds,
    reset_usage_interval,
    usage_time_cache_key,
)

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(minutes=1)


class HAUsageTimeEntity(SensorEntity, RestoreEntity):
    """Sensor accumulating hours spent in one state of the primary entity."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_should_poll = False
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 3
    _attr_translation_key = "usage_time"

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        counter_config: dict[str, Any],
    ) -> None:
        """Initialize a usage-time sensor from its counter configuration."""
        self.hass = hass
        triggers = counter_config.get("triggers", [])
        if not triggers and counter_config.get("trigger_entity"):
            triggers = [{"entity": counter_config["trigger_entity"]}]
        first = triggers[0] if triggers else {}
        self._source_entity: str = first.get("entity", "")
        self._usage_state: str = counter_config.get(CONF_USAGE_STATE, "")
        self._reset_cycle: str = counter_config.get(
            CONF_RESET_CYCLE, DEFAULT_RESET_CYCLE
        )
        counter_id = counter_config.get("id", "unknown")
        self._counter_unique_id = f"{entry_id}_{counter_id}"
        self._attr_unique_id = f"{self._counter_unique_id}_usage_time"
        self._counter_name: str = counter_config.get("name", "Unnamed Counter")
        self._attr_translation_placeholders = {"counter_name": self._counter_name}
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC
            if counter_config.get(CONF_DIAGNOSTIC, DEFAULT_DIAGNOSTIC)
            else None
        )
        self._accumulated_seconds = 0.0
        self._active_since: datetime | None = None
        self._cancel_reset: Any = None
        self.device_entry = (
            async_entity_id_to_device(hass, self._source_entity)
            if self._source_entity
            else None
        )

    @property
    def native_value(self) -> float:
        """Return accumulated usage time in hours."""
        seconds = current_duration_seconds(
            self._accumulated_seconds,
            self._active_since,
            dt_util.now(),
        )
        return round(seconds / 3600, 4)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose the source identity used to validate restored duration."""
        return {
            "monitored_entity": self._source_entity,
            "monitored_state": self._usage_state,
        }

    @property
    def device_info(self) -> DeviceInfo | None:
        """Use the source device or the counter's shared virtual device."""
        if self.device_entry is not None:
            return None
        return DeviceInfo(
            identifiers={(DOMAIN, self._counter_unique_id)},
            name=self._counter_name,
            manufacturer="Geek-MD",
            model="HA Daily Counter",
        )

    async def async_added_to_hass(self) -> None:
        """Restore duration, subscribe to state changes, and schedule resets."""
        await super().async_added_to_hass()
        now = dt_util.now()
        if last := await self.async_get_last_state():
            try:
                restored_hours = float(last.state)
            except (TypeError, ValueError):
                restored_hours = 0.0
            period_start = current_period_start(now, self._reset_cycle)
            same_measurement = (
                last.attributes.get("monitored_entity") == self._source_entity
                and last.attributes.get("monitored_state") == self._usage_state
            )
            if same_measurement and (
                period_start is None or last.last_updated >= period_start
            ):
                self._accumulated_seconds = max(0.0, restored_hours * 3600)

        current = self.hass.states.get(self._source_entity)
        if current is not None and current.state == self._usage_state:
            self._active_since = now

        if self._source_entity:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._source_entity],
                    self._handle_source_state_change,
                )
            )
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._publish_active_duration,
                UPDATE_INTERVAL,
            )
        )

        self.async_on_remove(self._cancel_scheduled_reset)
        if (reset_at := next_reset_time(now, self._reset_cycle)) is not None:
            self._schedule_reset(reset_at)

        if self._source_entity:
            self._sync_device_link()
            self.async_on_remove(
                async_track_entity_registry_updated_event(
                    self.hass,
                    self._source_entity,
                    self._handle_source_registry_update,
                )
            )

        cache = self.hass.data.setdefault(DOMAIN, {})
        cache[usage_time_cache_key(self._counter_unique_id)] = self
        self.async_on_remove(self._remove_from_cache)
        self.async_write_ha_state()

    @callback
    def async_entity_id_changed(self, old_entity_id: str) -> None:
        """Opt in to in-place entity ID changes."""
        super().async_entity_id_changed(old_entity_id)

    @callback
    def _handle_source_state_change(self, event: Any) -> None:
        """Start or finish a usage interval on a real state transition."""
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")
        self._accumulated_seconds, self._active_since = apply_usage_transition(
            self._accumulated_seconds,
            self._active_since,
            old_state.state if old_state else None,
            new_state.state if new_state else None,
            self._usage_state,
            dt_util.now(),
        )
        self.async_write_ha_state()

    @callback
    def _publish_active_duration(self, _now: datetime) -> None:
        """Publish elapsed time while the monitored state remains active."""
        if self._active_since is not None:
            self.async_write_ha_state()

    def _schedule_reset(self, reset_at: datetime) -> None:
        """Schedule the next reset boundary."""
        self._cancel_reset = async_track_point_in_utc_time(
            self.hass,
            self._reset_usage_time,
            reset_at,
        )

    @callback
    def _cancel_scheduled_reset(self) -> None:
        """Cancel the pending reset when unloaded."""
        if self._cancel_reset is not None:
            self._cancel_reset()
            self._cancel_reset = None

    @callback
    def _reset_usage_time(self, _now: datetime) -> None:
        """Reset at a scheduled boundary and arrange the next one."""
        local_now = dt_util.now()
        self.async_reset_usage_time(local_now)
        if (reset_at := next_reset_time(local_now, self._reset_cycle)) is not None:
            self._schedule_reset(reset_at)

    @callback
    def async_reset_usage_time(self, now: datetime | None = None) -> None:
        """Reset usage duration while preserving an active source interval."""
        reset_at = now or dt_util.now()
        current = self.hass.states.get(self._source_entity)
        self._accumulated_seconds, self._active_since = reset_usage_interval(
            current is not None and current.state == self._usage_state,
            reset_at,
        )
        self.async_write_ha_state()

    @callback
    def _handle_source_registry_update(self, event: Any) -> None:
        """Relink when the source entity is created or changes device."""
        if source_registry_update_requires_sync(event.data):
            self._sync_device_link()

    @callback
    def _sync_device_link(self) -> None:
        """Keep the usage sensor on its primary source device."""
        if not self._source_entity:
            return
        sync_device_link(
            er.async_get(self.hass),
            self._source_entity,
            self.entity_id,
        )

    @callback
    def _remove_from_cache(self) -> None:
        """Remove this usage sensor's private cache entry."""
        cache = self.hass.data.get(DOMAIN)
        key = usage_time_cache_key(self._counter_unique_id)
        if cache is not None and cache.get(key) is self:
            cache.pop(key)
