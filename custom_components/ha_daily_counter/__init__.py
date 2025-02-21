from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_registry import async_get as get_entity_registry
from homeassistant.helpers.device_registry import async_get as get_device_registry
from .const import DOMAIN
from .sensor import DailyCounterSensor

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup the integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get device and entity registries
    device_registry = get_device_registry(hass)
    entity_registry = get_entity_registry(hass)

    # Create or get the device
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data["device_id"])},
        name=entry.data["name"],
        manufacturer="HA Daily Counter",
        model="Virtual Counter"
    )

    # Ensure the entity is created and assigned to the device
    entity_id = entity_registry.async_get_or_create(
        domain="sensor",
        platform=DOMAIN,
        unique_id=entry.entry_id,
        suggested_object_id=f"counter_{entry.data['name'].lower().replace(' ', '_')}",
        config_entry=entry,
        device_id=device.id
    )

    # Register the sensor entity
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True
