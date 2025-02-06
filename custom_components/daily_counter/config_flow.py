# custom_components/custom_counter/config_flow.py
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

DATA_SCHEMA = vol.Schema({
    vol.Required("name"): str,
    vol.Required("sensor"): selector.EntitySelector(),
})

class CustomCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Manejador del flujo de configuración."""

    async def async_step_user(self, user_input=None):
        """Manejar el flujo de configuración inicial."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Opciones de configuración."""
        return CustomCounterOptionsFlow(config_entry)

class CustomCounterOptionsFlow(config_entries.OptionsFlow):
    """Manejador de opciones de configuración."""

    def __init__(self, config_entry):
        """Inicializar el flujo de opciones."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manejar las opciones."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("sensor", default=self.config_entry.data["sensor"]): selector.EntitySelector(),
            }),
        )
