from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .xport import XPort


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities, discovery_info=None
):
    """Set up platform."""
    # Code for setting up your platform inside of the event loop.

    xport: XPort = hass.data[DOMAIN][config.entry_id]

    switches: list[dict] = await hass.async_add_job(xport.switches)

    entities = []

    for switch in switches:
        entities.append(XPortSwitch(xport, switch.get("name"), switch))

    async_add_entities(entities, update_before_add=True)


class XPortSwitch(SwitchEntity):
    def __init__(self, xport: XPort, name: str, data: dict) -> None:
        super().__init__()

        self._xport = xport
        self._name = name
        self._data: dict = data

    @property
    def name(self):
        """Name of the entity."""
        return self._name

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
