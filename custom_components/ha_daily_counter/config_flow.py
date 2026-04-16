from __future__ import annotations

import logging
import uuid
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DOMAIN

_LOGGER = logging.getLogger(__name__)

LOGIC_OPTIONS = ["AND", "OR"]  # Only AND and OR, OR by default

# Domain options for entity filtering
DOMAIN_OPTIONS = [
    SelectOptionDict(value="binary_sensor", label="Binary Sensor"),
    SelectOptionDict(value="sensor", label="Sensor"),
    SelectOptionDict(value="automation", label="Automation"),
    SelectOptionDict(value="script", label="Script"),
    SelectOptionDict(value="input_boolean", label="Input Boolean"),
    SelectOptionDict(value="input_number", label="Input Number"),
    SelectOptionDict(value="input_select", label="Input Select"),
]


def _get_entity_states(hass: HomeAssistant, entity_id: str) -> list[str]:
    """Return a list of known/possible states for the given entity.

    For domains with well-known finite states the list is hardcoded.
    For input_select the runtime options attribute is used.
    For all other domains the entity's current state is returned as the
    only option so the user always has a sensible starting point.
    """
    if not entity_id:
        return []
    domain = entity_id.split(".")[0]
    state_obj = hass.states.get(entity_id)

    if domain in (
        "binary_sensor",
        "input_boolean",
        "switch",
        "light",
        "fan",
        "lock",
        "automation",
        "script",
    ):
        return ["on", "off"]
    if domain == "cover":
        return ["open", "closed", "opening", "closing"]
    if domain == "alarm_control_panel":
        return ["disarmed", "armed_home", "armed_away", "armed_night", "pending", "triggered"]
    if domain == "input_select" and state_obj:
        return list(state_obj.attributes.get("options", [state_obj.state]))
    if state_obj:
        return [state_obj.state]
    return []


def _state_selector(states: list[str]):
    """Return a SelectSelector for the given states list, or plain str if empty."""
    if not states:
        return str
    return SelectSelector(
        SelectSelectorConfig(
            options=[SelectOptionDict(value=s, label=s) for s in states],
            mode=SelectSelectorMode.DROPDOWN,
            custom_value=True,
        )
    )


