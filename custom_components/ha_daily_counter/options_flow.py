from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers.selector import selector

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Options flow for managing multiple counters."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        counters = self.config_entry.options.get("counters", [])

        options = {f"{idx}": f"{cfg['name']} ({cfg['trigger_entity']})" for idx, cfg in enumerate(counters)}
        options["add"] = "➕ Add new counter"

        schema = vol.Schema({vol.Required("action"): vol.In(options)})

        return self.async_show_form(step_id="manage", data_schema=schema)

    async def async_step_manage(self, user_input=None):
        if user_input is None:
            return await self.async_step_init()

        action = user_input["action"]

        if action == "add":
            return await self.async_step_edit()

        return await self.async_step_edit(counter_idx=int(action))

    async def async_step_edit(self, user_input=None, counter_idx=None):
        counters = self.config_entry.options.get("counters", [])

        if user_input:
            if counter_idx is not None:
                counters[counter_idx] = user_input
            else:
                counters.append(user_input)

            return self.async_create_entry(title="", data={"counters": counters})

        defaults = counters[counter_idx] if counter_idx is not None and counter_idx < len(counters) else {}

        schema = vol.Schema({
            vol.Required("name", default=defaults.get("name", "")): str,
            vol.Required(ATTR_TRIGGER_ENTITY, default=defaults.get(ATTR_TRIGGER_ENTITY, "")): selector({
                "entity": {"multiple": False}
            }),
            vol.Required(ATTR_TRIGGER_STATE, default=defaults.get(ATTR_TRIGGER_STATE, "")): str,
        })

        return self.async_show_form(step_id="edit", data_schema=schema)
