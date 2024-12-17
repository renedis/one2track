from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .common import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    devices = coordinator.data

    sensors = []
    for device in devices:
        name_prefix = device["name"]
        sensors.extend([
            One2TrackSensor(coordinator, device, "battery_percentage", f"{name_prefix} Battery Level", "%"),
            One2TrackSensor(coordinator, device, "latitude", f"{name_prefix} Breedtegraad", "°"),
            One2TrackSensor(coordinator, device, "longitude", f"{name_prefix} Lengtegraad", "°"),
            One2TrackSensor(coordinator, device, "accuracy", f"{name_prefix} GPS Nauwkeurigheid", "m"),
            One2TrackSensor(coordinator, device, "altitude", f"{name_prefix} Altitude", "m"),
            One2TrackSensor(coordinator, device, "signal_strength", f"{name_prefix} Signal Strength", "dBm"),
            One2TrackSensor(coordinator, device, "satellite_count", f"{name_prefix} Satellite Count", None),
            One2TrackSensor(coordinator, device, "address", f"{name_prefix} Address", None),
            One2TrackSensor(coordinator, device, "location_type", f"{name_prefix} Location Type", None),
            One2TrackSensor(coordinator, device, "last_communication", f"{name_prefix} Last Communication", None),
            One2TrackSensor(coordinator, device, "last_location_update", f"{name_prefix} Last Location Update", None),
            One2TrackSensor(coordinator, device, "phone_number", f"{name_prefix} Phone Number", None),
            One2TrackSensor(coordinator, device, "serial_number", f"{name_prefix} Serial Number", None),
            One2TrackSensor(coordinator, device, "uuid", f"{name_prefix} UUID", None),
            One2TrackSensor(coordinator, device, "status", f"{name_prefix} Status", None),
            One2TrackSensor(coordinator, device, "name", f"{name_prefix} Name", None),
            One2TrackSensor(coordinator, device, "tariff_type", f"{name_prefix} Tariff Type", None),
            One2TrackSensor(coordinator, device, "balance_cents", f"{name_prefix} Balance Cents", "cents"),
            One2TrackSensor(coordinator, device, "host", f"{name_prefix} Host", None),
            One2TrackSensor(coordinator, device, "port", f"{name_prefix} Port", None),
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
