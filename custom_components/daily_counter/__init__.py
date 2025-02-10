import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN

class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Daily Counter."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validar la entrada del usuario
            sensor_entity = user_input["sensor_entity"]
            if sensor_entity:
                return self.async_create_entry(title="Daily Counter", data=user_input)
            else:
                errors["base"] = "sensor_required"

        # Mostrar el formulario de configuración
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("sensor_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                )
            }),
            errors=errors,
        )
