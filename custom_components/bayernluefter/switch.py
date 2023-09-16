"""
Support for Bayernluefter switches.
"""


import logging

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
    # SwitchDeviceClass,
)

from . import (
    BayernluefterEntity,
    BayernluefterDataUpdateCoordinator as DataUpdateCoordinator,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up switch entries."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [BayernluefterPowerSwitch(coordinator)]
    async_add_entities(entities)


class BayernluefterPowerSwitch(BayernluefterEntity, SwitchEntity):
    """A power switch implementation for Bayernluefter devices."""

    entity_description: SwitchEntityDescription = SwitchEntityDescription(
        key="_SystemOn",
        name="Power",
        # device_class=SwitchDeviceClass.SWITCH,
    )

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize a switch entity for a Bayernluefter device."""
        super().__init__(coordinator, self.entity_description)

    @property
    def is_on(self) -> bool:
        """Return the device power status."""
        return self._device.raw_converted()[self.entity_description.key]

    async def async_turn_on(self, **kwargs):
        """Switch on the device."""
        await self._device.power_on()
        """self._assumed_state = True"""

    async def async_turn_off(self, **kwargs):
        """Switch off the device."""
        await self._device.power_off()

    async def async_toggle(self, **kwargs):
        """Toggle the device."""
        await self._device.power_toggle()
