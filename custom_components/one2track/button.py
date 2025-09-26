import logging
from typing import Any, Dict, Iterable, List

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common import DOMAIN
from . import GpsCoordinator

_LOGGER = logging.getLogger(__name__)


def _iter_devices(data: Any) -> Iterable[Dict[str, Any]]:
    """Normalize coordinator.data to an iterable of device dicts."""
    if not data:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "devices" in data and isinstance(data["devices"], list):
            return data["devices"]
        return [data]
    return []


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up One2Track button entities."""
    coordinator: GpsCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    devices = list(_iter_devices(coordinator.data))
    
    _LOGGER.debug("Setting up buttons for devices: %s", devices)
    
    buttons: List[ButtonEntity] = []
    for device in devices:
        device_id = device.get("uuid") or device.get("id") or device.get("device_id")
        if not device_id:
            _LOGGER.debug("Skipping device without id-like key: %s", device)
            continue
        
        buttons.append(UpdateLocationButton(coordinator, device_id, device))
        buttons.append(PowerOffDeviceButton(coordinator, device_id, device))
    
    if not buttons:
        _LOGGER.warning("No One2Track buttons created. coordinator.data was: %s", coordinator.data)
    
    async_add_entities(buttons)


class UpdateLocationButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger GPS update (API call 0039) for a One2Track device."""
    
    _attr_icon = "mdi:crosshairs-gps"
    
    def __init__(self, coordinator: GpsCoordinator, device_id: str, device_data: Dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_data = device_data
        
        name = device_data.get("name") or "One2Track"
        self._attr_name = f"{name} Update Location"
        self._attr_unique_id = f"one2track_{device_id}_update_location"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_data["name"])},
            "name": f"One2Track {name}",
            "manufacturer": "One2Track",
            "model": "GPS watch",
            "sw_version": device_data.get("serial_number", "Unknown"),
        }
    
    async def async_press(self) -> None:
        """Handle the button press: trigger API call '0039'."""
        try:
            _LOGGER.debug("Sending '0039' Update Location for device %s", self._device_id)
            await self.coordinator.api_client.force_gps_update(self._device_id)
            _LOGGER.info("Update Location (0039) sent for device %s", self._device_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to send Update Location (0039) for %s: %s", self._device_id, err)
            raise


class PowerOffDeviceButton(CoordinatorEntity, ButtonEntity):
    """Button to power off a One2Track device (API call 0048)."""
    
    _attr_icon = "mdi:power"
    
    def __init__(self, coordinator: GpsCoordinator, device_id: str, device_data: Dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_data = device_data
        
        name = device_data.get("name") or "One2Track"
        self._attr_name = f"{name} Power Off"
        self._attr_unique_id = f"one2track_{device_id}_power_off"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_data["name"])},
            "name": f"One2Track {name}",
            "manufacturer": "One2Track",
            "model": "GPS watch",
            "sw_version": device_data.get("serial_number", "Unknown"),
        }
    
    async def async_press(self) -> None:
        """Handle the button press: trigger API call '0048'."""
        try:
            _LOGGER.debug("Sending '0048' Power Off for device %s", self._device_id)
            await self.coordinator.api_client.power_off_device(self._device_id)
            _LOGGER.info("Power Off (0048) sent for device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to send Power Off (0048) for %s: %s", self._device_id, err)
            raise
