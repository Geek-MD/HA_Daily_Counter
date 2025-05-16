from homeassistant import config_entries

from .options_flow import HADailyCounterOptionsFlow
from .const import DOMAIN

class HADailyCounterConfigFlow(config_entries.ConfigFlow):
    """Config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        return self.async_create_entry(title="HA Daily Counter", data={})

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow handler."""
        return HADailyCounterOptionsFlow(config_entry)
