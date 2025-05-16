from homeassistant import config_entries
from homeassistant.helpers.selector import selector

from .options_flow import HADailyCounterOptionsFlow

class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain="ha_daily_counter"):
    """Handle a config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="HA Daily Counter", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=config_entries.ConfigFlow.flow_schema({}),
        )

    async def async_get_options_flow(self):
        """Return the options flow handler."""
        return HADailyCounterOptionsFlow(self.config_entry)
