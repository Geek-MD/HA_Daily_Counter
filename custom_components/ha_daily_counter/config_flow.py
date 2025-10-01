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
)

from homeassistant.data_entry_flow import FlowResult

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DOMAIN
from .options_flow import HADailyCounterOptionsFlow


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter with multiple triggers and reconfigure support."""

    VERSION = 1

    def __init__(self) -> None:
        self._name: str | None = None
        self._triggers: list[dict[str, str]] = []
        self._available_domain: str | None = None
        self._editing_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step: name, first trigger entity, and its state."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._name = user_input[CONF_NAME]
            trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
            trigger_state = user_input[ATTR_TRIGGER_STATE]

            if self._available_domain is None:
                self._available_domain = trigger_entity.split(".")[0]

            trigger = {"entity": trigger_entity, "state": trigger_state}
            self._triggers.append(trigger)

            if user_input.get("add_another"):
                return await self.async_step_another_trigger()

            return self._create_entry()

        defaults: dict[str, Any] = {}
        if self._editing_entry:
            counter = self._editing_entry.options["counters"][0]
            defaults = {
                CONF_NAME: counter["name"],
                ATTR_TRIGGER_ENTITY: counter["triggers"][0]["entity"],
                ATTR_TRIGGER_STATE: counter["triggers"][0]["state"],
            }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
                    vol.Required(
                        ATTR_TRIGGER_ENTITY, default=defaults.get(ATTR_TRIGGER_ENTITY, "")
                    ): EntitySelector(
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
                    vol.Required(
                        ATTR_TRIGGER_STATE, default=defaults.get(ATTR_TRIGGER_STATE, "")
                    ): str,
                    vol.Optional("add_another", default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step to add additional triggers with same state logic."""
        errors: dict[str, str] = {}

        if user_input is not None:
            trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
            trigger_state = self._triggers[0]["state"]

            trigger = {"entity": trigger_entity, "state": trigger_state}
            self._triggers.append(trigger)

            if user_input.get("add_another"):
                return await self.async_step_another_trigger()

            return self._create_entry()

        excluded_entities = [t["entity"] for t in self._triggers]

        available_entities = [
            e.entity_id
            for e in self.hass.states.async_all()
            if self._available_domain and e.entity_id.startswith(self._available_domain)
            and e.entity_id not in excluded_entities
        ]

        return self.async_show_form(
            step_id="another_trigger",
            data_schema=vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_ENTITY): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=e, label=e)
                                for e in available_entities
                            ],
                            mode="dropdown",
                        )
                    ),
                    vol.Optional("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "count": str(len(self._triggers) + 1),
            },
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of an existing counter."""
        self._editing_entry = self._get_reconfigure_entry()
        return await self.async_step_user(user_input)

    def _get_reconfigure_entry(self) -> config_entries.ConfigEntry | None:
        """Helper to get the entry being reconfigured."""
        return self.hass.config_entries.async_get_entry(self.context.get("entry_id"))

    def _create_entry(self) -> FlowResult:
        """Finalize and create or update the config entry."""
        counter_id = "_".join([t["entity"].replace(".", "_") for t in self._triggers])

        counter = {
            "id": counter_id,
            "name": self._name,
            "triggers": self._triggers,
        }

        if self._editing_entry:
            self.hass.config_entries.async_update_entry(
                self._editing_entry,
                options={"counters": [counter]},
            )
            return self.async_abort(reason="reconfigured")

        return self.async_create_entry(
            title=self._name or "Daily Counter",
            data={},
            options={"counters": [counter]},
        )

    @staticmethod
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return HADailyCounterOptionsFlow(entry)
