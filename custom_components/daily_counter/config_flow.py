# custom_components/daily_counter/config_flow.py
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

DOMAIN = "daily_counter"

class DailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Manejador del flujo de configuración."""

    async def async_step_user(self, user_input=None):
        """Manejar el flujo de configuración inicial."""
        if user_input is not None:
            # Guardar la configuración
            return self.async_create_entry(title=user_input["name"], data=user_input)

        # Mostrar el formulario de configuración
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): str,  # Campo para el nombre del contador
                    vol.Required("sensor"): str,  # Campo para seleccionar el sensor
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Opciones de configuración."""
        return DailyCounterOptionsFlow(config_entry)

class DailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Manejador de opciones de configuración."""

    def __init__(self, config_entry):
        """Inicializar el flujo de opciones."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manejar las opciones."""
        if user_input is not None:
            # Guardar las opciones
            return self.async_create_entry(title="", data=user_input)

        # Mostrar el formulario de opciones
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("sensor", default=self.config_entry.data.get("sensor")): str,
                }
            ),
        )
