from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import selector

from .const import DOMAIN, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle HA Daily Counter config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="HA Daily Counter", data={})

        return self.async_show_form(step_id="user")


class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Handle HA Daily Counter options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Main options step."""
        counters = self.config_entry.options.get("counters", [])

        options = {
            "add": "➕ Add Counter",
            "remove": "➖ Remove Counter",
        }

        if not counters:
            return await self.async_step_add()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required("action"): vol.In(options)}),
        )

    async def async_step_add(self, user_input=None):
        """Add a new counter."""
        if user_input is not None:
            counters = self.config_entry.options.get("counters", [])
            counters.append({
                CONF_NAME: user_input[CONF_NAME],
                ATTR_TRIGGER_ENTITY: user_input[ATTR_TRIGGER_ENTITY],
                ATTR_TRIGGER_STATE: user_input[ATTR_TRIGGER_STATE],
            })
            return self.async_create_entry(title="", data={"counters": counters})

        return self.async_show_form(
            step_id="add",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(ATTR_TRIGGER_ENTITY): selector({
                    "entity": {
                        "multiple": False
                    }
                }),
                vol.Required(ATTR_TRIGGER_STATE): str,
            })
        )

    async def async_step_remove(self, user_input=None):
        """Remove an existing counter."""
        counters = self.config_entry.options.get("counters", [])

        if not counters:
            return self.async_abort(reason="no_counters_to_remove")

        counter_names = [counter.get(CONF_NAME, f"Counter {i+1}") for i, counter in enumerate(counters)]

        if user_input is not None:
            selected = user_input["counter"]
            counters = [c for c in counters if c.get(CONF_NAME) != selected]
            return self.async_create_entry(title="", data={"counters": counters})

        return self.async_show_form(
            step_id="remove",
            data_schema=vol.Schema({
                vol.Required("counter"): vol.In(counter_names)
            })
        )
