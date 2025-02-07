# custom_components/daily_counter/__init__.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "daily_counter"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurar una entrada de configuración."""
    # Inicializar la plataforma "sensor"
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
