from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import voluptuous as vol
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    ATTR_TRIGGER_ENTITY,
    ATTR_TRIGGER_STATE,
    DEFAULT_NAME,
)

class HADailyCounterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options or self.config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=current.get(CONF_NAME, DEFAULT_NAME)): str,
                vol.Required(ATTR_TRIGGER_ENTITY, default=current.get(ATTR_TRIGGER_ENTITY)): selector({
                    "entity": {"multiple": False}
                }),
                vol.Required(ATTR_TRIGGER_STATE, default=current.get(ATTR_TRIGGER_STATE)): str,
            })
        )
