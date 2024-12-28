"""
Support for Bayernluefter sensors.
"""

import logging

from homeassistant.const import (
    EntityCategory,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from . import (
    BayernluefterEntity,
    BayernluefterDataUpdateCoordinator as DataUpdateCoordinator,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES_CONVERTED: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="FrostschutzAktiv",
        name="FrostschutzAktiv",
    ),
    BinarySensorEntityDescription(
        key="AbtauMode",
        name="AbtauMode",
    ),
    BinarySensorEntityDescription(
        key="VermieterMode",
        name="VermieterMode",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key="QuerlueftungAktiv",
        name="QuerlueftungAktiv",
    ),
    BinarySensorEntityDescription(
        key="TimerActiv",
        name="TimerAktiv",
    ),
    BinarySensorEntityDescription(
        key="SpeedFrozen",
        name="SpeedFrozen",
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor entries."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    entities.extend(
        [
            BayernluefterBinarySensor(coordinator, description)
            for description in SENSOR_TYPES_CONVERTED
        ]
    )
    async_add_entities(entities)


class BayernluefterBinarySensor(BayernluefterEntity, BinarySensorEntity):
    """A sensor implementation for Bayernluefter devices."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize a sensor entity for a Bayernluefter device."""
        super().__init__(coordinator, description)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return self._device.data[self.entity_description.key]
