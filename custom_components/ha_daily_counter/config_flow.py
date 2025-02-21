import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.device_registry import async_get as get_device_registry
from .const import DOMAIN

class CounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        device_registry = get_device_registry(self.hass)  # ✅ Fixed: Removed 'await'
        devices = {device.id: device.name or "Unnamed Device" for device in device_registry.devices.values()}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default="Daily Counter"): str,
                vol.Required("device_id"): vol.In(devices),
                vol.Required("event_type", default="state_changed"): str
            })
        )
