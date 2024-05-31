"""
Support for Bayernluefter fan speed via HA number.
"""

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberDeviceClass,
)

from . import (
    BayernluefterEntity,
    BayernluefterDataUpdateCoordinator as DataUpdateCoordinator,
)
from .const import DOMAIN
from .pyernluefter import Bayernluefter

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BayernluftNumberEntityDescription(NumberEntityDescription):
    """Describes a Bayernluft number entity."""

    value_fn: Callable[[Bayernluefter], float]


NUMBER_TYPES: tuple[BayernluftNumberEntityDescription, ...] = (
    BayernluftNumberEntityDescription(
        key="Speed_In",
        name="Speed_In_Control",
        native_min_value=0,
        native_max_value=10,
        native_step=1,
        device_class=NumberDeviceClass.SPEED,
        value_fn=lambda luefter, speed: luefter.set_speed_in(speed),
    ),
    BayernluftNumberEntityDescription(
        key="Speed_Out",
        name="Speed_Out_Control",
        native_min_value=0,
        native_max_value=10,
        native_step=1,
        device_class=NumberDeviceClass.SPEED,
        value_fn=lambda luefter, speed: luefter.set_speed_out(speed),
    ),
    BayernluftNumberEntityDescription(
        key="Speed_AntiFreeze",
        name="Speed_AntiFreeze_Control",
        native_min_value=0,
        native_max_value=50,
        native_step=5,
        device_class=NumberDeviceClass.SPEED,
        value_fn=lambda luefter, speed: luefter.set_speed_anti_freeze(speed),
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up number entries."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [
        BayernluefterNumber(coordinator, description) for description in NUMBER_TYPES
    ]
    async_add_entities(entities)


class BayernluefterNumber(BayernluefterEntity, NumberEntity):
    """A number implementation for Bayernluefter devices."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: BayernluftNumberEntityDescription,
    ) -> None:
        """Initialize a sensor entity for a Bayernluefter device."""
        super().__init__(coordinator, description)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the sensor."""
        return self._device.raw_converted()[self.entity_description.key]

    async def async_set_native_value(self, value: float) -> None:
        """Update the native value."""
        await self.entity_description.value_fn(self._device, value)
