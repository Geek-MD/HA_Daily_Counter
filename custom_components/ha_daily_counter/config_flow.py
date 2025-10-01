from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
    BooleanSelector,
)

from homeassistant.data_entry_flow import FlowResult

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DOMAIN
from .options_flow import HADailyCounterOptionsFlow


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter with multiple triggers."""

    VERSION = 1

    def __init__(self) -> None:
        self._name: str | None = None
        self._trigger_state: str | None = None
        self._trigger_entities: list[str] = []
        self._logic_operator: str | None = None
        self._domain: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step: basic info, first trigger, and state."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._name = user_input[CONF_NAME]
            first_entity = user_input[ATTR_TRIGGER_ENTITY]
            self._trigger_state = user_input[ATTR_TRIGGER_STATE]
            self._trigger_entities.append(first_entity)
            self._domain = first_entity.split(".")[0]

            if user_input.get("add_another"):
                return await self.async_step_add_trigger()

            return self._create_entry()

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
                    vol.Required(ATTR_TRIGGER_STATE): str,
                    vol.Optional("add_another", default=False): BooleanSelector(),
                }
            ),
            errors=errors,
        )

    async def async_step_add_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Second step: add more triggers and define logic."""
        if user_input is not None:
            next_entity = user_input[ATTR_TRIGGER_ENTITY]
            self._trigger_entities.append(next_entity)

            if self._logic_operator is None:
                self._logic_operator = user_input["logic_operator"]

            if user_input.get("add_another"):
                return await self.async_step_add_trigger()

            return self._create_entry()

        return self.async_show_form(
            step_id="add_trigger",
            data_schema=vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                        EntitySelectorConfig(domain=[self._domain])
                    ),
                    vol.Required("logic_operator", default="or"): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value="or", label="OR (any trigger matches)"),
                                SelectOptionDict(value="and", label="AND (all triggers match)"),
                                SelectOptionDict(value="nor", label="NOR (none match)"),
                                SelectOptionDict(value="nand", label="NAND (not all match)"),
                                SelectOptionDict(value="xor", label="XOR (exactly one matches)"),
                            ],
                            mode="dropdown",
                        )
                    ),
                    vol.Optional("add_another", default=False): BooleanSelector(),
                }
            ),
        )

    def _create_entry(self) -> FlowResult:
        """Create the final config entry."""
        counter_id = self._trigger_entities[0].replace(".", "_")
        counter = {
            "id": counter_id,
            "name": self._name,
            "trigger_entities": self._trigger_entities,
            "trigger_state": self._trigger_state,
            "logic_operator": self._logic_operator or "or",
        }

        return self.async_create_entry(
            title=self._name or "HA Daily Counter",
            data={},
            options={"counters": [counter]},
        )

    @staticmethod
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return HADailyCounterOptionsFlow(entry)
