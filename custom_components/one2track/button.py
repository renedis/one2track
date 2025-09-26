import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common import DOMAIN
from . import GpsCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up One2Track button entities."""
    coordinator: GpsCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_config_entry_first_refresh()

    buttons = []
    if coordinator.data:
        for device in coordinator.data:
            device_id = device.get("id") or device.get("uuid")
            if not device_id:
                continue
            buttons.append(ForceRefreshLocationButton(coordinator, device_id, device))

    async_add_entities(buttons, update_before_add=True)


class ForceRefreshLocationButton(CoordinatorEntity, ButtonEntity):
    """Force refresh location button for One2Track device."""

    def __init__(self, coordinator: GpsCoordinator, device_id: str, device_data: dict) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_data = device_data

        self._attr_name = f"{device_data.get('name', 'One2Track')} Force Refresh"
        self._attr_unique_id = f"{device_id}_force_refresh"
        self._attr_icon = "mdi:refresh"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_data.get("name", "One2Track Device"),
            "manufacturer": "One2Track",
            "model": device_data.get("model", "GPS Watch"),
            "sw_version": device_data.get("firmware_version"),
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            _LOGGER.debug("Sending force refresh command for device %s", self._device_id)
            await self.coordinator.api_client.set_device_refresh_location(self._device_id)
            _LOGGER.info("Force refresh command sent for device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to send force refresh command for %s: %s", self._device_id, err)
            raise
