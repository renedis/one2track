import logging
from datetime import timedelta, datetime
from typing import List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.entity import Entity
from homeassistant.components.device_tracker.config_entry import TrackerEntity
import async_timeout

from .client import GpsClient, TrackerDevice
from .common import DOMAIN, DEFAULT_UPDATE_RATE_SEC

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the main device tracker and its attribute sensors."""
    LOGGER.debug("one2track async_setup_entry")

    gps_api: GpsClient = hass.data[DOMAIN][entry.entry_id]['api_client']
    devices: List[TrackerDevice] = await gps_api.update()

    coordinator = GpsCoordinator(hass, gps_api, True)
    main_entities = []
    attribute_sensors = []

    LOGGER.info("Adding %s found one2track devices", len(devices))

    for device in devices:
        # Main device tracker entity
        main_entity = One2TrackSensor(coordinator, hass, entry, device)
        main_entities.append(main_entity)

        # Create sensors for all attributes
        attributes = {
            "serial_number": ("Serial Number", "mdi:numeric"),
            "uuid": ("UUID", "mdi:identifier"),
            "status": ("Status", "mdi:information"),
            "phone_number": ("Phone Number", "mdi:phone"),
            "tariff_type": ("Tariff Type", "mdi:card-account-details"),
            "balance_cents": ("Balance", "mdi:currency-usd"),
            "last_communication": ("Last Communication", "mdi:clock"),
            "last_location_update": ("Last Location Update", "mdi:update"),
            "altitude": ("Altitude", "mdi:elevation-rise"),
            "location_type": ("Location Type", "mdi:map-marker"),
            "address": ("Address", "mdi:map-marker"),
            "signal_strength": ("Signal Strength", "mdi:signal"),
            "satellite_count": ("Satellite Count", "mdi:satellite-variant"),
            "host": ("Host", "mdi:server"),
            "port": ("Port", "mdi:lan"),
            "battery_percentage": ("Battery Level", "mdi:battery"),
        }

        for attr, (name, icon) in attributes.items():
            attribute_sensors.append(One2TrackAttributeSensor(main_entity, attr, name, icon))

    # Add both the main entity and sensors
    async_add_entities(main_entities + attribute_sensors, update_before_add=True)

    LOGGER.debug("Done adding all trackers and sensors.")


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
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(300):
                data = await self.gps_api.update()
                LOGGER.debug("Update from the coordinator %s", data)
                self.last_update = datetime.now()
                return data
        except Exception as err:
            LOGGER.error("Error in updating updater: %s", err)
            raise UpdateFailed(err)


class One2TrackSensor(CoordinatorEntity, TrackerEntity):
    """Main device tracker entity."""

    def __init__(self, coordinator, hass: HomeAssistant, entry: ConfigEntry, device: TrackerDevice):
        super().__init__(coordinator)
        self._hass = hass
        self._entry = entry
        self._device = device
        self._attr_unique_id = device['uuid']
        self._attr_name = f"one2track_{device['name']}"

    @property
    def name(self):
        return self._device['name']

    @property
    def source_type(self):
        return "gps"

    @property
    def latitude(self):
        return float(self._device['last_location']['latitude'])

    @property
    def longitude(self):
        return float(self._device['last_location']['longitude'])

    @property
    def extra_state_attributes(self):
        """Additional attributes for the device tracker."""
        return {
            "serial_number": self._device['serial_number'],
            "uuid": self._device['uuid'],
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
            "battery_percentage": self._device["last_location"]["battery_percentage"],
        }

    @property
    def device_info(self):
        """Group this tracker and sensors under one device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "One2Track",
            "model": "GPS Tracker",
            "sw_version": "1.0",
        }


class One2TrackAttributeSensor(Entity):
    """Represents an attribute of the One2TrackSensor as a standalone sensor entity."""

    def __init__(self, parent_entity: One2TrackSensor, attribute: str, name: str, icon: str = None):
        self._parent_entity = parent_entity
        self._attribute = attribute
        self._attr_name = f"{parent_entity.name} {name}"
        self._attr_unique_id = f"{parent_entity.unique_id}_{attribute}"
        self._icon = icon

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        """Get the state of the attribute from the parent."""
        return self._parent_entity.extra_state_attributes.get(self._attribute)

    @property
    def icon(self):
        return self._icon

    @property
    def should_poll(self):
        return False

    @property
    def device_info(self):
        """Ensure this sensor is grouped with the parent device."""
        return self._parent_entity.device_info

    @callback
    def _handle_coordinator_update(self):
        """Handle updates from the parent entity."""
        self.async_write_ha_state()