class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter with multiple triggers and an overall logic operator."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler()

    def __init__(self) -> None:
        self._name: str | None = None
        self._triggers: list[dict[str, str]] = []
        self._add_more: bool = False
        self._logic: str = "OR"  # Logic selected only when adding the second trigger
        self._domain_filter: str = "binary_sensor"  # Domain filter selected by user
        self._current_trigger_entity: str = ""  # Entity selected in the current trigger step

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Collect counter name and entity domain filter."""
        _LOGGER.debug("Config flow step 'user' started")
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                self._name = user_input[CONF_NAME]
                self._domain_filter = user_input.get("domain_filter", "binary_sensor")
                return await self.async_step_first_trigger()
            except Exception as err:
                _LOGGER.error("Error in user step: %s", err, exc_info=True)
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required("domain_filter", default=self._domain_filter): SelectSelector(
                    SelectSelectorConfig(
                        options=DOMAIN_OPTIONS,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_first_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Select the first trigger entity (filtered by chosen domain)."""
        _LOGGER.debug("Config flow step 'first_trigger' started")
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                self._current_trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
                return await self.async_step_first_trigger_state()
            except Exception as err:
                _LOGGER.error("Error in first_trigger step: %s", err, exc_info=True)
                errors["base"] = "unknown"

        try:
            data_schema = vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                        EntitySelectorConfig(domain=[self._domain_filter])
                    ),
                }
            )
        except Exception as err:
            _LOGGER.error("Error creating first_trigger schema: %s", err, exc_info=True)
            errors["base"] = "unknown"
            data_schema = vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(EntitySelectorConfig()),
                }
            )

        return self.async_show_form(
            step_id="first_trigger",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_first_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 3: Select the trigger state from a dropdown populated with the entity's known states."""
        _LOGGER.debug("Config flow step 'first_trigger_state' started")
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                trigger_state = user_input[ATTR_TRIGGER_STATE]
                self._triggers.append(
                    {
                        "id": str(uuid.uuid4()),
                        "entity": self._current_trigger_entity,
                        "state": trigger_state,
                    }
                )
                if user_input.get("add_another", False):
                    return await self.async_step_another_trigger()
                return await self.async_step_finish()
            except Exception as err:
                _LOGGER.error("Error in first_trigger_state step: %s", err, exc_info=True)
                errors["base"] = "unknown"

        states = _get_entity_states(self.hass, self._current_trigger_entity)
        data_schema = vol.Schema(
            {
                vol.Required(ATTR_TRIGGER_STATE): _state_selector(states),
                vol.Optional("add_another", default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="first_trigger_state",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Repeatable step to select an additional trigger entity.
        Shows logic selector (AND/OR) only when adding the second trigger.
        """
        _LOGGER.debug("Config flow step 'another_trigger' started")
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Store logic only on the first additional trigger
                if len(self._triggers) == 1 and "logic" in user_input:
                    self._logic = user_input.get("logic", "OR")

                self._current_trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
                return await self.async_step_another_trigger_state()

            except Exception as err:
                _LOGGER.error("Error in another_trigger step: %s", err, exc_info=True)
                errors["base"] = "unknown"

        # Build friendly names of already-configured triggers for the description placeholder
        prev_friendly = []
        for t in self._triggers:
            try:
                state = self.hass.states.get(t["entity"])
                if state and state.name:
                    prev_friendly.append(f"{state.name} ({t['state']})")
                else:
                    prev_friendly.append(f"{t['entity']} ({t['state']})")
            except Exception as err:
                _LOGGER.warning("Error getting friendly name for %s: %s", t.get("entity"), err)
                prev_friendly.append(t.get("entity", "?"))

        # Show logic selector only when adding the second trigger
        is_first_additional = len(self._triggers) == 1
        schema_dict: dict[Any, Any] = {
            vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(EntitySelectorConfig()),
        }
        if is_first_additional:
            schema_dict[vol.Optional("logic", default="OR")] = vol.In(LOGIC_OPTIONS)

        return self.async_show_form(
            step_id="another_trigger",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={"previous_triggers": ", ".join(prev_friendly)},
            errors=errors,
        )

    async def async_step_another_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """State selection step for an additional trigger, using a dropdown of known states."""
        _LOGGER.debug("Config flow step 'another_trigger_state' started")
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                trigger_state = user_input[ATTR_TRIGGER_STATE]
                self._triggers.append(
                    {
                        "id": str(uuid.uuid4()),
                        "entity": self._current_trigger_entity,
                        "state": trigger_state,
                    }
                )
                if user_input.get("add_another", False):
                    return await self.async_step_another_trigger()
                return await self.async_step_finish()
            except Exception as err:
                _LOGGER.error("Error in another_trigger_state step: %s", err, exc_info=True)
                errors["base"] = "unknown"

        states = _get_entity_states(self.hass, self._current_trigger_entity)
        data_schema = vol.Schema(
            {
                vol.Required(ATTR_TRIGGER_STATE): _state_selector(states),
                vol.Optional("add_another", default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="another_trigger_state",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_finish(self) -> FlowResult:
        """Finaliza el flujo y crea la entry con los triggers y la lógica seleccionada en el primer paso."""
        _LOGGER.debug("Config flow step 'finish' started")
        
        try:
            title = self._name or "HA Daily Counter"

            # Build the counter in the format expected by sensor.py / OptionsFlowHandler
            counter = {
                "id": str(uuid.uuid4()),
                "name": title,
                "triggers": self._triggers,
                "logic": self._logic,
            }

            _LOGGER.info(
                "Creating config entry: title=%s, triggers_count=%d, logic=%s",
                title,
                len(self._triggers),
                self._logic,
            )

            # Store counters in entry.options so that async_setup_entry in sensor.py
            # can read entry.options.get("counters", []) and create entities immediately.
            return self.async_create_entry(
                title=title,
                data={},
                options={"counters": [counter]},
            )
            
        except Exception as err:
            _LOGGER.error(
                "Error creating config entry: %s",
                err,
                exc_info=True,
            )
            # Return to user step if creation fails
            return await self.async_step_user()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow for HA Daily Counter."""

    def __init__(self) -> None:
        self._counters: list[dict[str, Any]] = []
        self._new_counter: dict[str, Any] = {}
        self._new_counter_domain: str = "binary_sensor"
        self._selected_delete_name: str | None = None
        self._selected_edit_index: int | None = None
        self._editing_counter: dict[str, Any] = {}
        self._editing_domain: str = "binary_sensor"

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Initial step: add, edit, or delete a counter."""
        # Initialize counters from config_entry on first call
        if not self._counters:
            self._counters = list(self.config_entry.options.get("counters", []))
        
        if user_input is not None:
            if user_input["action"] == "add":
                return await self.async_step_user()
            elif user_input["action"] == "edit":
                return await self.async_step_select_edit()
            elif user_input["action"] == "delete":
                return await self.async_step_select_delete()

            return self.async_create_entry(title="", data={"counters": self._counters})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    "action": SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value="add", label="Add counter"),
                                SelectOptionDict(value="edit", label="Edit counter"),
                                SelectOptionDict(value="delete", label="Delete counter"),
                                SelectOptionDict(value="finish", label="Finish setup"),
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to collect the name of the new counter."""
        if user_input is not None:
            self._new_counter = {"name": user_input["name"]}
            return await self.async_step_trigger_domain()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({"name": str}),
        )

    async def async_step_trigger_domain(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to select the entity domain filter before picking the trigger entity."""
        if user_input is not None:
            self._new_counter_domain = user_input.get("domain_filter", "binary_sensor")
            return await self.async_step_trigger_entity()

        return self.async_show_form(
            step_id="trigger_domain",
            data_schema=vol.Schema(
                {
                    vol.Required("domain_filter", default=self._new_counter_domain): SelectSelector(
                        SelectSelectorConfig(
                            options=DOMAIN_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_trigger_entity(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to collect the entity that triggers the counter."""
        if user_input is not None:
            self._new_counter["trigger_entity"] = user_input["trigger_entity"]
            return await self.async_step_trigger_state()

        return self.async_show_form(
            step_id="trigger_entity",
            data_schema=vol.Schema(
                {
                    "trigger_entity": EntitySelector(
                        EntitySelectorConfig(domain=[self._new_counter_domain])
                    ),
                }
            ),
        )

    async def async_step_trigger_state(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to collect the trigger state via a dropdown of the entity's known states."""
        if user_input is not None:
            self._new_counter["trigger_state"] = user_input["trigger_state"]
            self._new_counter["id"] = str(uuid.uuid4())
            self._counters.append(self._new_counter)

            return await self.async_step_init()

        entity_id = self._new_counter.get("trigger_entity", "")
        states = _get_entity_states(self.hass, entity_id)

        return self.async_show_form(
            step_id="trigger_state",
            data_schema=vol.Schema({"trigger_state": _state_selector(states)}),
        )

    async def async_step_select_edit(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to select a counter to edit."""
        if not self._counters:
            return await self.async_step_init()

        if user_input is not None:
            selected_name = user_input["edit_target"]
            for idx, counter in enumerate(self._counters):
                if counter["name"] == selected_name:
                    self._selected_edit_index = idx
                    self._editing_counter = dict(counter)
                    # Pre-select the domain of the current trigger entity
                    current_entity = self._editing_counter.get("trigger_entity", "")
                    self._editing_domain = current_entity.split(".")[0] if current_entity else "binary_sensor"
                    return await self.async_step_edit_trigger_domain()
            return await self.async_step_init()

        return self.async_show_form(
            step_id="select_edit",
            data_schema=vol.Schema(
                {
                    "edit_target": SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=c["name"], label=c["name"])
                                for c in self._counters
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_edit_trigger_domain(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to select entity domain filter before editing the trigger entity."""
        if user_input is not None:
            self._editing_domain = user_input.get("domain_filter", self._editing_domain)
            return await self.async_step_edit_trigger_entity()

        return self.async_show_form(
            step_id="edit_trigger_domain",
            data_schema=vol.Schema(
                {
                    vol.Required("domain_filter", default=self._editing_domain): SelectSelector(
                        SelectSelectorConfig(
                            options=DOMAIN_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_trigger_entity(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to edit the trigger entity."""
        if user_input is not None:
            self._editing_counter["trigger_entity"] = user_input["trigger_entity"]
            return await self.async_step_edit_trigger_state()

        current_entity = self._editing_counter.get("trigger_entity", "")

        return self.async_show_form(
            step_id="edit_trigger_entity",
            data_schema=vol.Schema(
                {
                    "trigger_entity": EntitySelector(
                        EntitySelectorConfig(domain=[self._editing_domain])
                    ),
                }
            ),
            description_placeholders={
                "current_value": current_entity,
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_trigger_state(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to edit the trigger state via a dropdown of the entity's known states."""
        if user_input is not None:
            self._editing_counter["trigger_state"] = user_input["trigger_state"]
            # Update the counter in the list
            if self._selected_edit_index is not None and 0 <= self._selected_edit_index < len(self._counters):
                self._counters[self._selected_edit_index] = self._editing_counter

            # Reset editing state
            self._selected_edit_index = None
            self._editing_counter = {}

            return await self.async_step_init()

        current_state = self._editing_counter.get("trigger_state", "")
        entity_id = self._editing_counter.get("trigger_entity", "")
        states = _get_entity_states(self.hass, entity_id)

        return self.async_show_form(
            step_id="edit_trigger_state",
            data_schema=vol.Schema({"trigger_state": _state_selector(states)}),
            description_placeholders={
                "current_value": current_state,
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_select_delete(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to select a counter to delete."""
        if not self._counters:
            return await self.async_step_init()

        if user_input is not None:
            self._selected_delete_name = user_input["delete_target"]
            return await self.async_step_confirm_delete()

        return self.async_show_form(
            step_id="select_delete",
            data_schema=vol.Schema(
                {
                    "delete_target": SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=c["name"], label=c["name"])
                                for c in self._counters
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_confirm_delete(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Confirm and delete the selected counter."""
        if user_input is not None and user_input.get("confirm_delete"):
            self._counters = [c for c in self._counters if c["name"] != self._selected_delete_name]

        return await self.async_step_init()

    @callback
    def async_get_options(self) -> dict[str, Any]:
        return {"counters": self._counters}
