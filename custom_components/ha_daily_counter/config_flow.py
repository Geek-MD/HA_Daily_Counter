from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers.selector import selector

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DEFAULT_NAME, DOMAIN
from .options_flow import HADailyCounterOptionsFlow

class HADailyCounterConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for HA Daily Counter."""

    VERSION = 1
    DOMAIN = DOMAIN

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default=DEFAULT_NAME): str,
                vol.Required(ATTR_TRIGGER_ENTITY): selector({
                    "entity": {"multiple": False}
                }),
                vol.Required(ATTR_TRIGGER_STATE): str,
            })
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return HADailyCounterOptionsFlow(config_entry)
