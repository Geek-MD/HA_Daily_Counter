import logging
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.util import dt as dt_util
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN, CONF_NAME, CONF_SENSORS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Daily Counter sensor from a config entry."""
    name = config_entry.data[CONF_NAME]
    sensor_ids = config_entry.data[CONF_SENSORS]  # Lista de sensores
    unique_id = f"daily_counter_{name.lower().replace(' ', '_')}"
    async_add_entities([DailyCounterSensor(hass, name, sensor_ids, unique_id)])

class DailyCounterSensor(RestoreEntity):
    """Representation of a Daily Counter sensor."""

    def __init__(self, hass, name, sensor_ids, unique_id):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._sensor_ids = sensor_ids  # Lista de sensores
        self._unique_id = unique_id
        self._state = 0
        self._last_reset = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._unique_id

    async def async_added_to_hass(self):
        """Restore state and set up listeners."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state:
            self._state = int(state.state)
            self._last_reset = dt_util.parse_datetime(state.attributes.get("last_reset"))

        # Configurar listeners para todos los sensores
        for sensor_id in self._sensor_ids:
            async_track_state_change(self._hass, sensor_id, self._sensor_changed)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "last_reset": self._last_reset.isoformat(),
            "sensors": self._sensor_ids  # Mostrar la lista de sensores en los atributos
        }

    async def _sensor_changed(self, entity_id, old_state, new_state):
        """Handle sensor state changes."""
        if new_state.state == "on":  # Cambia "on" por el estado que desees detectar
            await self._increment_counter()

    async def _increment_counter(self):
        """Increment the counter."""
        now = dt_util.now()
        if now.date() != self._last_reset.date():
            self._state = 0
            self._last_reset = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self._state += 1
        self.async_write_ha_state()
