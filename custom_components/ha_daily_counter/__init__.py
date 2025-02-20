from homeassistant.core import HomeAssistant, Event
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_change
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    device_id = entry.data.get("device_id")
    event_type = entry.data.get("event_type")

    async def handle_event(event: Event):
        if event.data.get("device_id") == device_id:
            counter.increment()
    
    hass.bus.async_listen(event_type, handle_event)

    return True
