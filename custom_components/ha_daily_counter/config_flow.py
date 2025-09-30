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


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HA Daily Counter."""

    VERSION = 1

    def __init__(self) -> None:
        self._trigger_entity: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # If entity already selected but state not yet chosen, go to next step
            if ATTR_TRIGGER_ENTITY in user_input and ATTR_TRIGGER_STATE not in user_input:
                self._trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
                return await self.async_step_trigger_state(user_input)

            # Final step: both entity and state selected
            if (
                CONF_NAME in user_input
                and ATTR_TRIGGER_ENTITY in user_input
                and ATTR_TRIGGER_STATE in user_input
            ):
                name = user_input[CONF_NAME]
                trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
                trigger_state = user_input[ATTR_TRIGGER_STATE]

                counter_id = trigger_entity.replace(".", "_")

                counter = {
                    "id": counter_id,
                    "name": name,
                    "trigger_entity": trigger_entity,
                    "trigger_state": trigger_state,
                }

                return self.async_create_entry(
                    title=name,
                    data={},
                    options={"counters": [counter]},
                )

        # First step: ask for name + entity
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
            errors=errors,
        )

    async def async_step_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Second step: show available states dynamically based on the selected entity."""
        if self._trigger_entity is None:
            return await self.async_step_user(user_input)

        hass: HomeAssistant = self.hass
        entity_state = hass.states.get(self._trigger_entity)

        options: list[SelectOptionDict] = []
        if entity_state is not None:
            options = [
                SelectOptionDict(value=state, label=state)
                for state in {entity_state.state, *entity_state.attributes.get("options", [])}
                if state not in ("unknown", "unavailable")
            ]

        if user_input is not None and ATTR_TRIGGER_STATE in user_input:
            # Completed selection: return to async_step_user with full data
            return await self.async_step_user(
                {
                    CONF_NAME: user_input.get(CONF_NAME, "Daily Counter"),
                    ATTR_TRIGGER_ENTITY: self._trigger_entity,
                    ATTR_TRIGGER_STATE: user_input[ATTR_TRIGGER_STATE],
                }
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
        )

    @staticmethod
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return HADailyCounterOptionsFlow(entry)
