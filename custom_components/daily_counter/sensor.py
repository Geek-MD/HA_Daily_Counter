# custom_components/daily_counter/sensor.py
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "daily_counter"

async def async_setup_entry(hass, entry, async_add_entities):
    """Configurar el sensor desde una entrada de configuración."""
    # Obtener los datos de configuración
    name = entry.data.get("name", "Daily Counter")
    sensor_entity_id = entry.data.get("sensor")

    # Crear la entidad del contador
    async_add_entities([DailyCounterSensor(name, sensor_entity_id)])

class DailyCounterSensor(SensorEntity, RestoreEntity):
    """Representación de un sensor de contador diario."""

    def __init__(self, name, sensor_entity_id):
        """Inicializar el sensor."""
        self._name = name
        self._sensor_entity_id = sensor_entity_id
        self._state = 0

    @property
    def name(self):
        """Nombre del sensor."""
        return self._name

    @property
    def state(self):
        """Estado actual del sensor."""
        return self._state

    async def async_added_to_hass(self):
        """Restaurar el estado al iniciar."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state:
            self._state = int(float(state.state))

        # Escuchar cambios en el sensor asociado
        async_track_state_change(self.hass, self._sensor_entity_id, self._handle_sensor_change)

    async def _handle_sensor_change(self, entity_id, old_state, new_state):
        """Manejar cambios en el sensor."""
        if new_state.state == "on":  # Cambia "on" por el estado que desees detectar
            self._state += 1
            self.schedule_update_ha_state()

    def reset(self):
        """Reiniciar el contador."""
        self._state = 0
        self.schedule_update_ha_state()
