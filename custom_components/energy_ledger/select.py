from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass,entry,add_entities): add_entities([LedgerMonth(hass.data[DOMAIN][entry.entry_id])])

class LedgerMonth(CoordinatorEntity,SelectEntity):
    _attr_unique_id="energy_ledger_report_month"; entity_id="select.energy_ledger_report_month"
    def __init__(self, coordinator):
        super().__init__(coordinator); self._attr_name=f"{coordinator.vehicle_name} report month"
    @property
    def options(self): return self.coordinator.months
    @property
    def current_option(self): return self.coordinator.selected_month
    async def async_select_option(self,option): await self.coordinator.async_select_month(option)
