from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from typing import Any, Dict, Optional

from .options_flow import HADailyCounterOptionsFlow
from .const import DOMAIN


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Initial step: just create an empty entry, all configuration goes to options."""
        return self.async_create_entry(
            title="HA Daily Counter",
            data={},
            options={"counters": []},
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> HADailyCounterOptionsFlow:
        """Return the custom options flow handler."""
        return HADailyCounterOptionsFlow(config_entry)
