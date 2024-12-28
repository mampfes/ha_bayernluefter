"""
Config flow for bayernluefter component.
"""

import logging
import voluptuous as vol
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.helpers import aiohttp_client, selector
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaFlowFormStep,
    SchemaOptionsFlowHandler,
)

from .pyernluefter import Bayernluefter

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)

SIMPLE_OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement="seconds",
                min=1,
                max=600,
            ),
        ),
    }
)

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(next_step="simple_options"),
    "simple_options": SchemaFlowFormStep(SIMPLE_OPTIONS_SCHEMA),
}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Component config flow."""

    VERSION = 2
    MINOR_VERSION = 0

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> SchemaOptionsFlowHandler:
        """Get options flow for this handler."""
        return SchemaOptionsFlowHandler(config_entry, OPTIONS_FLOW)

    async def async_step_user(self, user_input=None):
        """Handle the start of the config flow.

        Called after integration has been selected in the 'add integration
        UI'. The user_input is set to None in this case. We will open a config
        flow form then.
        This function is also called if the form has been submitted. user_input
        contains a dict with the user entered values then.
        """
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        session = aiohttp_client.async_get_clientsession(self.hass)

        try:
            device = Bayernluefter(user_input[CONF_HOST], session)
            await device.update()
        except ValueError:
            errors["base"] = "cannot_connect"
        else:
            user_input[CONF_MAC] = format_mac(device.data["MAC"])
            await self.async_set_unique_id(user_input[CONF_MAC])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"{device.data['DeviceName']} @ {user_input[CONF_HOST]}",  # noqa: E501
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
