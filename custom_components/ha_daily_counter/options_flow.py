from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers.selector import selector

from .const import DOMAIN, ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Options flow to manage multiple counters."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Initial screen: list counters, manage actions."""
        counters = self.config_entry.options.get("counters", [])

        options = {f"{idx}": f"{cfg.get('name')} ({cfg.get('trigger_entity')})" for idx, cfg in enumerate(counters)}
        options["add"] = "➕ Add new counter"

        schema = vol.Schema({
            vol.Required("action"): vol.In(options)
        })

        return self.async_show_form(step_id="manage", data_schema=schema)

    async def async_step_manage(self, user_input=None):
        """Handle manage selection."""
        if user_input is None:
            return await self.async_step_init()

        action = user_input["action"]
        counters = self.config_entry.options.get("counters", [])

        if action == "add":
            return await self.async_step_edit(counter_idx=None)

        # Edit existing counter
        return await self.async_step_edit(counter_idx=int(action))

    async def async_step_edit(self, user_input=None, counter_idx=None):
        """Edit or create a counter."""
        counters = self.config_entry.options.get("counters", [])

        if user_input is not None:
            # Update existing or add new
            if counter_idx is not None and counter_idx < len(counters):
                counters[counter_idx] = user_input
            else:
                counters.append(user_input)

            return self.async_create_entry(title="", data={"counters": counters})

        # Prepare schema with defaults if editing
        defaults = counters[counter_idx] if counter_idx is not None and counter_idx < len(counters) else {}

        schema = vol.Schema({
            vol.Required("name", default=defaults.get("name", "")): str,
            vol.Required(ATTR_TRIGGER_ENTITY, default=defaults.get(ATTR_TRIGGER_ENTITY, "")): selector({
                "entity": {"multiple": False}
            }),
            vol.Required(ATTR_TRIGGER_STATE, default=defaults.get(ATTR_TRIGGER_STATE, "")): str,
        })

        return self.async_show_form(step_id="edit", data_schema=schema)

    async def async_step_delete(self, user_input=None):
        """Delete a counter."""
        counters = self.config_entry.options.get("counters", [])

        options = {f"{idx}": f"{cfg.get('name')} ({cfg.get('trigger_entity')})" for idx, cfg in enumerate(counters)}

        schema = vol.Schema({
            vol.Required("delete_counter"): vol.In(options)
        })

        if user_input is not None:
            idx_to_delete = int(user_input["delete_counter"])
            counters.pop(idx_to_delete)
            return self.async_create_entry(title="", data={"counters": counters})

        return self.async_show_form(step_id="delete", data_schema=schema)
