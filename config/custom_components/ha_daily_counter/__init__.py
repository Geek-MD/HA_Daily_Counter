import logging
import asyncio
from homeassistant.core import HomeAssistant, Event
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.storage import Store
from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION
from .counter import DailyCounter

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configurar la integración desde la UI."""
    hass.data.setdefault(DOMAIN, {})

    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    data = await store.async_load() or {}

    counter_name = entry.data["name"]
    event_type = entry.data["event_type"]
    entity_id = entry.data["entity_id"]

    counter = DailyCounter(hass, counter_name, data.get(counter_name, 0))
    hass.data[DOMAIN][entry.entry_id] = {"counter": counter, "store": store}

    async def handle_event(event: Event):
        """Incrementar el contador cuando se detecte el evento configurado."""
        if event.event_type == event_type and entity_id in event.data.get("entity_id", ""):
            counter.increment()
            await store.async_save({counter_name: counter.value})
            _LOGGER.info(f"Contador '{counter_name}' incrementado por evento '{event_type}'.")

    hass.bus.async_listen(event_type, handle_event)

    async def reset_counters(event_time):
        """Restablece el contador a las 00:00."""
        counter.reset()
        await store.async_save({counter_name: counter.value})
        _LOGGER.info(f"Contador '{counter_name}' reiniciado a las 00:00.")

    async_track_time_change(hass, reset_counters, hour=0, minute=0, second=0)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Desinstalar la integración."""
    hass.bus.async_remove_listener(entry.data["event_type"], hass.data[DOMAIN][entry.entry_id]["listener"])
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
