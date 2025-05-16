from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Options flow for HA Daily Counter."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return await self.async_step_manage(user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action", default="add"): vol.In(["add", "remove"]),
            }),
        )

    async def async_step_manage(self, user_input):
        action = user_input["action"]

        if action == "add":
            return await self.async_step_add()
        if action == "remove":
            return await self.async_step_remove()

        return self.async_abort(reason="unknown_action")

    async def async_step_add(self, user_input=None):
        if user_input is not None:
            counters = self.config_entry.options.get("counters", [])
            counters.append({
                "name": user_input["name"],
                "trigger_entity": user_input["trigger_entity"],
                "trigger_state": user_input["trigger_state"],
            })

            return self.async_create_entry(title="", data={"counters": counters})

        return self.async_show_form(
            step_id="add",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("trigger_entity"): selector({"entity": {}}),
                vol.Required("trigger_state"): str,
            }),
        )

    async def async_step_remove(self, user_input=None):
        counters = self.config_entry.options.get("counters", [])

        if user_input is not None:
            counters = [c for c in counters if c["name"] != user_input["name"]]
            return self.async_create_entry(title="", data={"counters": counters})

        if not counters:
            return self.async_abort(reason="no_counters_to_remove")

        return self.async_show_form(
            step_id="remove",
            data_schema=vol.Schema({
                vol.Required("name"): vol.In([c["name"] for c in counters]),
            }),
        )
