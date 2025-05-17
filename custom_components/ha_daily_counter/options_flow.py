from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlow, ConfigEntry
import voluptuous as vol
from typing import Optional, Dict, Any

from .const import CONF_RESET_HOUR, DEFAULT_RESET_HOUR


class HADailyCounterOptionsFlow(OptionsFlow):
    """Handle options for HA Daily Counter."""

    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        existing = self.config_entry.options

        schema = vol.Schema({
            vol.Optional(
                CONF_RESET_HOUR, default=existing.get(CONF_RESET_HOUR, DEFAULT_RESET_HOUR)
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),
        })

        return self.async_show_form(step_id="init", data_schema=schema)
