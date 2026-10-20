from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

ACTIONS={"refresh":"refresh","lock":"lock","export":"export","create_revision":"create-revision"}
async def async_setup_entry(hass,entry,add_entities):
    c=hass.data[DOMAIN][entry.entry_id]; add_entities([LedgerButton(c,k,v) for k,v in ACTIONS.items()])

class LedgerButton(CoordinatorEntity,ButtonEntity):
    def __init__(self,c,key,path):
        super().__init__(c); self.key=key; self.path=path; self._attr_unique_id=f"energy_ledger_report_{key}"; self._attr_name=f"{c.vehicle_name} report {key.replace('_',' ')}"; self.entity_id=f"button.energy_ledger_report_{key}"
    async def async_press(self):
        await self.coordinator.request("POST",f"/api/v1/months/{self.coordinator.selected_month}/{self.path}")
        await self.coordinator.async_request_refresh()
