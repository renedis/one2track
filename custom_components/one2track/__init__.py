import asyncio
from requests import ConnectTimeout, HTTPError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from .client import get_client, One2TrackConfig
from .common import (
    CONF_USER_NAME,
    CONF_PASSWORD,
    CONF_ID,
    DOMAIN,
    LOGGER
)

PLATFORMS = ["device_tracker", "sensor"]

class GpsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_client):
        super().__init__(
            hass,
            LOGGER,
            name="One2Track Coordinator",
            update_interval=timedelta(seconds=30),
        )
        self.api_client = api_client

    async def _async_update_data(self):
        try:
            return await self.api_client.update()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    config = One2TrackConfig(username=entry.data[CONF_USER_NAME], password=entry.data[CONF_PASSWORD], id=entry.data[CONF_ID])
    api = get_client(config)

    coordinator = GpsCoordinator(hass, api)
    await coordinator.async_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
