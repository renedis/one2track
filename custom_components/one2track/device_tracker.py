import logging
from datetime import timedelta
from typing import List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import async_timeout
from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from .client import GpsClient, TrackerDevice
from .common import DOMAIN, DEFAULT_UPDATE_RATE_SEC

LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Add an entry."""
    LOGGER.debug("one2track async_setup_entry")

    gps_api: GpsClient = hass.data[DOMAIN][entry.entry_id]['api_client']
    devices: List[TrackerDevice] = await gps_api.update()

    coordinator = GpsCoordinator(hass, gps_api, True)

    LOGGER.info("Adding %s found one2track devices", len(devices))

    for device in devices:
        LOGGER.debug("Adding %s", device)
        async_add_entities(
            [
                One2TrackDeviceTracker(
                    coordinator,
                    hass,
                    entry,
                    device
                )
            ],
            update_before_add=True,
        )

    LOGGER.debug("Done adding all trackers.")


class GpsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, gps_api: GpsClient, first_boot):
        super().__init__(
            hass,
            LOGGER,
            name="One2Track",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_RATE_SEC),
            always_update=False
        )
        self.gps_api = gps_api
        self.first_boot = first_boot
        self.last_update = None

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(300):
                data = await self.gps_api.update()

                LOGGER.debug("Update from the coordinator %s", data)

                if data or self.first_boot:
                    self.last_update = datetime.now()
                    return data
                else:
                    return None
        except Exception as err:
            LOGGER.error("Error in updating updater")
            raise UpdateFailed(err)


class One2TrackDeviceTracker(CoordinatorEntity, TrackerEntity):
    _device: TrackerDevice

    def __init__(
            self,
            coordinator,
            hass: HomeAssistant,
            entry: ConfigEntry,
            device: TrackerDevice
    ) -> None:
        super().__init__(coordinator)
        self._hass = hass
        self._entry = entry
        self._device = device
        self._attr_unique_id = device['uuid']
        self._attr_name = f"one2track_{device['name']}"

        self.sensors = self.create_sensors()

    @property
    def name(self):
        """Return the name of the device."""
        return self._device['name']

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return "gps"

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "serial_number": self._device['serial_number'],
            "name": self._device['name']
        }

    @property
    def icon(self):
        return "mdi:watch-variant"

    @property
    def extra_state_attributes(self):
        """Return device specific attributes."""
        return {
            "serial_number": self._device['serial_number'],
            "uuid": self._device['uuid'],
            "name": self._device['name'],
            "status": self._device['status'],
            "phone_number": self._device['phone_number'],
            "tariff_type": self._device['simcard']['tariff_type'],
            "balance_cents": self._device['simcard']['balance_cents'],
            "last_communication": self._device['last_location']['last_communication'],
            "last_location_update": self._device['last_location']['last_location_update'],
            "altitude": self._device['last_location']['altitude'],
            "location_type": self._device['last_location']['location_type'],
            "address": self._device['last_location']['address'],
            "signal_strength": self._device['last_location']['signal_strength'],
            "satellite_count": self._device['last_location']['satellite_count'],
            "host": self._device['last_location']['host'],
            "port": self._device['last_location']['port'],
            "battery_level": self._device["last_location"]["battery_percentage"]
        }

    def create_sensors(self):
        """Create sensors for the attributes."""
        sensors = []
        for attr, value in self.extra_state_attributes.items():
            sensor_name = f"{self._attr_name}_{attr}"
            sensors.append(
                One2TrackSensor(
                    self.coordinator,
                    self._hass,
                    self._entry,
                    self._device,
                    attr,
                    value,
                    sensor_name
                )
            )
        return sensors

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return float(self._device['last_location']['latitude'])

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return float(self._device['last_location']['longitude'])

    async def async_added_to_hass(self):
        """Register state update callback."""
        await super().async_added_to_hass()
        for sensor in self.sensors:
            await sensor.async_added_to_hass()

    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        await super().async_will_remove_from_hass()
        for sensor in self.sensors:
            await sensor.async_will_remove_from_hass()


class One2TrackSensor(CoordinatorEntity):
    def __init__(
            self,
            coordinator,
            hass: HomeAssistant,
            entry: ConfigEntry,
            device: TrackerDevice,
            attribute: str,
            value,
            name: str
    ) -> None:
        super().__init__(coordinator)
        self._hass = hass
        self._entry = entry
        self._device = device
        self._attribute = attribute
        self._value = value
        self._attr_unique_id = f"{device['uuid']}_{attribute}"
        self._attr_name = name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def device_info(self):
        """Return the device_info of the sensor."""
        return {
            "identifiers": {(DOMAIN, self._device['uuid'])},
            "name": self._device['name']
        }

    @property
    def extra_state_attributes(self):
        """Return sensor-specific attributes."""
        return {
            "attribute": self._attribute
        }
