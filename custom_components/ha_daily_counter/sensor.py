import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_track_point_in_utc_time,
    async_track_state_change_event,
)
from homeassistant.helpers.restore_state import RestoreEntity
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

    # Fallback for entries created before v1.5.2: triggers were stored in entry.data
    # instead of entry.options, so no entities were ever registered.
    if not counters and entry.data.get("triggers"):
        counters = [
            {
                "id": entry.entry_id,
                "name": entry.title,
                "triggers": entry.data.get("triggers", []),
                "logic": entry.data.get("logic", "OR"),
            }
        ]
        _LOGGER.warning(
            "Entry '%s' was created before v1.5.2 and has no counters in options. "
            "Loaded from entry.data as fallback. Re-create the entry to migrate.",
            entry.title,
        )

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
        counter_config: dict[str, Any],
    ) -> None:
        self.hass = hass
        self._entry_id = entry_id

        # Build the canonical triggers list from whatever format the config uses.
        # v1.3.0 stored a single trigger_entity / trigger_state pair.
        # v1.3.1+ stores a "triggers" list.
        if "triggers" in counter_config and isinstance(counter_config["triggers"], list):
            self._triggers_list: list[dict[str, str]] = counter_config["triggers"]
        elif "trigger_entity" in counter_config:
            self._triggers_list = [
                {
                    "entity": counter_config.get("trigger_entity", ""),
                    "state": counter_config.get("trigger_state", ""),
                }
            ]
        else:
            _LOGGER.warning("Invalid counter config: %s", counter_config)
            self._triggers_list = []

        self._logic: str = counter_config.get("logic", "OR")

        # Keep a single _trigger_entity / _trigger_state for backward-compat
        # code paths that still reference these attributes.
        first = self._triggers_list[0] if self._triggers_list else {}
        self._trigger_entity: str = first.get("entity", "")
        self._trigger_state: str = first.get("state", "")

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
        """Return device information for Home Assistant UI.

        When the counter monitors a **single** entity and that entity belongs to
        a known device, the counter sensor is attached to that device so it
        appears alongside its related hardware in the HA device page.

        When the counter monitors **multiple** entities it must not be attached
        to any specific device (doing so would create duplicate entries for the
        same config-entry in that device).  In that case an independent virtual
        device is created using the counter's own unique identifier.
        """
        if len(self._triggers_list) == 1 and self._trigger_entity:
            ent_reg = er.async_get(self.hass)
            ent_entry = ent_reg.async_get(self._trigger_entity)
            if ent_entry and ent_entry.device_id:
                dev_reg = dr.async_get(self.hass)
                device = dev_reg.async_get(ent_entry.device_id)
                if device and device.identifiers:
                    return DeviceInfo(identifiers=set(device.identifiers))

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

        # Subscribe to ALL configured trigger entities
        trigger_entities = [t["entity"] for t in self._triggers_list if t.get("entity")]
        if trigger_entities:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    trigger_entities,
                    self._handle_trigger_state_change,
                )
            )
            _LOGGER.debug(
                "Subscribed to %d trigger(s) for '%s': %s",
                len(trigger_entities),
                self._name,
                trigger_entities,
            )
        else:
            _LOGGER.warning("Counter '%s' has no valid trigger entities", self._name)

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
        """Increment counter when trigger conditions are met.

        OR logic (default): increment when ANY configured trigger entity
        transitions to its specified state.

        AND logic: increment only when the entity that just changed satisfies
        its trigger state AND every other trigger entity is already in its
        required state simultaneously.
        """
        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, None):
            return

        changed_entity: str = event.data.get("entity_id", "")

        if self._logic == "AND":
            # All triggers must be satisfied at the same time.
            for trigger in self._triggers_list:
                t_entity = trigger.get("entity", "")
                t_state = trigger.get("state", "")
                if t_entity == changed_entity:
                    if new_state.state != t_state:
                        return  # The changed entity doesn't satisfy its trigger
                else:
                    current = self.hass.states.get(t_entity)
                    if not current or current.state != t_state:
                        return  # Another trigger is not in its required state
            # All conditions met
            self._attr_native_value += 1
            self.async_write_ha_state()
            _LOGGER.debug(
                "Counter '%s' incremented to %d (AND logic)",
                self._name,
                self._attr_native_value,
            )
        else:
            # OR logic: increment when the changed entity matches any trigger.
            for trigger in self._triggers_list:
                if (
                    trigger.get("entity") == changed_entity
                    and new_state.state == trigger.get("state")
                ):
                    self._attr_native_value += 1
                    self.async_write_ha_state()
                    _LOGGER.debug(
                        "Counter '%s' incremented to %d (OR logic)",
                        self._name,
                        self._attr_native_value,
                    )
                    break

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
