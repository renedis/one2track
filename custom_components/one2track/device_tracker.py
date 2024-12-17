from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .common import DOMAIN
import logging

LOGGER = logging.getLogger(__name__)

class One2TrackTracker(CoordinatorEntity, TrackerEntity):
    """Primary One2Track Tracker Entity."""

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"one2track_tracker_{device['uuid']}"
        self._attr_name = f"One2Track {device['name']}"

    @property
    def latitude(self):
        return self._device["last_location"]["latitude"]

    @property
    def longitude(self):
        return self._device["last_location"]["longitude"]

    @property
    def battery_level(self):
        return self._device["last_location"]["battery_percentage"]

    @property
    def extra_state_attributes(self):
        """Return only key attributes."""
        return {
            "status": self._device["status"],
            "signal_strength": self._device["last_location"]["signal_strength"],
            "altitude": self._device["last_location"]["altitude"],
        }
