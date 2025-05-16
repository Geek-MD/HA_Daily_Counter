from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import selector
import voluptuous as vol

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DEFAULT_NAME


class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Options flow for HA Daily Counter."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return await self._process_user_input(user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)): str,
                vol.Required(ATTR_TRIGGER_ENTITY, default=self.config_entry.data.get(ATTR_TRIGGER_ENTITY)): selector({
                    "entity": {"multiple": False}
                }),
                vol.Required(ATTR_TRIGGER_STATE, default=self.config_entry.data.get(ATTR_TRIGGER_STATE)): str,
            }),
        )

    async def _process_user_input(self, user_input):
        updated_options = self.config_entry.options.copy()
        updated_options.update(user_input)
        return self.async_create_entry(title="", data=updated_options)
