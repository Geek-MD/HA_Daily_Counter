from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import voluptuous as vol
from homeassistant.helpers.selector import selector
from homeassistant.core import callback

from .const import DOMAIN, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DEFAULT_NAME
from .options_flow import HADailyCounterOptionsFlowHandler


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(ATTR_TRIGGER_ENTITY): selector({
                    "entity": {"multiple": False}
                }),
                vol.Required(ATTR_TRIGGER_STATE): str,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return HADailyCounterOptionsFlowHandler(config_entry)
