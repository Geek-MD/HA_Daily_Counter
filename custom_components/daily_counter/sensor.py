import logging
from datetime import timedelta, datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

DOMAIN = "custom_counter"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the custom counter platform."""
    sensors = []

    # Crear una entidad de tipo contador
    counter = CustomCounter(hass, "custom_counter_1", "Custom Counter 1")
    sensors.append(counter)

    async_add_entities(sensors)

    # Reiniciar el contador a las 00:00
    async def reset_counter_at_midnight(now):
        counter.reset()

    hass.helpers.event.async_track_time_change(reset_counter_at_midnight, hour=0, minute=0, second=0)

class CustomCounter(SensorEntity, RestoreEntity):
    """Representación de un contador personalizado."""

    def __init__(self, hass, unique_id, name):
        """Inicializar el contador."""
        self._hass = hass
        self._unique_id = unique_id
        self._name = name
        self._state = 0
        self._sensor_entity_id = None

    @property
    def name(self):
        """Nombre del contador."""
        return self._name

    @property
    def state(self):
        """Estado actual del contador."""
        return self._state

    @property
    def unique_id(self):
        """ID único del contador."""
        return self._unique_id

    def increment(self):
        """Incrementar el contador."""
        self._state += 1
        self.schedule_update_ha_state()

    def reset(self):
        """Reiniciar el contador."""
        self._state = 0
        self.schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Ejecutar cuando la entidad es añadida a Home Assistant."""
        await super().async_added_to_hass()

        # Restaurar el estado guardado
        state = await self.async_get_last_state()
        if state:
            self._state = int(float(state.state))  # Convertir el estado a entero

        # Configurar el seguimiento del sensor
        if self._sensor_entity_id:
            async_track_state_change(self._hass, self._sensor_entity_id, self._handle_sensor_change)

    async def _handle_sensor_change(self, entity_id, old_state, new_state):
        """Manejar cambios en el sensor."""
        if new_state.state == "on":  # Cambia "on" por el estado que desees detectar
            self.increment()
