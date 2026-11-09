from __future__ import annotations

import logging
import uuid
from typing import Any

import probatio
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    StateSelector,
    StateSelectorConfig,
)

from .const import (
    ATTR_TRIGGER_ENTITY,
    ATTR_TRIGGER_STATE,
    CONF_COUNT_MODE,
    CONF_DIAGNOSTIC,
    CONF_MAX_CHANGES,
    CONF_RESET_CYCLE,
    CONF_TRACK_USAGE_TIME,
    CONF_USAGE_STATE,
    COUNT_MODE_LIMITED,
    COUNT_MODES,
    DEFAULT_COUNT_MODE,
    DEFAULT_DIAGNOSTIC,
    DEFAULT_MAX_CHANGES,
    DEFAULT_RESET_CYCLE,
    DEFAULT_TRACK_USAGE_TIME,
    DOMAIN,
    RESET_CYCLES,
)

_LOGGER = logging.getLogger(__name__)

LOGIC_OPTIONS = ["AND", "OR"]  # Only AND and OR, OR by default


def _reset_cycle_selector() -> SelectSelector:
    """Return the translated reset-cycle selector."""
    return SelectSelector(
        SelectSelectorConfig(
            options=RESET_CYCLES,
            mode=SelectSelectorMode.DROPDOWN,
            translation_key="reset_cycle",
        )
    )


def _count_mode_selector() -> SelectSelector:
    """Return the translated count-mode selector."""
    return SelectSelector(
        SelectSelectorConfig(
            options=COUNT_MODES,
            mode=SelectSelectorMode.DROPDOWN,
            translation_key="count_mode",
        )
    )


def _max_changes_selector() -> NumberSelector:
    """Return a positive integer selector for the per-cycle limit."""
    return NumberSelector(
        NumberSelectorConfig(min=1, step=1, mode=NumberSelectorMode.BOX)
    )

# Domain options for entity filtering
DOMAIN_OPTIONS = [
    SelectOptionDict(value="binary_sensor", label="Binary Sensor"),
    SelectOptionDict(value="sensor", label="Sensor"),
    SelectOptionDict(value="switch", label="Switch"),
    SelectOptionDict(value="light", label="Light"),
    SelectOptionDict(value="fan", label="Fan"),
    SelectOptionDict(value="cover", label="Cover"),
    SelectOptionDict(value="lock", label="Lock"),
    SelectOptionDict(value="alarm_control_panel", label="Alarm Control Panel"),
    SelectOptionDict(value="automation", label="Automation"),
    SelectOptionDict(value="script", label="Script"),
    SelectOptionDict(value="input_boolean", label="Input Boolean"),
    SelectOptionDict(value="input_number", label="Input Number"),
    SelectOptionDict(value="input_select", label="Input Select"),
]


