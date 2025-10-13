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
    AreaSelector,
    AreaSelectorConfig,
)
from homeassistant.data_entry_flow import FlowResult

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DOMAIN
from .options_flow import HADailyCounterOptionsFlow


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter with multiple triggers."""

    VERSION = 1

    def __init__(self) -> None:
        self._name: str | None = None
        self._triggers: list[dict[str, str]] = []
        self._available_domain: str | None = None
        self._add_more: bool = False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step: name, first trigger entity, its state, and add more toggle."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._name = user_input[CONF_NAME]
            trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
            trigger_state = user_input[ATTR_TRIGGER_STATE]

            # Guardamos el dominio para los siguientes disparadores
            if self._available_domain is None:
                self._available_domain = trigger_entity.split(".")[0]

            self._triggers.append(
                {
                    "entity": trigger_entity,
                    "state": trigger_state,
                }
            )

            self._add_more = user_input.get("add_another", False)
            if self._add_more:
                return await self.async_step_another_trigger()

            return await self.async_step_finish()

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
                    vol.Optional("add_another", default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step to add additional triggers with their states."""
        errors: dict[str, str] = {}

        if user_input is not None:
            trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
            trigger_state = user_input[ATTR_TRIGGER_STATE]

            self._triggers.append(
                {
                    "entity": trigger_entity,
                    "state": trigger_state,
                }
            )

            self._add_more = user_input.get("add_another", False)
            if self._add_more:
                return await self.async_step_another_trigger()

            return await self.async_step_finish()

        # Friendly names y filtrado de entidades ya seleccionadas
        excluded_entities = [t["entity"] for t in self._triggers]

        all_entities = [
            e.entity_id
            for e in self.hass.states.async_all()
            if self._available_domain and e.entity_id.startswith(self._available_domain)
        ]
        available_entities = [e for e in all_entities if e not in excluded_entities]

        # Friendly names de triggers previos
        prev_friendly = [
            f"{self.hass.states.get(t['entity']).name} ({t['state']})"
            for t in self._triggers
            if self.hass.states.get(t["entity"])
        ]

        return self.async_show_form(
            step_id="another_trigger",
            data_schema=vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_ENTITY): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=e, label=self.hass.states.get(e).name)
                                for e in available_entities
                                if self.hass.states.get(e)
                            ],
                            mode="dropdown",
                        )
                    ),
                    vol.Required(ATTR_TRIGGER_STATE): str,
                    vol.Optional("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "previous_triggers": ", ".join(prev_friendly) or "None",
                "count": str(len(self._triggers) + 1),
            },
            errors=errors,
        )

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Final step: logic operator and area."""
        if user_input is not None:
            logic_operator = user_input["logic_operator"]
            area = user_input.get("area")

            counter_id = "_".join([t["entity"].replace(".", "_") for t in self._triggers])

            counter = {
                "id": counter_id,
                "name": self._name,
                "triggers": self._triggers,
                "logic": logic_operator,
                "area": area,
            }

            return self.async_create_entry(
                title=self._name or "Daily Counter",
                data={},
                options={"counters": [counter]},
            )

        return self.async_show_form(
            step_id="finish",
            data_schema=vol.Schema(
                {
                    vol.Required("logic_operator"): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value="and", label="AND"),
                                SelectOptionDict(value="or", label="OR"),
                                SelectOptionDict(value="nand", label="NAND"),
                                SelectOptionDict(value="nor", label="NOR"),
                            ],
                            mode="dropdown",
                        )
                    ),
                    vol.Optional("area"): AreaSelector(AreaSelectorConfig()),
                }
            ),
            description_placeholders={
                "count": str(len(self._triggers)),
            },
        )

    @staticmethod
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return HADailyCounterOptionsFlow(entry)
