from .const import DOMAIN
from .xport import XPort
from homeassistant.helpers.entity import Entity


class BaseXportEntity(Entity):
    """Base xport entity"""

    def __init__(self, xport: XPort, name: str, data: dict, type: str) -> None:
        super().__init__()
        self._xport = xport
        self._name = name
        self._data: dict = data
        self._type = type

    @property
    def name(self):
        """Name of the entity."""
        return self._name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self._name,
            "manufacturer": "xport",
            "model": "xport-" + self._type,
        }

    @property
    def unique_id(self):
        return "xport." + self._data.get("homeAssistantType") + self._data.get("name")
