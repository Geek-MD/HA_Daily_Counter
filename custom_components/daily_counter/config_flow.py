import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_SENSORS

class DailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Daily Counter."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validar que el nombre no esté duplicado
            await self.async_set_unique_id(user_input[CONF_NAME])
            self._abort_if_unique_id_configured()

            # Validar que todos los sensores existan
            invalid_sensors = [
                sensor for sensor in user_input[CONF_SENSORS]
                if not self.hass.states.get(sensor)
            ]
            if invalid_sensors:
                errors["base"] = "invalid_sensors"
            else:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        # Mostrar el formulario en la UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_SENSORS): vol.All(  # Aceptar una lista de sensores
                    cv.ensure_list,
                    [str]
                ),
            }),
            errors=errors,
            description_placeholders={
                "sensor_example": "binary_sensor.puerta_principal"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DailyCounterOptionsFlow(config_entry)

class DailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Daily Counter."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_SENSORS, default=self.config_entry.data[CONF_SENSORS]): vol.All(
                    cv.ensure_list,
                    [str]
                ),
            }),
        )
