import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class CounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flujo de configuración de HA Daily Counter."""

    async def async_step_user(self, user_input=None):
        """Paso de configuración inicial."""
        if user_input is not None:
            return self.async_create_entry(title="HA Daily Counter", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("counters", default=[]): vol.All(vol.Length(min=1), [str])
            })
        )
