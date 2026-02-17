import uuid
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow for HA Daily Counter."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self._counters = list(config_entry.options.get("counters", []))
        self._new_counter: Dict[str, Any] = {}
        self._selected_delete_name: Optional[str] = None
        self._selected_edit_index: Optional[int] = None
        self._editing_counter: Dict[str, Any] = {}

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Initial step: add, edit, or delete a counter."""
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
            data_schema={
                "action": SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value="add", label="Add counter"),
                            SelectOptionDict(value="edit", label="Edit counter"),
                            SelectOptionDict(value="delete", label="Delete counter"),
                            SelectOptionDict(value="finish", label="Finish setup")
                        ],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            },
        )

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to collect the name of the new counter."""
        if user_input is not None:
            self._new_counter["name"] = user_input["name"]
            return await self.async_step_trigger_entity()

        return self.async_show_form(
            step_id="user",
            data_schema={"name": str},
        )

    async def async_step_trigger_entity(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to collect the entity that triggers the counter."""
        if user_input is not None:
            self._new_counter["trigger_entity"] = user_input["trigger_entity"]
            return await self.async_step_trigger_state()

        return self.async_show_form(
            step_id="trigger_entity",
            data_schema={
                "trigger_entity": EntitySelector(EntitySelectorConfig())
            },
        )

    async def async_step_trigger_state(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to collect the trigger state."""
        if user_input is not None:
            self._new_counter["trigger_state"] = user_input["trigger_state"]
            self._new_counter["id"] = str(uuid.uuid4())
            self._counters.append(self._new_counter)

            return await self.async_step_init()

        return self.async_show_form(
            step_id="trigger_state",
            data_schema={
                "trigger_state": str
            },
        )

    async def async_step_select_edit(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to select a counter to edit."""
        if not self._counters:
            return await self.async_step_init()

        if user_input is not None:
            selected_name = user_input["edit_target"]
            # Find the counter index by name
            for idx, counter in enumerate(self._counters):
                if counter["name"] == selected_name:
                    self._selected_edit_index = idx
                    self._editing_counter = dict(counter)
                    return await self.async_step_edit_trigger_entity()
            # If not found, go back to init
            return await self.async_step_init()

        return self.async_show_form(
            step_id="select_edit",
            data_schema={
                "edit_target": SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=c["name"], label=c["name"])
                            for c in self._counters
                        ],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            },
        )

    async def async_step_edit_trigger_entity(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to edit the trigger entity."""
        if user_input is not None:
            self._editing_counter["trigger_entity"] = user_input["trigger_entity"]
            return await self.async_step_edit_trigger_state()

        # Get current trigger entity value
        current_entity = self._editing_counter.get("trigger_entity", "")

        return self.async_show_form(
            step_id="edit_trigger_entity",
            data_schema={
                "trigger_entity": EntitySelector(
                    EntitySelectorConfig()
                )
            },
            description_placeholders={
                "current_value": current_entity,
                "counter_name": self._editing_counter.get("name", "")
            }
        )

    async def async_step_edit_trigger_state(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to edit the trigger state."""
        if user_input is not None:
            self._editing_counter["trigger_state"] = user_input["trigger_state"]
            # Update the counter in the list
            if self._selected_edit_index is not None and 0 <= self._selected_edit_index < len(self._counters):
                self._counters[self._selected_edit_index] = self._editing_counter
            
            # Reset editing state
            self._selected_edit_index = None
            self._editing_counter = {}
            
            return await self.async_step_init()

        # Get current trigger state value
        current_state = self._editing_counter.get("trigger_state", "")

        return self.async_show_form(
            step_id="edit_trigger_state",
            data_schema={
                "trigger_state": str
            },
            description_placeholders={
                "current_value": current_state,
                "counter_name": self._editing_counter.get("name", "")
            }
        )

    async def async_step_select_delete(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to select a counter to delete."""
        if not self._counters:
            return await self.async_step_init()

        if user_input is not None:
            self._selected_delete_name = user_input["delete_target"]
            return await self.async_step_confirm_delete()

        return self.async_show_form(
            step_id="select_delete",
            data_schema={
                "delete_target": SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=c["name"], label=c["name"])
                            for c in self._counters
                        ],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            },
        )

    async def async_step_confirm_delete(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Confirm and delete the selected counter."""
        if user_input is not None and user_input.get("confirm_delete"):
            self._counters = [c for c in self._counters if c["name"] != self._selected_delete_name]

        return await self.async_step_init()

    def _confirm_delete_schema(self) -> dict:
        return {
            "confirm_delete": bool
        }

    @callback
    def async_get_options(self) -> Dict[str, Any]:
        return {"counters": self._counters}
