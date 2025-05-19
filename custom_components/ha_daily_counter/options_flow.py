from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
)
from typing import Any, Dict, Optional
import uuid

from .const import DOMAIN


class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Handle the options flow for HA Daily Counter."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self._counters = list(config_entry.options.get("counters", []))
        self._new_counter: Dict[str, Any] = {}

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Initial step: prompt to add a new counter or finish."""
        if user_input is not None:
            if user_input["add_counter"]:
                return await self.async_step_user()
            return self.async_create_entry(title="", data={"counters": self._counters})

        return self.async_show_form(
            step_id="init",
            data_schema={
                "add_counter": bool
            },
            translation_key="init"
        )

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Step to collect the name of the new counter."""
        if user_input is not None:
            self._new_counter["name"] = user_input["name"]
            return await self.async_step_trigger_entity()

        return self.async_show_form(
            step_id="user",
            data_schema={"name": str},
            translation_key="user"
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
            translation_key="trigger_entity"
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
                "trigger_state": SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value="on", label="on"),
                            SelectOptionDict(value="off", label="off"),
                            SelectOptionDict(value="home", label="home"),
                            SelectOptionDict(value="not_home", label="not_home"),
                            SelectOptionDict(value="open", label="open"),
                            SelectOptionDict(value="closed", label="closed"),
                            SelectOptionDict(value="idle", label="idle"),
                            SelectOptionDict(value="playing", label="playing")
                        ],
                        multiple=False,
                        mode="dropdown"
                    )
                )
            },
            translation_key="trigger_state"
        )

    @callback
    def async_get_options(self) -> Dict[str, Any]:
        """Return current options."""
        return {"counters": self._counters}
