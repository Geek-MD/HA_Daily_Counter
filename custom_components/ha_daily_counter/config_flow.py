from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import voluptuous as vol
from homeassistant.helpers.selector import selector

from .const import DOMAIN, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

class HADailyCounterConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(ATTR_TRIGGER_ENTITY): selector({
                    "entity": {"multiple": False}
                }),
                vol.Required(ATTR_TRIGGER_STATE): str,
            })
        )

async def async_get_options_flow(config_entry):
    from .options_flow import HADailyCounterOptionsFlow
    return HADailyCounterOptionsFlow(config_entry)
