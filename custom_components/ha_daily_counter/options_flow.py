from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import voluptuous as vol
from homeassistant.helpers.selector import selector

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE

class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Options flow for HA Daily Counter."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            if user_input["action"] == "add":
                return await self.async_step_add_counter()
            if user_input["action"] == "remove":
                return await self.async_step_remove_counter()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action", default="add"): vol.In(["add", "remove"]),
            }),
            description_placeholders={"name": self.config_entry.title},
        )

    async def async_step_add_counter(self, user_input=None):
        if user_input is not None:
            counters = self.config_entry.options.get("counters", [])
            counters.append({
                CONF_NAME: user_input[CONF_NAME],
                ATTR_TRIGGER_ENTITY: user_input[ATTR_TRIGGER_ENTITY],
                ATTR_TRIGGER_STATE: user_input[ATTR_TRIGGER_STATE],
            })

            return self.async_create_entry(title="", data={"counters": counters})

        return self.async_show_form(
            step_id="add_counter",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(ATTR_TRIGGER_ENTITY): selector({
                    "entity": {"multiple": False}
                }),
                vol.Required(ATTR_TRIGGER_STATE): str,
            }),
        )

    async def async_step_remove_counter(self, user_input=None):
        counters = self.config_entry.options.get("counters", [])

        if not counters:
            return self.async_abort(reason="no_counters")

        counter_names = [c[CONF_NAME] for c in counters]

        if user_input is not None:
            counters = [c for c in counters if c[CONF_NAME] != user_input["counter_to_remove"]]
            return self.async_create_entry(title="", data={"counters": counters})

        return self.async_show_form(
            step_id="remove_counter",
            data_schema=vol.Schema({
                vol.Required("counter_to_remove"): vol.In(counter_names),
            }),
        )
