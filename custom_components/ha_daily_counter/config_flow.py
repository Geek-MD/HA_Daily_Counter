import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.entity_registry import async_get as get_entity_registry
from .const import DOMAIN

ENTITY_DOMAINS = {
    "binary_sensor": ["on", "off", "open", "close"],
    "light": ["on", "off"],
    "sensor": []
}

class CounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.domain_selected = user_input["entity_domain"]
            return await self.async_step_select_entity()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("entity_domain", default="binary_sensor"): vol.In(ENTITY_DOMAINS.keys())
            })
        )

    async def async_step_select_entity(self, user_input=None):
        entity_registry = get_entity_registry(self.hass)
        entities = {
            entity.entity_id: entity.original_name or entity.entity_id
            for entity in entity_registry.entities.values()
            if entity.entity_id.startswith(self.domain_selected)
        }

        if user_input is not None:
            self.entity_selected = user_input["entity_id"]
            return await self.async_step_select_state()

        return self.async_show_form(
            step_id="select_entity",
            data_schema=vol.Schema({
                vol.Required("entity_id"): vol.In(entities)
            })
        )

    async def async_step_select_state(self, user_input=None):
        states = ENTITY_DOMAINS.get(self.domain_selected, ["on", "off"])

        if user_input is not None:
            return self.async_create_entry(title=self.entity_selected, data={
                "entity_domain": self.domain_selected,
                "entity_id": self.entity_selected,
                "state": user_input["state"]
            })

        return self.async_show_form(
            step_id="select_state",
            data_schema=vol.Schema({
                vol.Required("state", default=states[0]): vol.In(states)
            })
        )
