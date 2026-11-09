"""Button entities for manually resetting HA Daily Counter sensors."""

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device import async_entity_id_to_device
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_entity_registry_updated_event

from .const import CONF_DIAGNOSTIC, DEFAULT_DIAGNOSTIC, DOMAIN
from .device_link import source_registry_update_requires_sync, sync_device_link
from .usage_time import usage_time_cache_key


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one manual-reset button per counter."""
    counters = entry.options.get("counters", [])
    if not counters and entry.data.get("triggers"):
        counters = [
            {
                "id": entry.entry_id,
                "name": entry.title,
                "triggers": entry.data.get("triggers", []),
            }
        ]

    async_add_entities(
        HADailyCounterResetButton(hass, entry.entry_id, counter)
        for counter in counters
    )


class HADailyCounterResetButton(ButtonEntity):
    """Button that resets its corresponding counter sensor."""

    _attr_icon = "mdi:restart"
    _attr_has_entity_name = True
    _attr_translation_key = "reset"

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        counter_config: dict[str, Any],
    ) -> None:
        self.hass = hass
        self._counter_unique_id = f"{entry_id}_{counter_config.get('id', 'unknown')}"
        self._attr_unique_id = f"{self._counter_unique_id}_reset"
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC
            if counter_config.get(CONF_DIAGNOSTIC, DEFAULT_DIAGNOSTIC)
            else None
        )
        self._counter_name: str = counter_config.get("name", "Unnamed Counter")
        triggers = counter_config.get("triggers", [])
        if not triggers and counter_config.get("trigger_entity"):
            triggers = [{"entity": counter_config["trigger_entity"]}]
        self._triggers: list[dict[str, Any]] = triggers
        self._source_entity: str | None = (
            self._triggers[0].get("entity") if len(self._triggers) == 1 else None
        )
        self.device_entry = (
            async_entity_id_to_device(hass, self._source_entity)
            if self._source_entity
            else None
        )

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return fallback device information when no source device is available."""
        if self.device_entry is not None:
            return None

        return DeviceInfo(
            identifiers={(DOMAIN, self._counter_unique_id)},
            name=self._counter_name,
            manufacturer="Geek-MD",
            model="HA Daily Counter",
        )

    async def async_added_to_hass(self) -> None:
        """Follow the source entity when its device is recreated."""
        await super().async_added_to_hass()

        if self._source_entity:
            self._sync_device_link()
            self.async_on_remove(
                async_track_entity_registry_updated_event(
                    self.hass,
                    self._source_entity,
                    self._handle_source_registry_update,
                )
            )

    @callback
    def async_entity_id_changed(self, old_entity_id: str) -> None:
        """Opt in to in-place entity ID changes."""
        super().async_entity_id_changed(old_entity_id)

    @callback
    def _handle_source_registry_update(self, event: Any) -> None:
        """Relink when the source entity is created or changes device."""
        if source_registry_update_requires_sync(event.data):
            self._sync_device_link()

    @callback
    def _sync_device_link(self) -> None:
        """Keep the reset button on its source entity's device."""
        if self._source_entity is None:
            return
        ent_reg = er.async_get(self.hass)
        sync_device_link(ent_reg, self._source_entity, self.entity_id)

    async def async_press(self) -> None:
        """Reset the corresponding counter to zero."""
        counter = self.hass.data.get(DOMAIN, {}).get(self._counter_unique_id)
        if counter is not None:
            counter.async_reset_counter()
            return
        usage_sensor = self.hass.data.get(DOMAIN, {}).get(
            usage_time_cache_key(self._counter_unique_id)
        )
        if usage_sensor is not None:
            usage_sensor.async_reset_usage_time()
