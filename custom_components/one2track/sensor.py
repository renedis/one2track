from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .common import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    devices = coordinator.data

    sensors = []
    for device in devices:
        sensors.extend([
            One2TrackSensor(coordinator, device, "battery_percentage", "Battery Level", "%"),
            One2TrackSensor(coordinator, device, "latitude", "Breedtegraad", "°"),
            One2TrackSensor(coordinator, device, "longitude", "Lengtegraad", "°"),
            One2TrackSensor(coordinator, device, "accuracy", "GPS Nauwkeurigheid", "m"),
            One2TrackSensor(coordinator, device, "altitude", "Altitude", "m"),
            One2TrackSensor(coordinator, device, "signal_strength", "Signal Strength", "dBm"),
            One2TrackSensor(coordinator, device, "satellite_count", "Satellite Count", None),
            One2TrackSensor(coordinator, device, "address", "Address", None),
            One2TrackSensor(coordinator, device, "location_type", "Location Type", None),
            One2TrackSensor(coordinator, device, "last_communication", "Last Communication", None),
            One2TrackSensor(coordinator, device, "last_location_update", "Last Location Update", None),
            One2TrackSensor(coordinator, device, "phone_number", "Phone Number", None),
            One2TrackSensor(coordinator, device, "serial_number", "Serial Number", None),
            One2TrackSensor(coordinator, device, "uuid", "UUID", None),
            One2TrackSensor(coordinator, device, "status", "Status", None),
            One2TrackSensor(coordinator, device, "name", "Name", None),
            One2TrackSensor(coordinator, device, "tariff_type", "Tariff Type", None),
            One2TrackSensor(coordinator, device, "balance_cents", "Balance Cents", "cents"),
            One2TrackSensor(coordinator, device, "host", "Host", None),
            One2TrackSensor(coordinator, device, "port", "Port", None),
        ])
    async_add_entities(sensors)

class One2TrackSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device, attribute, name, unit=None):
        super().__init__(coordinator)
        self._device = device
        self._attribute = attribute
        self._attr_name = f"{name}"
        self._attr_unique_id = f"one2track_{device['uuid']}_{attribute}"
        self._attr_unit_of_measurement = unit

    @property
    def state(self):
        return self._device["last_location"].get(self._attribute)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["name"])},
            "name": f"One2Track {self._device['name']}",
            "manufacturer": "One2Track",
            "model": "GPS Tracker",
            "sw_version": self._device.get("serial_number", "Unknown"),
        }
