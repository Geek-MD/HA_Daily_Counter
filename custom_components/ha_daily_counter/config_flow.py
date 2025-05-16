from __future__ import annotations

from homeassistant import config_entries
from homeassistant.helpers.selector import selector

from .const import DOMAIN

class HADailyCounterConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema={
                "name": selector({"text": {}}),
                "trigger_entity": selector({"entity": {"domain": "binary_sensor"}}),
                "trigger_state": selector({"text": {}}),
            },
        )

    async def async_get_options_flow(self, config_entry):
        from .options_flow import HADailyCounterOptionsFlow
        return HADailyCounterOptionsFlow(config_entry)
