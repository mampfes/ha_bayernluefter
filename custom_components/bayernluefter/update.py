"""
Support for Bayernluefter update.
"""

import logging
from typing import Any

from homeassistant.components.update import (
    UpdateEntity,
    UpdateEntityDescription,
    UpdateEntityFeature,
    UpdateDeviceClass,
)


from . import (
    BayernluefterEntity,
    BayernluefterDataUpdateCoordinator as DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up update entries."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [BayernluefterUpdate(coordinator)]
    async_add_entities(entities)


class BayernluefterUpdate(BayernluefterEntity, UpdateEntity):
    """An update implementation for Bayernluefter devices."""

    entity_description = UpdateEntityDescription(
        key="FW_WiFi", device_class=UpdateDeviceClass.FIRMWARE
    )

    # These update specific attributes are not (yet) part of UpdateEntityDescription
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize an update entity for a Bayernluefter device."""
        super().__init__(coordinator, self.entity_description)
        self._attr_release_url = self._device.wifi_release_url

    @property
    def available(self) -> bool:
        return (
            self._coordinator.last_update_success
            and self._device.installed_wifi_version is not None
        )

    @property
    def latest_version(self) -> str:
        return self._device.latest_wifi_version

    @property
    def installed_version(self) -> str:
        return self._device.installed_wifi_version

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install the latest firmware version."""
        await self._device.update_check()
