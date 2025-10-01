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
from homeassistant.core import HomeAssistant

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DOMAIN
from .options_flow import HADailyCounterOptionsFlow


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter with multiple triggers."""

    VERSION = 1

    def __init__(self) -> None:
        self._name: str | None = None
        self._triggers: list[dict[str, str]] = []
        self._available_domain: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step: name, first trigger entity, and its state."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._name = user_input[CONF_NAME]
            trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
            trigger_state = user_input[ATTR_TRIGGER_STATE]

            # Save domain to enforce consistency across triggers
            if self._available_domain is None:
                self._available_domain = trigger_entity.split(".")[0]

            trigger = {
                "entity": trigger_entity,
                "state": trigger_state,
            }
            self._triggers.append(trigger)

            # Ask if user wants another trigger
            if user_input.get("add_another"):
                return await self.async_step_another_trigger()

            # Finish configuration
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
                    vol.Optional("add_another", default=False): bool,
                }
            ),
            description_placeholders={"name": "Counter Name"},
            errors=errors,
        )

    async def async_step_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step to add additional triggers with same state logic."""
        errors: dict[str, str] = {}

        hass: HomeAssistant = self.hass

        if user_input is not None:
            trigger_entity = user_input[ATTR_TRIGGER_ENTITY]

            # State should be the same as first trigger
            trigger_state = self._triggers[0]["state"]

            trigger = {
                "entity": trigger_entity,
                "state": trigger_state,
            }
            self._triggers.append(trigger)

            if user_input.get("add_another"):
                return await self.async_step_another_trigger()

            # Finish configuration
            return self._create_entry()

        # Filter out already selected triggers
        excluded_entities = [t["entity"] for t in self._triggers]

        all_entities = [
            e.entity_id
            for e in hass.states.async_all()
            if self._available_domain and e.entity_id.startswith(self._available_domain)
        ]
        available_entities = [
            e for e in all_entities if e not in excluded_entities
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

    def _create_entry(self) -> FlowResult:
        """Finalize and create the config entry."""
        counter_id = "_".join(
            [t["entity"].replace(".", "_") for t in self._triggers]
        )

        counter = {
            "id": counter_id,
            "name": self._name,
            "triggers": self._triggers,
        }

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
