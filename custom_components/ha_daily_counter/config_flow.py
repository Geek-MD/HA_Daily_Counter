from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
)
from homeassistant.data_entry_flow import FlowResult

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DOMAIN
from .options_flow import HADailyCounterOptionsFlow


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter."""

    VERSION = 1

    def __init__(self) -> None:
        self._trigger_entity: str | None = None
        self._name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Ask for counter name and entity to monitor."""
        if user_input is not None:
            self._name = user_input[CONF_NAME]
            self._trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
            return await self.async_step_trigger_state()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                        EntitySelectorConfig(
                            domain=[
                                "sensor",
                                "binary_sensor",
                                "input_boolean",
                                "input_number",
                                "input_select",
                            ]
                        )
                    ),
                }
            ),
            description_placeholders={
                "name": "Name",
                "trigger_entity": "Entity to monitor",
            },
        )

    async def async_step_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Select which state of the entity will increment the counter."""
        if self._trigger_entity is None:
            return await self.async_step_user(user_input)

        hass: HomeAssistant = self.hass
        entity_state = hass.states.get(self._trigger_entity)

        options: list[SelectOptionDict] = []
        if entity_state is not None:
            possible_states = set()

            # Estado actual
            if entity_state.state not in ("unknown", "unavailable"):
                possible_states.add(entity_state.state)

            # Opciones de input_select
            if "options" in entity_state.attributes:
                possible_states.update(entity_state.attributes["options"])

            # Estados típicos de binary_sensor
            if self._trigger_entity.startswith("binary_sensor."):
                possible_states.update(["on", "off"])

            # Estados comunes de puertas y ventanas
            if entity_state.attributes.get("device_class") in ["door", "window"]:
                possible_states.update(["open", "closed"])

            options = [
                SelectOptionDict(value=state, label=state)
                for state in sorted(possible_states)
            ]

        if user_input is not None and ATTR_TRIGGER_STATE in user_input:
            trigger_state = user_input[ATTR_TRIGGER_STATE]

            counter_id = self._trigger_entity.replace(".", "_")
            counter = {
                "id": counter_id,
                "name": self._name or "Daily Counter",
                "trigger_entity": self._trigger_entity,
                "trigger_state": trigger_state,
            }

            return self.async_create_entry(
                title=self._name or "Daily Counter",
                data={},
                options={"counters": [counter]},
            )

        return self.async_show_form(
            step_id="trigger_state",
            data_schema=vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_STATE): SelectSelector(
                        SelectSelectorConfig(options=options, mode="dropdown")
                    )
                }
            ),
            description_placeholders={
                "trigger_state": "State to monitor",
            },
        )

    @staticmethod
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return HADailyCounterOptionsFlow(entry)
