from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntityFeature,
    CoverEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .xport import XPort
from .base_entity import BaseXportEntity
import asyncio


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities, discovery_info=None
):
    """Set up platform."""
    xport: XPort = hass.data[DOMAIN][config.entry_id]

    covers: list[dict] = await asyncio.to_thread(xport.covers)

    entities = []

    for cover in covers:
        entities.append(XPortCover(xport, cover.get("name"), cover))

    async_add_entities(entities, update_before_add=True)


class XPortCover(CoverEntity, BaseXportEntity):
    def __init__(self, xport: XPort, name: str, data: dict) -> None:
        CoverEntity.__init__(self)
        BaseXportEntity.__init__(self, xport, name, data, "cover")

    @property
    def unique_id(self):
        return "xport.cover." + self._data.get("name")

    @property
    def supported_features(self):
        if self._data.get("supportsHalf"):
            return CoverEntityFeature.STOP | CoverEntityFeature.CLOSE | CoverEntityFeature.OPEN
        else:
            return CoverEntityFeature.CLOSE | CoverEntityFeature.OPEN

    @property
    def device_class(self):
        return CoverDeviceClass.BLIND

    @property
    def is_opening(self):
        if self._data.get("assumeInMotion") == True:
            if self._data.get("state") == "1" or self._data.get("state") == 1:
                return True
        return False

    @property
    def is_closing(self):
        if self._data.get("assumeInMotion") == True:
            if self._data.get("state") == "2" or self._data.get("state") == 2:
                return True
        return False

    @property
    def is_closed(self):
        if self._data.get("assumeInMotion") == True:
            return False
        if self._data.get("state") == "2" or self._data.get("state") == 2:
            return True
        return False

    @property
    def assumed_state(self):
        return True

    async def async_update(self):
        """Update entity data"""
        self._data = await asyncio.to_thread(self._xport.get_cover, self._name)

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        self._data = await asyncio.to_thread(
            self._xport.do_cover_action, self._name, "UP"
        )

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        self._data = await asyncio.to_thread(
            self._xport.do_cover_action, self._name, "DOWN"
        )

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        self._data = await asyncio.to_thread(
            self._xport.do_cover_action, self._name, "STOP"
        )
