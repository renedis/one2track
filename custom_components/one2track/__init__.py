import asyncio
from requests import ConnectTimeout, HTTPError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from datetime import timedelta
from .client import get_client, One2TrackConfig
from .common import (
    CONF_USER_NAME,
    CONF_PASSWORD,
    CONF_ID,
    DOMAIN,
    LOGGER
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

PLATFORMS = ["device_tracker", "sensor"]

class GpsCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch and manage One2Track data."""

    def __init__(self, hass, api_client):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name="One2Track Coordinator",
            update_interval=timedelta(seconds=30),
        )
        self.api_client = api_client

    async def _async_update_data(self):
        """Fetch the latest data from the API."""
        try:
            return await self.api_client.update()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up One2Track Data from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    config = One2TrackConfig(username=entry.data[CONF_USER_NAME], password=entry.data[CONF_PASSWORD], id=entry.data[CONF_ID])
    api = get_client(config)

    # Wrap the API client with GpsCoordinator
    coordinator = GpsCoordinator(hass, api)
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
