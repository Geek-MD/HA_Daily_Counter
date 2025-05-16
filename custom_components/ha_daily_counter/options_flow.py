from __future__ import annotations

from homeassistant import config_entries
from homeassistant.helpers.selector import selector

class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Options flow for HA Daily Counter."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            action = user_input["action"]
            if action == "add":
                return await self.async_step_add_counter()
            if action == "remove":
                return await self.async_step_remove_counter()

        return self.async_show_form(
            step_id="init",
            data_schema={
                "action": selector({
                    "select": {
                        "options": ["add", "remove"]
                    }
                })
            }
        )

    async def async_step_add_counter(self, user_input=None):
        if user_input is not None:
            counters = self.config_entry.options.get("counters", [])
            counters.append(user_input)
            return self.async_create_entry(title="Counter Added", data={"counters": counters})

        return self.async_show_form(
            step_id="add_counter",
            data_schema={
                "name": selector({"text": {}}),
                "trigger_entity": selector({"entity": {"domain": "binary_sensor"}}),
                "trigger_state": selector({"text": {}})
            }
        )

    async def async_step_remove_counter(self, user_input=None):
        if user_input is not None:
            counters = self.config_entry.options.get("counters", [])
            counters = [c for c in counters if c.get("name") != user_input["name"]]
            return self.async_create_entry(title="Counter Removed", data={"counters": counters})

        counters = self.config_entry.options.get("counters", [])
        options = [c["name"] for c in counters]

        return self.async_show_form(
            step_id="remove_counter",
            data_schema={
                "name": selector({"select": {"options": options}})
            }
        )
