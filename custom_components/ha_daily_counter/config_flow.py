import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.entity_registry import async_get as get_entity_registry
from .const import DOMAIN

# Only allow binary sensors for doors and windows
ALLOWED_DOMAINS = ["binary_sensor"]
ALLOWED_DEVICE_CLASSES = ["door", "window"]

SENSOR_STATES = {
    "binary_sensor": ["on", "off", "open", "close"]
}

class CounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step 1: Select a sensor from allowed domains and device classes."""
        entity_registry = get_entity_registry(self.hass)
        entities = {
            entity.entity_id: entity.original_name or entity.entity_id
            for entity in entity_registry.entities.values()
            if entity.domain in ALLOWED_DOMAINS and entity.device_class in ALLOWED_DEVICE_CLASSES
        }
        
        if user_input is not None:
            self.entity_selected = user_input["entity_id"]
            return await self.async_step_select_state()
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
        """Step 2: Select the state to monitor."""
        states = SENSOR_STATES.get("binary_sensor", ["on", "off"])

        if user_input is not None:
            return self.async_create_entry(title=self.entity_selected, data={
                "entity_id": self.entity_selected,
                "state": user_input["state"]
            })

        return self.async_show_form(
            step_id="select_state",
            data_schema=vol.Schema({
                vol.Required("state", default=states[0]): vol.In(states)
            })
        )
