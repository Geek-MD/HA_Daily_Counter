from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from typing import Optional, Dict, Any

from .options_flow import HADailyCounterOptionsFlow


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain="ha_daily_counter"):
    """Configuration flow for the HA Daily Counter integration."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step of the user configuration flow."""
        return self.async_create_entry(title="HA Daily Counter", data={})

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> HADailyCounterOptionsFlow:
        """Return the options flow handler for the config entry."""
        return HADailyCounterOptionsFlow(config_entry)
