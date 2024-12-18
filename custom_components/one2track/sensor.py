from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .common import DOMAIN

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
    devices = coordinator.data

    sensors = []
    for device in devices:
        name_prefix = f"{device['name']} watch"
        sensors.extend([
            One2TrackSensor(coordinator, device, "battery_percentage", f"{name_prefix} Battery Level", "%", "battery"),
            One2TrackSensor(coordinator, device, "latitude", f"{name_prefix} Latitude", "°"),
            One2TrackSensor(coordinator, device, "longitude", f"{name_prefix} Longitude", "°"),
            One2TrackSensor(coordinator, device, "accuracy", f"{name_prefix} GPS accuracy", "m", fallback=device.get("accuracy")),
            One2TrackSensor(coordinator, device, "altitude", f"{name_prefix} Altitude", "m"),
            One2TrackSensor(coordinator, device, "signal_strength", f"{name_prefix} Signal strength", "dBm", "signal_strength"),
            One2TrackSensor(coordinator, device, "satellite_count", f"{name_prefix} Satellite count", None),
            One2TrackSensor(coordinator, device, "address", f"{name_prefix} Address", None),
            One2TrackSensor(coordinator, device, "location_type", f"{name_prefix} Location type", None),
            One2TrackSensor(coordinator, device, "last_communication", f"{name_prefix} Last communication", None, "timestamp"),
            One2TrackSensor(coordinator, device, "last_location_update", f"{name_prefix} Last location update", None, "timestamp"),
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
    async_add_entities(sensors)

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

        if attribute == "balance_cents":
            self._attr_device_class = "valuta"

        if attribute in ["uuid", "port", "host", "latitude", "longitude", "accuracy", "tariff_type", "name", "status", "last_communication", "last_location_update"]:
            self._attr_entity_registry_enabled_default = False

    @property
    def state(self):
        return self._device["last_location"].get(self._attribute, self._fallback)

    @property
    def state(self):
        if self._attribute == "balance_cents":
            balance_cents = self._device.get("simcard", {}).get(self._attribute, 0)
            if balance_cents is not None:
                return round(balance_cents / 100, 2)
            return None
        return self._device.get("last_location", {}).get(self._attribute, self._fallback)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["name"])},
            "name": f"One2Track {self._device['name']}",
            "manufacturer": "One2Track",
            "model": "GPS Tracker",
            "sw_version": self._device.get("serial_number", "Unknown"),
        }
