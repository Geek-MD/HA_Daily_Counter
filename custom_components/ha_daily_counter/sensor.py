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
        self._attr_name = entry.data["entity_id"]
        self._attr_device_class = "counter"
        self._state = 0

        # Store device attributes
        self._device_id = entry.data.get("device_id")
        self._friendly_name = entry.data.get("friendly_name", self._attr_name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes of the entity."""
        return {
            "device_id": self._device_id,
            "friendly_name": self._friendly_name
        }

    def increment(self):
        """Increment the counter value."""
        self._state += 1
        self.schedule_update_ha_state()
