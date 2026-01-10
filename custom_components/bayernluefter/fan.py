"""
Support for Bayernluefter fan.
"""

import logging
from enum import StrEnum
from typing import Any, Optional

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.util.percentage import (
    ranged_value_to_percentage,
    int_states_in_range,
    percentage_to_ranged_value,
)

from .pyernluefter.convert import SystemMode

from . import (
    BayernluefterEntity,
    BayernluefterDataUpdateCoordinator as DataUpdateCoordinator,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

FAN_SPEED_RANGE = (1, 10)


class FanMode(StrEnum):
    """Device entry type."""

    Auto = "Auto"
    Timer = "Timer"


SYSTEM_MODES_WITH_AUTO = {SystemMode.Kellermode, SystemMode.Behaglichkeitsmode}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up fan entries."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [BayernluefterFan(coordinator)]
    async_add_entities(entities)


class BayernluefterFan(BayernluefterEntity, FanEntity):
    """A fan implementation for Bayernluefter devices."""

    entity_description = FanEntityDescription(
        key="SystemOn",
        name="Fan",
    )

    # These fan specific attributes are not (yet) part of FanEntityDescription
    _attr_speed_count = int_states_in_range(FAN_SPEED_RANGE)
    _attr_supported_features = (
        FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
    )
    _enable_turn_on_off_backwards_compatibility = False
    # _attr_preset_modes = [e.value for e in FanMode]

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize a fan entity for a Bayernluefter device."""
        super().__init__(coordinator, self.entity_description)
        self._attr_preset_modes = [FanMode.Timer]
        if self._device.data.get("SystemMode") in SYSTEM_MODES_WITH_AUTO:
            self._attr_preset_modes.append(FanMode.Auto)

    @property
    def is_on(self) -> bool:
        """Return the fan on status."""
        return self._device.data.get("SystemOn", False)

    @property
    def percentage(self) -> int:
        """Return the speed of the fan-"""
        # Added "or 0" to handle NoneType return from get()
        return ranged_value_to_percentage(
            FAN_SPEED_RANGE, self._device.data.get("Speed_Out") or 0
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        # Changed direct dict access to .get() to prevent KeyError
        if self._device.data.get("TimerActiv"):
            pm = FanMode.Timer
        elif self._device.data.get("SpeedFrozen"):
            pm = None
        else:
            pm = FanMode.Auto
        return pm

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        await self._device.power_on()
        await self._async_set_percentage(percentage)
        await self.coordinator.async_refresh()

    async def _async_set_percentage(self, percentage: int) -> None:
        speed = int(percentage_to_ranged_value(FAN_SPEED_RANGE, percentage))
        if speed == 0:
            await self._device.power_off()
        else:
            await self._device.set_speed(speed)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        await self._async_set_preset_mode(preset_mode)

    async def _async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode == FanMode.Auto:
            await self._device.reset_speed()
        elif preset_mode == FanMode.Timer:
            await self._device.timer_toggle()
        else:
            raise ValueError(f"Invalid preset mode: {preset_mode}")
        await self.coordinator.async_refresh()

    async def async_turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        await self._device.power_on()
        if percentage is not None:
            await self._async_set_percentage(percentage)
        if preset_mode is not None:
            await self._async_set_preset_mode(preset_mode)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self._device.power_off()
        await self.coordinator.async_refresh()

    async def async_toggle(self, **kwargs: Any) -> None:
        """Toggle the fan."""
        await self._device.power_toggle()
        await self.coordinator.async_refresh()
