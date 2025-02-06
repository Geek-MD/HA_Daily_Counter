import logging
from datetime import datetime, timedelta
import asyncio
import voluptuous as vol
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change, async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

CONF_SENSORS = "sensors"
CONF_TRIGGER_SENSOR = "trigger_sensor"
CONF_NAME = "name"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SENSORS): vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_NAME): cv.string,
                        vol.Required(CONF_TRIGGER_SENSOR): cv.entity_id,
                    }
                )
            ],
        )
    }
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    sensors = []
    for sensor_config in entry.data[CONF_SENSORS]:
        name = sensor_config[CONF_NAME]
        trigger_sensor = sensor_config[CONF_TRIGGER_SENSOR]
        sensor = DailyCounterSensor(hass, name, trigger_sensor)
        sensors.append(sensor)
    
    async_add_entities(sensors, True)

class DailyCounterSensor(RestoreEntity):
    def __init__(self, hass: HomeAssistant, name: str, trigger_sensor: str):
        self._hass = hass
        self._name = name
        self._trigger_sensor = trigger_sensor
        self._state = 0
        self._reset_time = datetime.combine(datetime.today() + timedelta(days=1), datetime.min.time())

    async def async_added_to_hass(self):
        last_state = await self.async_get_last_state()
        if last_state and last_state.state.isdigit():
            self._state = int(last_state.state)
        
        async_track_state_change(self._hass, self._trigger_sensor, self._increment_counter)
        async_track_time_change(self._hass, self._reset_counter, hour=0, minute=0, second=0)

    @callback
    def _increment_counter(self, entity_id, old_state, new_state):
        if old_state and new_state and old_state.state != new_state.state:
            self._state += 1
            self.async_write_ha_state()
    
    @callback
    def _reset_counter(self, time):
        self._state = 0
        self.async_write_ha_state()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"daily_counter_{self._name.lower().replace(' ', '_')}"
