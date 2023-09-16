"""
Support for Bayernluefter sensors.
"""

import logging

from homeassistant.const import (
    EntityCategory,
    STATE_UNKNOWN,
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
        key="_FrostschutzAktiv",
        name="FrostschutzAktiv",
    ),
    BinarySensorEntityDescription(
        key="_AbtauMode",
        name="AbtauMode",
    ),
    BinarySensorEntityDescription(
        key="_VermieterMode",
        name="VermieterMode",
        entity_category=EntityCategory.CONFIG,
    ),
    BinarySensorEntityDescription(
        key="_QuerlueftungAktiv",
        name="QuerlueftungAktiv",
    ),
    BinarySensorEntityDescription(
        key="_MaxMode",
        name="MaxMode",
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
        try:
            return self._device.raw_converted()[self.entity_description.key]
        except KeyError:
            return STATE_UNKNOWN
