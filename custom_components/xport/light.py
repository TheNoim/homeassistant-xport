from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .xport import XPort
from .base_entity import BaseXportEntity


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities, discovery_info=None
):
    """Set up platform."""
    # Code for setting up your platform inside of the event loop.

    xport: XPort = hass.data[DOMAIN][config.entry_id]

    lights: list[dict] = await hass.async_add_job(xport.lights)

    entities = []

    for light in lights:
        entities.append(XPortLight(xport, light.get("name"), light))

    async_add_entities(entities, update_before_add=True)


class XPortLight(LightEntity, BaseXportEntity):
    def __init__(self, xport: XPort, name: str, data: dict) -> None:
        LightEntity.__init__(self)
        BaseXportEntity.__init__(self, xport, name, data, "light")

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._data.get("value")

    @property
    def unique_id(self):
        return "xport." + self._data.get("homeAssistantType") + self._data.get("name")

    async def async_update(self):
        """Update entity data"""

        self._data = await self.hass.async_add_job(self._xport.get_switch, self._name)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""

        self._data = await self.hass.async_add_job(
            self._xport.set_state, self._name, False
        )

    async def async_turn_on(self, **kwargs):
        """Turn the entity om."""

        self._data = await self.hass.async_add_job(
            self._xport.set_state, self._name, True
        )
