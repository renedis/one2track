from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .common import DOMAIN
import logging

LOGGER = logging.getLogger(__name__)

ICON_MAPPING = {
    "battery_percentage": "mdi:battery",
    "latitude": "mdi:map-marker",
    "longitude": "mdi:map-marker",
    "accuracy": "mdi:crosshairs-gps",
    "altitude": "mdi:altimeter",
    "signal_strength": "mdi:signal",
    "satellite_count": "mdi:satellite-variant",
    "address": "mdi:home-map-marker",
    "location_type": "mdi:map-clock",
    "last_communication": "mdi:clock",
    "last_location_update": "mdi:refresh",
    "phone_number": "mdi:phone",
    "serial_number": "mdi:identifier",
    "uuid": "mdi:identifier",
    "status": "mdi:information",
    "name": "mdi:label",
    "tariff_type": "mdi:sim",
    "balance_cents": "mdi:currency-eur",
    "host": "mdi:server-network",
    "port": "mdi:ethernet"
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    LOGGER.debug(f"Coordinator data structure: {coordinator.data}")
    devices = coordinator.data

    sensors = []
    for device in devices:
        name_prefix = f"{device['name']} watch"
        sensors.extend([
            One2TrackSensor(coordinator, device, "battery_percentage", f"{name_prefix} Battery Level", "%"),
            One2TrackSensor(coordinator, device, "latitude", f"{name_prefix} Latitude", "°"),
            One2TrackSensor(coordinator, device, "longitude", f"{name_prefix} Longitude", "°"),
            One2TrackSensor(coordinator, device, "accuracy", f"{name_prefix} GPS accuracy", "m", fallback=device.get("accuracy")),
            One2TrackSensor(coordinator, device, "altitude", f"{name_prefix} Altitude", "m"),
            One2TrackSensor(coordinator, device, "signal_strength", f"{name_prefix} Signal strength", "dBm"),
            One2TrackSensor(coordinator, device, "satellite_count", f"{name_prefix} Satellite count", None),
            One2TrackSensor(coordinator, device, "address", f"{name_prefix} Address", None),
            One2TrackSensor(coordinator, device, "location_type", f"{name_prefix} Location type", None),
            One2TrackSensor(coordinator, device, "last_communication", f"{name_prefix} Last communication", None),
            One2TrackSensor(coordinator, device, "last_location_update", f"{name_prefix} Last location update", None),
            One2TrackSensor(coordinator, device, "phone_number", f"{name_prefix} Phone number", None, fallback=device.get("phone_number")),
            One2TrackSensor(coordinator, device, "serial_number", f"{name_prefix} Serial number", None, fallback=device.get("serial_number")),
            One2TrackSensor(coordinator, device, "uuid", f"{name_prefix} UUID", None, fallback=device.get("uuid")),
            One2TrackSensor(coordinator, device, "status", f"{name_prefix} Status", None, fallback=device.get("status")),
            One2TrackSensor(coordinator, device, "name", f"{name_prefix} Name", None, fallback=device.get("name")),
            One2TrackSensor(coordinator, device, "tariff_type", f"{name_prefix} SIM type", None, fallback=device["simcard"].get("tariff_type")),
            One2TrackSensor(coordinator, device, "balance_cents", f"{name_prefix} Balance", fallback=device["simcard"].get("balance_cents")),
            One2TrackSensor(coordinator, device, "host", f"{name_prefix} Host", None),
            One2TrackSensor(coordinator, device, "port", f"{name_prefix} Port", None),
        ])
    async_add_entities(sensors, update_before_add=True)

class One2TrackSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device, attribute, name, unit=None, fallback=None):
        super().__init__(coordinator)
        self._device = device
        self._attribute = attribute
        self._attr_name = f"{name}"
        self._attr_unique_id = f"one2track_{device['uuid']}_{attribute}"
        self._attr_unit_of_measurement = unit
        self._fallback = fallback
        self._attr_icon = ICON_MAPPING.get(attribute, "mdi:information-outline")
        self._attr_device_class = self._get_device_class(attribute)

        if self._attr_device_class == "enum":
            if attribute == "location_type":
                self._attr_options = ["WIFI", "GPS"]
            elif attribute == "status":
                self._attr_options = ["WIFI", "GPS"]

        if attribute in ["uuid", "port", "host", "latitude", "longitude", "accuracy", 
                         "tariff_type", "name", "status", "last_communication", 
                         "last_location_update"]:
            self._attr_entity_registry_enabled_default = False

    def _get_device_class(self, attribute):
        device_class_mapping = {
            "battery_percentage": "battery",
            "signal_strength": "signal_strength",
            "last_communication": "timestamp",
            "last_location_update": "timestamp",
            "balance_cents": "monetary",
            "location_type": "enum",
            "status": "enum",
        }
        return device_class_mapping.get(attribute)

    def _get_device_data(self):
        if isinstance(self.coordinator.data, list):
            for device_data in self.coordinator.data:
                if device_data.get("uuid") == self._device["uuid"]:
                    return device_data
        elif isinstance(self.coordinator.data, dict):
            return self.coordinator.data.get(self._device["uuid"], {})
        return {}

    @property
    def state(self):
        device_data = self._get_device_data()
        if self._attribute == "balance_cents":
            balance_cents = device_data.get("simcard", {}).get(self._attribute, 0)
            if balance_cents is not None:
                return round(balance_cents / 100, 2)
            return None
        return device_data.get("last_location", {}).get(self._attribute, self._fallback)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["name"])},
            "name": f"One2Track {self._device['name']}",
            "manufacturer": "One2Track",
            "model": "GPS watch",
            "sw_version": self._device.get("serial_number", "Unknown"),
        }
