from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import (
    EntitySelector, EntitySelectorConfig,
    TextSelector, TextSelectorConfig,
    BooleanSelector, BooleanSelectorConfig,
)
from homeassistant.data_entry_flow import FlowResult
from typing import Any

from .const import DOMAIN
from .options_flow import HADailyCounterOptionsFlow  # si lo usas

STEP_TRIGGER = "trigger"
STEP_ANOTHER = "another"

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HA Daily Counter with multiple triggers."""

    VERSION = 1

    def __init__(self) -> None:
        self._name: str = ""
        self._triggers: list[dict[str, str]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 1: Ask for counter name."""
        if user_input:
            self._name = user_input[CONF_NAME]
            return await self.async_step_trigger(user_input=None)

        return self.async_show_form(
            step_id="user",
            data_schema=config_entries.vol.Schema({
                config_entries.vol.Required(CONF_NAME): str
            }),
        )

    async def async_step_trigger(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 2+: Ask for one trigger (entity + state)."""
        if user_input:
            self._triggers.append({
                "entity": user_input["trigger_entity"],
                "state": user_input["trigger_state"],
            })
            return await self.async_step_another()

        return self.async_show_form(
            step_id=STEP_TRIGGER,
            data_schema=config_entries.vol.Schema({
                config_entries.vol.Required("trigger_entity"): EntitySelector(
                    EntitySelectorConfig()
                ),
                config_entries.vol.Required("trigger_state"): TextSelector(
                    TextSelectorConfig(type="text")
                ),
            }),
            description_placeholders={"count": str(len(self._triggers) + 1)},
        )

    async def async_step_another(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 3: Ask if we add another trigger or finish."""
        if user_input:
            if user_input["add_another"]:
                return await self.async_step_trigger(user_input=None)
            # Finish: create entry
            counter = {
                "id": self._name.replace(" ", "_").lower(),
                "name": self._name,
                "triggers": self._triggers,
            }
            return self.async_create_entry(
                title=self._name,
                data={},
                options={"counters": [counter]},
            )

        return self.async_show_form(
            step_id=STEP_ANOTHER,
            data_schema=config_entries.vol.Schema({
                config_entries.vol.Required("add_another", default=True): BooleanSelector(
                    BooleanSelectorConfig()
                )
            }),
            description_placeholders={"count": str(len(self._triggers))},
        )

    @staticmethod
    def async_get_options_flow(entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Si manejas edición en options_flow."""
        return HADailyCounterOptionsFlow(entry)
