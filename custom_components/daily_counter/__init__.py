import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "daily_counter"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Daily Counter integration."""
    _LOGGER.info("Daily Counter está siendo configurado")
    return True
