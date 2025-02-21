from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_component import async_get_entity_platform
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up HA Daily Counter from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    platform = async_get_entity_platform(hass, "sensor", DOMAIN)
    await platform.async_add_entities([DailyCounterSensor(hass, entry)])
    return True
