from homeassistant import config_entries
from .const import DOMAIN

class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Initial step: just create entry."""
        return self.async_create_entry(title="HA Daily Counter", data={})
