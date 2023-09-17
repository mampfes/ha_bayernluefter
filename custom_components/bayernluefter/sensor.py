"""
Support for Bayernluefter sensors.
"""

import logging
from typing import Final

from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.typing import StateType

from pyernluefter.convert import SystemMode

from . import (
    BayernluefterEntity,
    BayernluefterDataUpdateCoordinator as DataUpdateCoordinator,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# special units of measurement
CONCENTRATION_GRAMS_PER_CUBIC_METER: Final = "g/m³"
TRANSPORT_GRAMS_PER_DAY: Final = "g/d"


SENSOR_TYPES_CONVERTED: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="Temp_In",
        name="Temp_In",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Temp_Out",
        name="Temp_Out",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Temp_Fresh",
        name="Temp_Fresh",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="rel_Humidity_In",
        name="Humidity_In_rel",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="rel_Humidity_Out",
        name="Humidity_Out_rel",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="abs_Humidity_In",
        name="Humidity_In_abs",
        icon="mdi:water-percent",
        native_unit_of_measurement=CONCENTRATION_GRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="abs_Humidity_Out",
        name="Humidity_Out_abs",
        icon="mdi:water-percent",
        native_unit_of_measurement=CONCENTRATION_GRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Efficiency",
        name="Efficiency",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Humidity_Transport",
        name="Humidity_Transport",
        icon="mdi:arrow-right-bold-circle-outline",
        native_unit_of_measurement=TRANSPORT_GRAMS_PER_DAY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="RSSI",
        name="RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="Speed_In",
        name="Speed_In",
        icon="mdi:fan",
    ),
    SensorEntityDescription(
        key="Speed_Out",
        name="Speed_Out",
        icon="mdi:fan",
    ),
    SensorEntityDescription(
        key="Speed_AntiFreeze",
        name="Speed_AntiFreeze",
        icon="mdi:fan",
    ),
)
SENSOR_TYPES_RAW: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="MAC",
        name="MAC",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="LocalIP",
        name="IP",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="SystemMode",
        name="SystemMode",
        device_class=SensorDeviceClass.ENUM,
        options=[e.value for e in SystemMode],
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor entries."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    entities.extend(
        [
            BayernluefterSensorConverted(coordinator, description)
            for description in SENSOR_TYPES_CONVERTED
        ]
    )
    entities.extend(
        [
            BayernluefterSensorRaw(coordinator, description)
            for description in SENSOR_TYPES_RAW
        ]
    )
    async_add_entities(entities)


class BayernluefterSensorEntity(BayernluefterEntity, SensorEntity):
    """A sensor implementation for Bayernluefter devices."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize a sensor entity for a Bayernluefter device."""
        super().__init__(coordinator, description)
        self.entity_description = description


class BayernluefterSensorConverted(BayernluefterSensorEntity):
    """A sensor implementation for Bayernluefter devices."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize a sensor entity for a Bayernluefter device."""
        super().__init__(coordinator, description)

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self._device.raw_converted()[self.entity_description.key]


class BayernluefterSensorRaw(BayernluefterSensorEntity):
    """A sensor implementation for Bayernluefter devices."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize a sensor entity for a Bayernluefter device."""
        super().__init__(coordinator, description)

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self._device.raw()[self.entity_description.key]
