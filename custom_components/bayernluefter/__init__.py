"""
Support for Bayernluefter.
"""

import logging
from datetime import timedelta, datetime
from typing import Any
from aiohttp import ClientError
from requests.exceptions import RequestException

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pyernluefter import Bayernluefter

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


UPDATE_SCAN_INTERVAL = timedelta(days=1)  # check once per day for firmware updates

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.FAN, Platform.UPDATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry,
    config_entry contains data from config entry database."""
    session = async_get_clientsession(hass)
    device = Bayernluefter(entry.data[CONF_HOST], session)

    await device.poll_latest_versions()

    update_interval = timedelta(
        seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    coordinator = BayernluefterDataUpdateCoordinator(
        hass, device=device, update_interval=update_interval
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(on_update_options_listener))

    async def poll_latest_versions(now: datetime) -> None:
        await device.poll_latest_versions()

    entry.async_on_unload(
        async_track_time_interval(hass, poll_latest_versions, UPDATE_SCAN_INTERVAL)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def on_update_options_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.update_interval = timedelta(seconds=entry.options[CONF_SCAN_INTERVAL])


class BayernluefterDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from Bayernluefter device."""

    _device: Bayernluefter

    def __init__(
        self,
        hass: HomeAssistant,
        device: Bayernluefter,
        update_interval,
    ) -> None:
        """Initialize."""
        self._device = device

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            await self._device.update()
            self._failure_counter = 0
        except (ClientError, RequestException):
            self._failure_counter += 1
            if self._failure_counter == 3:
                _LOGGER.error("3 consecutive errors")
            if self._failure_counter >= 3:
                raise


class BayernluefterEntity(CoordinatorEntity, Entity):
    """A sensor implementation for Bayernluefter devices."""

    _coordinator: BayernluefterDataUpdateCoordinator
    _device: Bayernluefter
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BayernluefterDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize a sensor for an Bayernluefter device."""
        super().__init__(coordinator)
        device = coordinator._device
        self._coordinator = coordinator
        self._device = device
        self._attr_unique_id = f"{format_mac(device.raw()['MAC'])}-{description.key}"
        self._attr_device_info = DeviceInfo(
            configuration_url=f"http://{device.raw()['LocalIP']}",
            identifiers={(DOMAIN, format_mac(device.raw()["MAC"]))},
            name=device.raw()["DeviceName"],
            manufacturer="BAVARIAVENT UG (haftungsbeschränkt) & Co. KG",
            model="Bayernlüfter",
            sw_version=f"{device.raw()['FW_MainController']} / {device.raw()['FW_WiFi']}",  # noqa: E501
        )

    @property
    def available(self) -> bool:
        # Note: we only check raw() and not raw_converted() because both have the
        # same set of keys
        return super().available and self.entity_description.key in self._device.raw()
