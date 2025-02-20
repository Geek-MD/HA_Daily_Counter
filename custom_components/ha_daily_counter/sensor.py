from homeassistant.helpers.entity import Entity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the counter sensor."""
    sensor = DailyCounterSensor(hass, entry)
    async_add_entities([sensor], update_before_add=True)

class DailyCounterSensor(Entity):
    """Representation of a daily counter sensor."""

    def __init__(self, hass, entry):
        """Initialize the counter sensor."""
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = entry.data["name"]
        self._attr_device_class = "counter"
        self._state = 0

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self):
        """Return device information for this sensor."""
        return {
            "identifiers": {(DOMAIN, self._entry.data["device_id"])},
            "name": self._entry.data["name"],
            "manufacturer": "HA Daily Counter",
            "model": "Virtual Counter"
        }

    def increment(self):
        """Increment the counter value."""
        self._state += 1
        self.schedule_update_ha_state()
