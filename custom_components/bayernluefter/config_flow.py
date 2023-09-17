"""
Config flow for bayernluefter component.
"""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
)
from homeassistant.helpers import aiohttp_client
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import format_mac

from pyernluefter import Bayernluefter

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Component config flow."""

    VERSION = 1

    def __init__(self):
        self._source = None

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
            user_input[CONF_MAC] = format_mac(device.raw()["MAC"])
            # user_input[CONF_MODEL] = avr.protocol.model
            await self.async_set_unique_id(user_input[CONF_MAC])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"{device.raw_converted()['DeviceName']} @ {user_input[CONF_HOST]}", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
