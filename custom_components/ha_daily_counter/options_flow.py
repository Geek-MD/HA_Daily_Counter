from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers.selector import selector

from .const import DOMAIN, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Options flow for managing counters."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_manage()

    async def async_step_manage(self, user_input=None):
        counters = self.config_entry.options.get("counters", [])

        if user_input is not None:
            counters.append(user_input)
            return self.async_create_entry(title="", data={"counters": counters})

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required(ATTR_TRIGGER_ENTITY): selector({"entity": {"multiple": False}}),
            vol.Required(ATTR_TRIGGER_STATE): str,
        })

        return self.async_show_form(step_id="manage", data_schema=schema)
