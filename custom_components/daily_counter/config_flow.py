import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.selector import selector

from .const import DOMAIN, CONF_NAME, CONF_TRIGGER_SENSOR

class DailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        hass: HomeAssistant = self.hass
        entity_registry = async_get_entity_registry(hass)
        
        sensor_options = {
            entity.entity_id: entity.original_name or entity.entity_id
            for entity in entity_registry.entities.values()
            if entity.entity_id.startswith("binary_sensor.") or entity.entity_id.startswith("sensor.")
        }
        
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_TRIGGER_SENSOR): selector({
                        "select": {
                            "options": [
                                {"value": eid, "label": name} for eid, name in sensor_options.items()
                            ],
                            "mode": "dropdown"
                        }
                    })
                }
            ),
            errors=errors,
        )
