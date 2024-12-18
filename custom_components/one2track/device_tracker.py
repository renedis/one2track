from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .common import DOMAIN
import logging

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    devices = coordinator.data
    async_add_entities([One2TrackTracker(coordinator, device) for device in devices])

class One2TrackTracker(CoordinatorEntity, TrackerEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"one2track_tracker_{device['uuid']}"
        self._attr_name = f"One2Track {device['name']}"
        self._attr_icon = "mdi:map-marker"

    @property
    def latitude(self):
        return float(self._device["last_location"].get("latitude", 0.0))

    @property
    def longitude(self):
        return float(self._device["last_location"].get("longitude", 0.0))

    @property
    def battery_level(self):
        return self._device["last_location"].get("battery_percentage")

    @property
    def extra_state_attributes(self):
        return {
            "bron": "One2Track",
            "battery_level": self._device["last_location"].get("battery_percentage"),
            "breedtegraad": self._device["last_location"].get("latitude"),
            "lengtegraad": self._device["last_location"].get("longitude"),
            "gps_nauwkeurigheid": self._device["last_location"].get("accuracy"),
            "status": self._device.get("status"),
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["name"])},
            "name": f"One2Track {self._device['name']}",
            "manufacturer": "One2Track",
            "model": "GPS Tracker",
            "sw_version": self._device.get("serial_number", "Unknown"),
            "icon": "mdi:watch",
        }
