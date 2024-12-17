import asyncio
from requests import ConnectTimeout, HTTPError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
import voluptuous as vol

from .client import get_client, One2TrackConfig
from .common import (
    CONF_USER_NAME,
    CONF_PASSWORD,
    CONF_ID,
    DOMAIN,
    LOGGER
)

PLATFORMS = [DEVICE_TRACKER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up One2Track Data from a config entry."""

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    config = One2TrackConfig(username=entry.data[CONF_USER_NAME], password=entry.data[CONF_PASSWORD], id=entry.data[CONF_ID])
    api = get_client(config)
    try:
        account_id = await api.install()
    except (ConnectTimeout, HTTPError) as ex:
        LOGGER.error("Could not retrieve details from One2Track API")
        raise ConfigEntryNotReady from ex

    if account_id != entry.data[CONF_ID]:
        LOGGER.error(f"Unexpected initial account id: {account_id}. Expected: {entry.data[CONF_ID]}")
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {'api_client': api}

    # Import device tracker and sensors
    async def async_setup_platforms():
        coordinator = hass.data[DOMAIN][entry.entry_id]['api_client']
        devices = await coordinator.update()
        entities = [
            One2TrackTracker(coordinator, device) for device in devices
        ]
        
        attributes = {
            "battery_percentage": ("Battery Level", "%"),
            "signal_strength": ("Signal Strength", "dBm"),
            "altitude": ("Altitude", "m"),
            "gps_nauwkeurigheid": ("GPS Accuracy", "m"),
        }

        for device in devices:
            for attribute, (name, unit) in attributes.items():
                entities.append(One2TrackSensor(coordinator, device, attribute, name, unit))

        hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))

    await async_setup_platforms()

    for component in PLATFORMS:
        LOGGER.debug(f"[one2track] creating tracker for: {entry}")
        await hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
