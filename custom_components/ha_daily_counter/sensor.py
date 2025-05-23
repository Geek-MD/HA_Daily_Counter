import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
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
        hass.data.setdefault(DOMAIN, {})[entity.entity_id] = entity
        entities.append(entity)

    if entities:
        async_add_entities(entities)


class HADailyCounterEntity(SensorEntity, RestoreEntity):
    """Sensor that counts when *cualquiera* de varios triggers llegue a un estado."""

    _attr_should_poll = False
    _attr_icon = "mdi:counter"
    _attr_state_class = "total_increasing"
    _attr_native_unit_of_measurement = None

    def __init__(self, hass: HomeAssistant, entry_id: str, cfg: Dict[str, Any]) -> None:
        self.hass = hass
        self._entry_id = entry_id
        self._unique_id = f"{entry_id}_{cfg['id']}"
        self._name = cfg["name"]
        self._triggers: list[tuple[str, str]] = [
            (t["entity"], t["state"]) for t in cfg.get("triggers", [])
        ]
        self._attr_native_value = 0
        self._cancel_reset = None

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Geek-MD",
            "model": "HA Daily Counter",
        }

    async def async_added_to_hass(self) -> None:
        """Restaurar estado, suscribir a cada trigger y programar reset diario."""
        if (last := await self.async_get_last_state()) and last.state.isdigit():
            self._attr_native_value = int(last.state)

        for entity_id, _state in self._triggers:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [entity_id],
                    self._handle_state_change,
                )
            )

        # Primer reset
        next_reset = self._next_reset_time()
        self._cancel_reset = async_track_point_in_utc_time(
            self.hass, self._reset, next_reset
        )
        _LOGGER.debug("Scheduled reset for %s at %s", self._name, next_reset)

    @callback
    def _handle_state_change(self, event: Any) -> None:
        """Incrementa si *cualquiera* de los triggers alcanzó su estado objetivo."""
        new = event.data.get("new_state")
        if not new or new.state in (STATE_UNKNOWN, None):
            return

        for entity_id, state in self._triggers:
            if new.entity_id == entity_id and new.state == state:
                self._attr_native_value += 1
                self.async_write_ha_state()
                _LOGGER.debug("Counter %s incremented to %s", self._name, self._attr_native_value)
                break

    @callback
    def _reset(self, now: datetime) -> None:
        """Reiniciar a 0 y reprogramar reset al siguiente 00:00 local."""
        self._attr_native_value = 0
        self.async_write_ha_state()
        _LOGGER.info("Counter %s reset to 0", self._name)

        next_reset = self._next_reset_time()
        self._cancel_reset = async_track_point_in_utc_time(
            self.hass, self._reset, next_reset
        )
        _LOGGER.debug("Next reset for %s scheduled at %s", self._name, next_reset)

    def _next_reset_time(self) -> datetime:
        """Próximo 00:00 local."""
        now = dt_util.now()
        reset = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if reset <= now:
            reset += timedelta(days=1)
        return reset
