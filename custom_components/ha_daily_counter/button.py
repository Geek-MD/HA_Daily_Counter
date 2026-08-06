"""Button entities for manually resetting HA Daily Counter sensors."""

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


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
        self._counter_name: str = counter_config.get("name", "Unnamed Counter")
        triggers = counter_config.get("triggers", [])
        if not triggers and counter_config.get("trigger_entity"):
            triggers = [{"entity": counter_config["trigger_entity"]}]
        self._triggers: list[dict[str, Any]] = triggers

    @property
    def device_info(self) -> DeviceInfo:
        """Attach the button to the same device as its counter sensor."""
        if len(self._triggers) == 1 and (
            trigger_entity := self._triggers[0].get("entity")
        ):
            entity_entry = er.async_get(self.hass).async_get(trigger_entity)
            if entity_entry and entity_entry.device_id:
                device = dr.async_get(self.hass).async_get(entity_entry.device_id)
                if device and device.identifiers:
                    return DeviceInfo(identifiers=set(device.identifiers))

        return DeviceInfo(
            identifiers={(DOMAIN, self._counter_unique_id)},
            name=self._counter_name,
            manufacturer="Geek-MD",
            model="HA Daily Counter",
        )

    async def async_press(self) -> None:
        """Reset the corresponding counter to zero."""
        counter = self.hass.data.get(DOMAIN, {}).get(self._counter_unique_id)
        if counter is not None:
            counter.async_reset_counter()
