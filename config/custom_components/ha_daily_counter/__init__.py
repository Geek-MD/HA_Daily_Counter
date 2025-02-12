import logging
import asyncio
from datetime import datetime, time, timedelta
from homeassistant.core import HomeAssistant
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

    counters = {
        name: DailyCounter(hass, name, data.get(name, 0))
        for name in entry.data.get("counters", [])
    }

    hass.data[DOMAIN] = {"counters": counters, "store": store}

    async def reset_counters(event_time):
        """Restablece los contadores a las 00:00."""
        for counter in counters.values():
            counter.reset()
        await store.async_save({name: counter.value for name, counter in counters.items()})
        _LOGGER.info("Contadores reiniciados a las 00:00")

    async_track_time_change(hass, reset_counters, hour=0, minute=0, second=0)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Desinstalar la integración."""
    if DOMAIN in hass.data:
        hass.data.pop(DOMAIN)
    return True
