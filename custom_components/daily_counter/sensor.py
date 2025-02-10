import logging
from homeassistant.helpers.entity import Entity
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change

_LOGGER = logging.getLogger(__name__)

DOMAIN = "daily_counter"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the counter from a config entry."""
    sensor_entity = config_entry.data["sensor_entity"]

    # Crear el contador
    contador = DailyCounter(sensor_entity)
    async_add_entities([contador])

    # Escuchar cambios en el sensor
    async_track_state_change(hass, sensor_entity, contador.async_update_counter)

class DailyCounter(Entity):
    """Representación del contador."""

    def __init__(self, sensor_entity):
        """Inicializar el contador."""
        self._sensor_entity = sensor_entity
        self._state = 0

    @property
    def name(self):
        """Nombre del contador."""
        return "Daily Counter"

    @property
    def state(self):
        """Estado actual del contador."""
        return self._state

    @callback
    def async_update_counter(self, entity, old_state, new_state):
        """Actualizar el contador cuando el sensor cambie."""
        if old_state != new_state:
            self._state += 1
            self.async_write_ha_state()
