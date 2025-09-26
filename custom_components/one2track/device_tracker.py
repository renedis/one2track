from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .common import DOMAIN
import logging

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    LOGGER.debug(f"Coordinator data structure: {coordinator.data}")
    devices = coordinator.data
    async_add_entities([One2TrackTracker(coordinator, device) for device in devices], update_before_add=True)


class One2TrackTracker(CoordinatorEntity, TrackerEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"one2track_tracker_{device['uuid']}"
        self._attr_name = f"One2Track {device['name']}"
        self._last_lat = None
        self._last_lon = None
        self._last_address = None

    def _get_device_data(self):
        if isinstance(self.coordinator.data, list):
            for device_data in self.coordinator.data:
                if device_data.get("uuid") == self._device["uuid"]:
                    return device_data
        elif isinstance(self.coordinator.data, dict):
            return self.coordinator.data.get(self._device["uuid"], {})
        return {}

    def _handle_coordinator_update(self) -> None:
        """Only update HA state if relevant location fields changed."""
        device_data = self._get_device_data()
        loc = device_data.get("last_location", {})

        lat = float(loc.get("latitude", 0.0))
        lon = float(loc.get("longitude", 0.0))
        addr = loc.get("address")

        if (
            self._last_lat != lat
            or self._last_lon != lon
            or self._last_address != addr
        ):
            self._last_lat = lat
            self._last_lon = lon
            self._last_address = addr
            super()._handle_coordinator_update()

    @property
    def latitude(self):
        device_data = self._get_device_data()
        return float(device_data.get("last_location", {}).get("latitude", 0.0))

    @property
    def longitude(self):
        device_data = self._get_device_data()
        return float(device_data.get("last_location", {}).get("longitude", 0.0))

    @property
    def battery_level(self):
        device_data = self._get_device_data()
        return device_data.get("last_location", {}).get("battery_percentage")

    @property
    def extra_state_attributes(self):
        device_data = self._get_device_data()
        return {
            "bron": "One2Track",
            "battery_level": device_data.get("last_location", {}).get("battery_percentage"),
            "breedtegraad": device_data.get("last_location", {}).get("latitude"),
            "lengtegraad": device_data.get("last_location", {}).get("longitude"),
            "gps_nauwkeurigheid": device_data.get("last_location", {}).get("accuracy"),
            "serial_number": self._device.get("serial_number"),
            "uuid": self._device.get("uuid"),
            "name": self._device.get("name"),
            "status": self._device.get("status"),
            "phone_number": self._device.get("phone_number"),
            "tariff_type": self._device.get("simcard", {}).get("tariff_type"),
            "balance_cents": self._device.get("simcard", {}).get("balance_cents"),
            "last_communication": device_data.get("last_location", {}).get("last_communication"),
            "last_location_update": device_data.get("last_location", {}).get("last_location_update"),
            "altitude": device_data.get("last_location", {}).get("altitude"),
            "location_type": device_data.get("last_location", {}).get("location_type"),
            "address": device_data.get("last_location", {}).get("address"),
            "signal_strength": device_data.get("last_location", {}).get("signal_strength"),
            "satellite_count": device_data.get("last_location", {}).get("satellite_count"),
            "host": device_data.get("last_location", {}).get("host"),
            "port": device_data.get("last_location", {}).get("port"),
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["name"])},
            "name": f"One2Track {self._device['name']}",
            "manufacturer": "One2Track",
            "model": "GPS watch",
            "sw_version": self._device.get("serial_number", "Unknown"),
        }
