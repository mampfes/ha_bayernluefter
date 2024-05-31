"""Connect to a Bayernluefter."""

import logging
import aiohttp
import re
import parse
from http import HTTPStatus
from enum import Enum
from dataclasses import dataclass

from typing import Dict

from .convert import CONVERSION_DICT

ENDPOINT_EXPORT = "?export=1"
ENDPOINT_TEMPLATE = "/export.txt"
ENDPOINT_POWER_ON = "?power=on"
ENDPOINT_POWER_OFF = "?power=off"
ENDPOINT_BUTTON_POWER = "?button=power"
ENDPOINT_BUTTON_TIMER = "?button=timer"
ENDPOINT_SPEED = "?speed={}"
ENDPOINT_UPDATE_CHECK = "?updatecheck=1"

# The following motor speed controls are only available if device is switched off!
# and firmware version >= WS32240427
ENDPOINT_SPEED_IN = "?speedIn={}"
ENDPOINT_SPEED_OUT = "?speedOut={}"
ENDPOINT_SPEED_ANTI_FREEZE = "?speedFrM={}"

SERVER_URL = "https://www.bayernluft.de"


class UpdateTarget(Enum):
    WLAN32 = "wlan32"
    WLAN = "wlan"


@dataclass
class UpdateTargetInfo:
    release_url: str
    version_url: str


UPDATE_TARGET_INFOS = {
    UpdateTarget.WLAN: UpdateTargetInfo(
        release_url=f"{SERVER_URL}/de/wlan_changelist.html",
        version_url=f"{SERVER_URL}/de/download/wlan/version.txt",
    ),
    UpdateTarget.WLAN32: UpdateTargetInfo(
        release_url=f"{SERVER_URL}/de/wlan32_changelist.html",
        version_url=f"{SERVER_URL}/de/download/wlan32/version.txt",
    ),
}

_LOGGER = logging.getLogger(__name__)


def repl_to_parse(m: re.Match):
    # prepend a v s.t. no variable begins with an underscore
    return f"{{v{m.group(1)}}}"


def construct_url(ip_address: str) -> str:
    """Construct the URL with a given IP address."""
    if "http://" not in ip_address and "https://" not in ip_address:
        ip_address = f"http://{ip_address}"
    ip_address = ip_address.rstrip("/")
    return ip_address


class Bayernluefter:
    """Interface to communicate with the Bayernluefter."""

    def __init__(self, ip, session: aiohttp.ClientSession) -> None:
        """Initialize the the printer."""
        self.url = construct_url(ip)
        self._session = session
        self.data = {}  # type: Dict[str, Any]
        self.data_converted = {}  # type: Dict[str, Any]
        self.template = None
        self._latest_version = {}
        self._update_target: UpdateTarget | None = None

    async def fetch_template(self):
        """
        Fetches the template for the export values from the Bayernluefter
        """

        bl_template = await self._request_bl(ENDPOINT_TEMPLATE)
        self.template = re.sub(r"~(.+)~", repl_to_parse, bl_template)

    async def update(self) -> None:
        if self.template is None:
            await self.fetch_template()

        state = await self._request_bl(ENDPOINT_EXPORT)
        try:
            parse_dict = parse.parse(self.template, state).named
        except AttributeError:
            # the template has been changed -> ignore this update
            self.template = None
            return

        self.data = {key[1:]: value for key, value in parse_dict.items()}
        self.data_converted = {
            key: CONVERSION_DICT.get(key, str)(value)
            for key, value in self.data.items()
        }

        # estimate update target
        if self._update_target is None:
            if self.data.get("FW_MainController", "").startswith("Rev2."):
                self._update_target = UpdateTarget.WLAN32
            else:
                self._update_target = UpdateTarget.WLAN

    async def _request_bl(self, target):
        url = f"{self.url}{target}"
        async with self._session.get(url) as response:
            if response.status != HTTPStatus.OK:
                raise ValueError("Server does not support Bayernluefter protocol.")
            return await response.text(encoding="ascii", errors="ignore")

    def raw(self) -> Dict:
        """Return all details of the Bayernluefter."""
        return self.data

    def raw_converted(self) -> Dict:
        """Return all details of the Bayernluefter, converted"""
        return self.data_converted

    async def power_on(self):
        await self._request_bl(ENDPOINT_POWER_ON)

    async def power_off(self):
        await self._request_bl(ENDPOINT_POWER_OFF)

    async def power_toggle(self):
        await self._request_bl(ENDPOINT_BUTTON_POWER)

    async def timer_toggle(self):
        await self._request_bl(ENDPOINT_BUTTON_TIMER)

    async def reset_speed(self):
        await self._request_bl(ENDPOINT_SPEED.format(0))

    async def set_speed(self, level: int):
        assert 1 <= level <= 10, "Level must be between 1 and 10"
        await self._request_bl(ENDPOINT_SPEED.format(level))

    async def set_speed_in(self, level: int):
        assert 0 <= level <= 10, "Level must be between 0 and 10"
        await self._request_bl(ENDPOINT_SPEED_IN.format(level))

    async def set_speed_out(self, level: int):
        assert 0 <= level <= 10, "Level must be between 0 and 10"
        await self._request_bl(ENDPOINT_SPEED_OUT.format(level))

    async def set_speed_anti_freeze(self, level: int):
        assert 0 <= level <= 50, "Level must be between 0 and 50"
        await self._request_bl(ENDPOINT_SPEED_ANTI_FREEZE.format(level))

    async def update_check(self):
        await self._request_bl(ENDPOINT_UPDATE_CHECK)

    async def poll_latest_versions(self):
        for target in UpdateTarget:
            await self.poll_latest_version(target)

    async def poll_latest_version(self, target: UpdateTarget):
        """Fetch latest version from Bayernluft server"""
        async with self._session.get(
            UPDATE_TARGET_INFOS[target].version_url
        ) as response:
            response.raise_for_status()
            self._latest_version[target] = await response.text(
                encoding="ascii", errors="ignore"
            )

    def latest_wifi_version(self) -> str:
        return self._latest_version.get(self._update_target)

    def installed_wifi_version(self) -> str:
        if self._update_target in (UpdateTarget.WLAN32, UpdateTarget.WLAN):
            return self.data.get("FW_WiFi")

        return None

    def wifi_release_url(self) -> str:
        info = UPDATE_TARGET_INFOS.get(self._update_target)
        if info is not None:
            return info.release_url
        return None
