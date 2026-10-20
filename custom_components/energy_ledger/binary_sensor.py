from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass,entry,add_entities):
    c=hass.data[DOMAIN][entry.entry_id]; add_entities([LedgerBinary(c,"ready"),LedgerBinary(c,"locked")])

class LedgerBinary(CoordinatorEntity,BinarySensorEntity):
    def __init__(self,c,key):
        super().__init__(c); self.key=key; self._attr_unique_id=f"energy_ledger_report_{key}"; self._attr_name=f"{c.vehicle_name} report {key}"; self.entity_id=f"binary_sensor.energy_ledger_report_{key}"
    @property
    def is_on(self): return bool(self.coordinator.data.get(self.key))
