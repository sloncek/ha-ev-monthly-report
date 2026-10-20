from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, add_entities):
    add_entities([LedgerVat(hass.data[DOMAIN][entry.entry_id])])


class LedgerVat(CoordinatorEntity, NumberEntity):
    _attr_unique_id = "energy_ledger_vat_rate"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 0.01
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:percent"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"{coordinator.vehicle_name} DDV od izbranega meseca"
        self.entity_id = "number.energy_ledger_report_vat_rate"

    @property
    def native_value(self):
        value = self.coordinator.data.get("vat_rate_pct")
        return None if value is None else float(value)

    @property
    def available(self):
        return super().available and self.native_value is not None

    @property
    def extra_state_attributes(self):
        return {"effective_from_month":self.coordinator.selected_month,
                "description":"Sprememba velja od izbranega meseca naprej. Starejši meseci se ne spremenijo."}

    async def async_set_native_value(self, value):
        await self.coordinator.request("POST",f"/api/v1/months/{self.coordinator.selected_month}/vat",json={"rate_pct":str(value)})
        await self.coordinator.async_request_refresh()