def _state_selector(entity_id: str) -> StateSelector:
    """Return Home Assistant's dynamic state selector for an entity."""
    return StateSelector(StateSelectorConfig(entity_id=entity_id))


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
        self._reset_cycle: str = DEFAULT_RESET_CYCLE
        self._count_mode: str = DEFAULT_COUNT_MODE
        self._max_changes: int = DEFAULT_MAX_CHANGES
        self._diagnostic: bool = DEFAULT_DIAGNOSTIC
        self._track_usage_time: bool = DEFAULT_TRACK_USAGE_TIME
        self._usage_state: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
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

        data_schema = probatio.Schema(
            {
                probatio.Required(CONF_NAME): str,
                probatio.Required("domain_filter", default=self._domain_filter): SelectSelector(
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
    ) -> ConfigFlowResult:
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
            data_schema = probatio.Schema(
                {
                    probatio.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                        EntitySelectorConfig(domain=[self._domain_filter])
                    ),
                }
            )
        except Exception as err:
            _LOGGER.error("Error creating first_trigger schema: %s", err, exc_info=True)
            errors["base"] = "unknown"
            data_schema = probatio.Schema(
                {
                    probatio.Required(ATTR_TRIGGER_ENTITY): EntitySelector(EntitySelectorConfig()),
                }
            )

        return self.async_show_form(
            step_id="first_trigger",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_first_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
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
                return await self.async_step_reset_cycle()
            except Exception as err:
                _LOGGER.error("Error in first_trigger_state step: %s", err, exc_info=True)
                errors["base"] = "unknown"

        data_schema = probatio.Schema(
            {
                probatio.Required(ATTR_TRIGGER_STATE): _state_selector(
                    self._current_trigger_entity
                ),
                probatio.Optional("add_another", default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="first_trigger_state",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
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
            probatio.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                EntitySelectorConfig(domain=[self._domain_filter])
            ),
        }
        if is_first_additional:
            schema_dict[probatio.Optional("logic", default="OR")] = probatio.In(LOGIC_OPTIONS)

        return self.async_show_form(
            step_id="another_trigger",
            data_schema=probatio.Schema(schema_dict),
            description_placeholders={"previous_triggers": ", ".join(prev_friendly)},
            errors=errors,
        )

    async def async_step_another_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
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
                return await self.async_step_reset_cycle()
            except Exception as err:
                _LOGGER.error("Error in another_trigger_state step: %s", err, exc_info=True)
                errors["base"] = "unknown"

        data_schema = probatio.Schema(
            {
                probatio.Required(ATTR_TRIGGER_STATE): _state_selector(
                    self._current_trigger_entity
                ),
                probatio.Optional("add_another", default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="another_trigger_state",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reset_cycle(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select how often this counter resets."""
        if user_input is not None:
            self._reset_cycle = user_input[CONF_RESET_CYCLE]
            return await self.async_step_count_mode()

        return self.async_show_form(
            step_id="reset_cycle",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_RESET_CYCLE, default=self._reset_cycle
                    ): _reset_cycle_selector(),
                }
            ),
        )

    async def async_step_count_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose whether all changes or a limited number are counted per cycle."""
        if user_input is not None:
            self._count_mode = user_input[CONF_COUNT_MODE]
            if self._count_mode == COUNT_MODE_LIMITED:
                return await self.async_step_max_changes()
            return await self.async_step_additional_options()

        return self.async_show_form(
            step_id="count_mode",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_COUNT_MODE, default=self._count_mode
                    ): _count_mode_selector(),
                }
            ),
        )

    async def async_step_max_changes(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the maximum number of changes counted per cycle."""
        if user_input is not None:
            self._max_changes = max(1, int(user_input[CONF_MAX_CHANGES]))
            return await self.async_step_additional_options()

        return self.async_show_form(
            step_id="max_changes",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_MAX_CHANGES, default=self._max_changes
                    ): _max_changes_selector(),
                }
            ),
        )

    async def async_step_additional_options(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose optional diagnostic and usage-time entities."""
        if user_input is not None:
            self._diagnostic = user_input.get(CONF_DIAGNOSTIC, False)
            self._track_usage_time = user_input.get(CONF_TRACK_USAGE_TIME, False)
            if self._track_usage_time:
                return await self.async_step_usage_state()
            return await self.async_step_finish()

        return self.async_show_form(
            step_id="additional_options",
            data_schema=probatio.Schema(
                {
                    probatio.Optional(
                        CONF_DIAGNOSTIC, default=self._diagnostic
                    ): bool,
                    probatio.Optional(
                        CONF_TRACK_USAGE_TIME, default=self._track_usage_time
                    ): bool,
                }
            ),
        )

    async def async_step_usage_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the primary entity state whose duration will be accumulated."""
        if user_input is not None:
            self._usage_state = user_input[CONF_USAGE_STATE]
            return await self.async_step_finish()

        primary_entity = self._triggers[0]["entity"] if self._triggers else ""
        return self.async_show_form(
            step_id="usage_state",
            data_schema=probatio.Schema(
                {probatio.Required(CONF_USAGE_STATE): _state_selector(primary_entity)}
            ),
            description_placeholders={"entity_id": primary_entity},
        )

    async def async_step_finish(self) -> ConfigFlowResult:
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
                CONF_RESET_CYCLE: self._reset_cycle,
                CONF_COUNT_MODE: self._count_mode,
                CONF_MAX_CHANGES: self._max_changes,
                CONF_DIAGNOSTIC: self._diagnostic,
                CONF_TRACK_USAGE_TIME: self._track_usage_time,
                CONF_USAGE_STATE: self._usage_state,
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
        self._new_counter_triggers: list[dict[str, str]] = []
        self._new_counter_logic: str = "OR"
        self._new_counter_current_entity: str = ""
        self._new_counter_reset_cycle: str = DEFAULT_RESET_CYCLE
        self._new_counter_count_mode: str = DEFAULT_COUNT_MODE
        self._new_counter_max_changes: int = DEFAULT_MAX_CHANGES
        self._new_counter_diagnostic: bool = DEFAULT_DIAGNOSTIC
        self._new_counter_track_usage_time: bool = DEFAULT_TRACK_USAGE_TIME
        self._new_counter_usage_state: str = ""
        self._selected_delete_name: str | None = None
        self._selected_edit_index: int | None = None
        self._editing_counter: dict[str, Any] = {}
        self._editing_domain: str = "binary_sensor"
        self._editing_triggers: list[dict[str, str]] = []
        self._editing_logic: str = "OR"
        self._editing_current_entity: str = ""
        self._editing_reset_cycle: str = DEFAULT_RESET_CYCLE
        self._editing_count_mode: str = DEFAULT_COUNT_MODE
        self._editing_max_changes: int = DEFAULT_MAX_CHANGES
        self._editing_diagnostic: bool = DEFAULT_DIAGNOSTIC
        self._editing_track_usage_time: bool = DEFAULT_TRACK_USAGE_TIME
        self._editing_usage_state: str = ""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Initial step: directly proceed to editing the counter."""
        # Initialize counters from config_entry on first call
        if not self._counters:
            self._counters = list(self.config_entry.options.get("counters", []))
            if not self._counters and self.config_entry.data.get("triggers"):
                self._counters = [
                    {
                        "id": self.config_entry.entry_id,
                        "name": self.config_entry.title,
                        "triggers": self.config_entry.data.get("triggers", []),
                        "logic": self.config_entry.data.get("logic", "OR"),
                        CONF_RESET_CYCLE: self.config_entry.data.get(
                            CONF_RESET_CYCLE, DEFAULT_RESET_CYCLE
                        ),
                        CONF_COUNT_MODE: DEFAULT_COUNT_MODE,
                        CONF_MAX_CHANGES: DEFAULT_MAX_CHANGES,
                        CONF_DIAGNOSTIC: DEFAULT_DIAGNOSTIC,
                        CONF_TRACK_USAGE_TIME: DEFAULT_TRACK_USAGE_TIME,
                    }
                ]

        # If no counters exist yet, start the add flow
        if not self._counters:
            return await self.async_step_user()

        # If there is exactly one counter, select it automatically and go straight to editing
        if len(self._counters) == 1:
            self._selected_edit_index = 0
            self._editing_counter = dict(self._counters[0])
            self._editing_triggers = []
            self._editing_logic = "OR"
            self._editing_current_entity = ""
            self._editing_reset_cycle = self._editing_counter.get(
                CONF_RESET_CYCLE, DEFAULT_RESET_CYCLE
            )
            self._editing_count_mode = self._editing_counter.get(
                CONF_COUNT_MODE, DEFAULT_COUNT_MODE
            )
            self._editing_max_changes = self._editing_counter.get(
                CONF_MAX_CHANGES, DEFAULT_MAX_CHANGES
            )
            self._editing_diagnostic = self._editing_counter.get(
                CONF_DIAGNOSTIC, DEFAULT_DIAGNOSTIC
            )
            self._editing_track_usage_time = self._editing_counter.get(
                CONF_TRACK_USAGE_TIME, DEFAULT_TRACK_USAGE_TIME
            )
            self._editing_usage_state = self._editing_counter.get(
                CONF_USAGE_STATE, ""
            )
            current_entity = self._editing_counter.get("trigger_entity", "")
            if not current_entity:
                first = (self._editing_counter.get("triggers") or [{}])[0]
                current_entity = first.get("entity", "")
            self._editing_domain = current_entity.split(".")[0] if current_entity else "binary_sensor"
            return await self.async_step_edit_trigger_domain()

        # Multiple counters: let the user choose which one to edit
        return await self.async_step_select_edit()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to collect the name of the new counter."""
        if user_input is not None:
            self._new_counter = {"name": user_input["name"]}
            return await self.async_step_trigger_domain()

        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema({"name": str}),
        )

    async def async_step_trigger_domain(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to select the entity domain filter before picking the trigger entity."""
        if user_input is not None:
            self._new_counter_domain = user_input.get("domain_filter", "binary_sensor")
            return await self.async_step_trigger_entity()

        return self.async_show_form(
            step_id="trigger_domain",
            data_schema=probatio.Schema(
                {
                    probatio.Required("domain_filter", default=self._new_counter_domain): SelectSelector(
                        SelectSelectorConfig(
                            options=DOMAIN_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_trigger_entity(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to collect the entity that triggers the counter."""
        if user_input is not None:
            self._new_counter_current_entity = user_input["trigger_entity"]
            # Keep legacy key for backward compat in case anything reads it
            self._new_counter["trigger_entity"] = self._new_counter_current_entity
            return await self.async_step_trigger_state()

        return self.async_show_form(
            step_id="trigger_entity",
            data_schema=probatio.Schema(
                {
                    "trigger_entity": EntitySelector(
                        EntitySelectorConfig(domain=[self._new_counter_domain])
                    ),
                }
            ),
        )

    async def async_step_trigger_state(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to collect the trigger state via a dropdown of the entity's known states."""
        if user_input is not None:
            self._new_counter_triggers.append(
                {
                    "id": str(uuid.uuid4()),
                    "entity": self._new_counter_current_entity,
                    "state": user_input["trigger_state"],
                }
            )
            if user_input.get("add_another", False):
                return await self.async_step_new_another_trigger()
            return await self.async_step_new_reset_cycle()

        return self.async_show_form(
            step_id="trigger_state",
            data_schema=probatio.Schema(
                {
                    probatio.Required("trigger_state"): _state_selector(
                        self._new_counter_current_entity
                    ),
                    probatio.Optional("add_another", default=False): bool,
                }
            ),
        )

    async def async_step_new_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Repeatable step to add an extra trigger entity while creating a new counter.

        The entity selector is restricted to the same domain as the first entity.
        """
        if user_input is not None:
            if len(self._new_counter_triggers) == 1 and "logic" in user_input:
                self._new_counter_logic = user_input.get("logic", "OR")
            self._new_counter_current_entity = user_input[ATTR_TRIGGER_ENTITY]
            return await self.async_step_new_another_trigger_state()

        prev_friendly: list[str] = []
        for t in self._new_counter_triggers:
            try:
                state = self.hass.states.get(t["entity"])
                if state and state.name:
                    prev_friendly.append(f"{state.name} ({t['state']})")
                else:
                    prev_friendly.append(f"{t['entity']} ({t['state']})")
            except (KeyError, AttributeError) as err:
                _LOGGER.warning("Error getting friendly name for %s: %s", t.get("entity"), err)
                prev_friendly.append(t.get("entity", "?"))

        is_first_additional = len(self._new_counter_triggers) == 1
        schema_dict: dict[Any, Any] = {
            probatio.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                EntitySelectorConfig(domain=[self._new_counter_domain])
            ),
        }
        if is_first_additional:
            schema_dict[probatio.Optional("logic", default="OR")] = probatio.In(LOGIC_OPTIONS)

        return self.async_show_form(
            step_id="new_another_trigger",
            data_schema=probatio.Schema(schema_dict),
            description_placeholders={"previous_triggers": ", ".join(prev_friendly)},
        )

    async def async_step_new_another_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """State selection step for an additional trigger while creating a new counter."""
        if user_input is not None:
            self._new_counter_triggers.append(
                {
                    "id": str(uuid.uuid4()),
                    "entity": self._new_counter_current_entity,
                    "state": user_input[ATTR_TRIGGER_STATE],
                }
            )
            if user_input.get("add_another", False):
                return await self.async_step_new_another_trigger()
            return await self.async_step_new_reset_cycle()

        return self.async_show_form(
            step_id="new_another_trigger_state",
            data_schema=probatio.Schema(
                {
                    probatio.Required(ATTR_TRIGGER_STATE): _state_selector(
                        self._new_counter_current_entity
                    ),
                    probatio.Optional("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "counter_name": self._new_counter.get("name", ""),
            },
        )

    async def async_step_new_reset_cycle(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the reset cycle for a new counter."""
        if user_input is not None:
            self._new_counter_reset_cycle = user_input[CONF_RESET_CYCLE]
            return await self.async_step_new_count_mode()

        return self.async_show_form(
            step_id="new_reset_cycle",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_RESET_CYCLE, default=self._new_counter_reset_cycle
                    ): _reset_cycle_selector(),
                }
            ),
        )

    async def async_step_new_count_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the count mode for a new counter."""
        if user_input is not None:
            self._new_counter_count_mode = user_input[CONF_COUNT_MODE]
            if self._new_counter_count_mode == COUNT_MODE_LIMITED:
                return await self.async_step_new_max_changes()
            return await self.async_step_new_additional_options()

        return self.async_show_form(
            step_id="new_count_mode",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_COUNT_MODE, default=self._new_counter_count_mode
                    ): _count_mode_selector(),
                }
            ),
        )

    async def async_step_new_max_changes(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the per-cycle limit for a new counter."""
        if user_input is not None:
            self._new_counter_max_changes = max(
                1, int(user_input[CONF_MAX_CHANGES])
            )
            return await self.async_step_new_additional_options()

        return self.async_show_form(
            step_id="new_max_changes",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_MAX_CHANGES, default=self._new_counter_max_changes
                    ): _max_changes_selector(),
                }
            ),
        )

    async def async_step_new_additional_options(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose optional entities for a new counter."""
        if user_input is not None:
            self._new_counter_diagnostic = user_input.get(CONF_DIAGNOSTIC, False)
            self._new_counter_track_usage_time = user_input.get(
                CONF_TRACK_USAGE_TIME, False
            )
            if self._new_counter_track_usage_time:
                return await self.async_step_new_usage_state()
            return await self.async_step_new_counter_finish()

        return self.async_show_form(
            step_id="new_additional_options",
            data_schema=probatio.Schema(
                {
                    probatio.Optional(
                        CONF_DIAGNOSTIC, default=self._new_counter_diagnostic
                    ): bool,
                    probatio.Optional(
                        CONF_TRACK_USAGE_TIME,
                        default=self._new_counter_track_usage_time,
                    ): bool,
                }
            ),
        )

    async def async_step_new_usage_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the usage state for a new counter's primary entity."""
        if user_input is not None:
            self._new_counter_usage_state = user_input[CONF_USAGE_STATE]
            return await self.async_step_new_counter_finish()

        primary_entity = (
            self._new_counter_triggers[0]["entity"]
            if self._new_counter_triggers
            else ""
        )
        schema: dict[Any, Any] = {
            probatio.Required(CONF_USAGE_STATE): _state_selector(primary_entity)
        }
        return self.async_show_form(
            step_id="new_usage_state",
            data_schema=probatio.Schema(schema),
            description_placeholders={"entity_id": primary_entity},
        )

    async def async_step_new_counter_finish(self) -> ConfigFlowResult:
        """Finalise a new counter created through the options flow."""
        counter: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "name": self._new_counter.get("name", "Unnamed Counter"),
            "triggers": self._new_counter_triggers,
            "logic": self._new_counter_logic,
            CONF_RESET_CYCLE: self._new_counter_reset_cycle,
            CONF_COUNT_MODE: self._new_counter_count_mode,
            CONF_MAX_CHANGES: self._new_counter_max_changes,
            CONF_DIAGNOSTIC: self._new_counter_diagnostic,
            CONF_TRACK_USAGE_TIME: self._new_counter_track_usage_time,
            CONF_USAGE_STATE: self._new_counter_usage_state,
        }
        self._counters.append(counter)

        # Reset new-counter state for a potential next run
        self._new_counter = {}
        self._new_counter_triggers = []
        self._new_counter_logic = "OR"
        self._new_counter_current_entity = ""

        return self.async_create_entry(title="", data={"counters": self._counters})

    async def async_step_select_edit(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to select a counter to edit."""
        if not self._counters:
            return await self.async_step_init()

        if user_input is not None:
            selected_name = user_input["edit_target"]
            for idx, counter in enumerate(self._counters):
                if counter["name"] == selected_name:
                    self._selected_edit_index = idx
                    self._editing_counter = dict(counter)
                    self._editing_triggers = []
                    self._editing_logic = "OR"
                    self._editing_current_entity = ""
                    self._editing_reset_cycle = self._editing_counter.get(
                        CONF_RESET_CYCLE, DEFAULT_RESET_CYCLE
                    )
                    self._editing_count_mode = self._editing_counter.get(
                        CONF_COUNT_MODE, DEFAULT_COUNT_MODE
                    )
                    self._editing_max_changes = self._editing_counter.get(
                        CONF_MAX_CHANGES, DEFAULT_MAX_CHANGES
                    )
                    self._editing_diagnostic = self._editing_counter.get(
                        CONF_DIAGNOSTIC, DEFAULT_DIAGNOSTIC
                    )
                    self._editing_track_usage_time = self._editing_counter.get(
                        CONF_TRACK_USAGE_TIME, DEFAULT_TRACK_USAGE_TIME
                    )
                    self._editing_usage_state = self._editing_counter.get(
                        CONF_USAGE_STATE, ""
                    )
                    current_entity = self._editing_counter.get("trigger_entity", "")
                    if not current_entity:
                        first = (self._editing_counter.get("triggers") or [{}])[0]
                        current_entity = first.get("entity", "")
                    self._editing_domain = current_entity.split(".")[0] if current_entity else "binary_sensor"
                    return await self.async_step_edit_trigger_domain()
            return await self.async_step_init()

        return self.async_show_form(
            step_id="select_edit",
            data_schema=probatio.Schema(
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

    async def async_step_edit_trigger_domain(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to select entity domain filter before editing the trigger entity."""
        if user_input is not None:
            self._editing_domain = user_input.get("domain_filter", self._editing_domain)
            return await self.async_step_edit_trigger_entity()

        return self.async_show_form(
            step_id="edit_trigger_domain",
            data_schema=probatio.Schema(
                {
                    probatio.Required("domain_filter", default=self._editing_domain): SelectSelector(
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

    async def async_step_edit_trigger_entity(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to edit the trigger entity."""
        if user_input is not None:
            self._editing_current_entity = user_input["trigger_entity"]
            return await self.async_step_edit_trigger_state()

        current_entity = self._editing_counter.get("trigger_entity", "")
        if not current_entity:
            first = (self._editing_counter.get("triggers") or [{}])[0]
            current_entity = first.get("entity", "")

        return self.async_show_form(
            step_id="edit_trigger_entity",
            data_schema=probatio.Schema(
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

    async def async_step_edit_trigger_state(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to edit the trigger state.  Asks whether to add another entity afterwards."""
        if user_input is not None:
            self._editing_triggers.append(
                {
                    "id": str(uuid.uuid4()),
                    "entity": self._editing_current_entity,
                    "state": user_input[ATTR_TRIGGER_STATE],
                }
            )
            if user_input.get("add_another", False):
                return await self.async_step_edit_another_trigger()
            return await self.async_step_edit_reset_cycle()

        return self.async_show_form(
            step_id="edit_trigger_state",
            data_schema=probatio.Schema(
                {
                    probatio.Required(ATTR_TRIGGER_STATE): _state_selector(
                        self._editing_current_entity
                    ),
                    probatio.Optional("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Repeatable step to add an extra monitored entity while editing a counter."""
        if user_input is not None:
            if len(self._editing_triggers) == 1 and "logic" in user_input:
                self._editing_logic = user_input.get("logic", "OR")
            self._editing_current_entity = user_input[ATTR_TRIGGER_ENTITY]
            return await self.async_step_edit_another_trigger_state()

        prev_friendly: list[str] = []
        for t in self._editing_triggers:
            try:
                state = self.hass.states.get(t["entity"])
                if state and state.name:
                    prev_friendly.append(f"{state.name} ({t['state']})")
                else:
                    prev_friendly.append(f"{t['entity']} ({t['state']})")
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Error getting friendly name for %s: %s", t.get("entity"), err)
                prev_friendly.append(t.get("entity", "?"))

        is_first_additional = len(self._editing_triggers) == 1
        schema_dict: dict[Any, Any] = {
            probatio.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                EntitySelectorConfig(domain=[self._editing_domain])
            ),
        }
        if is_first_additional:
            schema_dict[probatio.Optional("logic", default="OR")] = probatio.In(LOGIC_OPTIONS)

        return self.async_show_form(
            step_id="edit_another_trigger",
            data_schema=probatio.Schema(schema_dict),
            description_placeholders={"previous_triggers": ", ".join(prev_friendly)},
        )

    async def async_step_edit_another_trigger_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """State selection step for an additional trigger while editing a counter."""
        if user_input is not None:
            self._editing_triggers.append(
                {
                    "id": str(uuid.uuid4()),
                    "entity": self._editing_current_entity,
                    "state": user_input[ATTR_TRIGGER_STATE],
                }
            )
            if user_input.get("add_another", False):
                return await self.async_step_edit_another_trigger()
            return await self.async_step_edit_reset_cycle()

        return self.async_show_form(
            step_id="edit_another_trigger_state",
            data_schema=probatio.Schema(
                {
                    probatio.Required(ATTR_TRIGGER_STATE): _state_selector(
                        self._editing_current_entity
                    ),
                    probatio.Optional("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_reset_cycle(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the reset cycle while editing a counter."""
        if user_input is not None:
            self._editing_reset_cycle = user_input[CONF_RESET_CYCLE]
            return await self.async_step_edit_count_mode()

        return self.async_show_form(
            step_id="edit_reset_cycle",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_RESET_CYCLE, default=self._editing_reset_cycle
                    ): _reset_cycle_selector(),
                }
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_count_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the count mode while editing a counter."""
        if user_input is not None:
            self._editing_count_mode = user_input[CONF_COUNT_MODE]
            if self._editing_count_mode == COUNT_MODE_LIMITED:
                return await self.async_step_edit_max_changes()
            return await self.async_step_edit_additional_options()

        return self.async_show_form(
            step_id="edit_count_mode",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_COUNT_MODE, default=self._editing_count_mode
                    ): _count_mode_selector(),
                }
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_max_changes(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the per-cycle limit while editing a counter."""
        if user_input is not None:
            self._editing_max_changes = max(
                1, int(user_input[CONF_MAX_CHANGES])
            )
            return await self.async_step_edit_additional_options()

        return self.async_show_form(
            step_id="edit_max_changes",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_MAX_CHANGES, default=self._editing_max_changes
                    ): _max_changes_selector(),
                }
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_additional_options(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose optional entities while editing a counter."""
        if user_input is not None:
            self._editing_diagnostic = user_input.get(CONF_DIAGNOSTIC, False)
            self._editing_track_usage_time = user_input.get(
                CONF_TRACK_USAGE_TIME, False
            )
            if self._editing_track_usage_time:
                return await self.async_step_edit_usage_state()
            self._editing_usage_state = ""
            return await self.async_step_edit_finish()

        return self.async_show_form(
            step_id="edit_additional_options",
            data_schema=probatio.Schema(
                {
                    probatio.Optional(
                        CONF_DIAGNOSTIC, default=self._editing_diagnostic
                    ): bool,
                    probatio.Optional(
                        CONF_TRACK_USAGE_TIME,
                        default=self._editing_track_usage_time,
                    ): bool,
                }
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
            },
        )

    async def async_step_edit_usage_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the usage state while editing a counter."""
        if user_input is not None:
            self._editing_usage_state = user_input[CONF_USAGE_STATE]
            return await self.async_step_edit_finish()

        primary_entity = (
            self._editing_triggers[0]["entity"] if self._editing_triggers else ""
        )
        schema_key = (
            probatio.Required(
                CONF_USAGE_STATE,
                default=self._editing_usage_state,
            )
            if self._editing_usage_state
            else probatio.Required(CONF_USAGE_STATE)
        )
        return self.async_show_form(
            step_id="edit_usage_state",
            data_schema=probatio.Schema(
                {schema_key: _state_selector(primary_entity)}
            ),
            description_placeholders={
                "counter_name": self._editing_counter.get("name", ""),
                "entity_id": primary_entity,
            },
        )

    async def async_step_edit_finish(self) -> ConfigFlowResult:
        """Save the edited counter preserving its original id and name."""
        updated_counter: dict[str, Any] = {
            "id": self._editing_counter.get("id", str(uuid.uuid4())),
            "name": self._editing_counter.get("name", ""),
            "triggers": self._editing_triggers,
            "logic": self._editing_logic,
            CONF_RESET_CYCLE: self._editing_reset_cycle,
            CONF_COUNT_MODE: self._editing_count_mode,
            CONF_MAX_CHANGES: self._editing_max_changes,
            CONF_DIAGNOSTIC: self._editing_diagnostic,
            CONF_TRACK_USAGE_TIME: self._editing_track_usage_time,
            CONF_USAGE_STATE: self._editing_usage_state,
        }

        if self._selected_edit_index is not None and 0 <= self._selected_edit_index < len(self._counters):
            self._counters[self._selected_edit_index] = updated_counter

        # Reset editing state
        self._selected_edit_index = None
        self._editing_counter = {}
        self._editing_triggers = []

        return self.async_create_entry(title="", data={"counters": self._counters})

    async def async_step_select_delete(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step to select a counter to delete."""
        if not self._counters:
            return self.async_create_entry(title="", data={"counters": self._counters})

        if user_input is not None:
            self._selected_delete_name = user_input["delete_target"]
            return await self.async_step_confirm_delete()

        return self.async_show_form(
            step_id="select_delete",
            data_schema=probatio.Schema(
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

    async def async_step_confirm_delete(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Confirm and delete the selected counter."""
        if user_input is not None and user_input.get("confirm_delete"):
            self._counters = [c for c in self._counters if c["name"] != self._selected_delete_name]

        return self.async_create_entry(title="", data={"counters": self._counters})

    @callback
    def async_get_options(self) -> dict[str, Any]:
        return {"counters": self._counters}
