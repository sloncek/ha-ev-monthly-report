from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .values import timestamp_value

FIELDS = {
    **{f"mileage_{key}": (None,"km") for key in ("predicted_final_odometer_km","excess_km","anchor_odometer_km")},
    "mileage_history_months": (None,None), "mileage_status": (None,None),
    "claim_status": (None,None), "reimbursement_rate": (None,"EUR/kWh"),
    **{key: (SensorDeviceClass.MONETARY,"EUR") for key in ("home_reimbursement_eur","public_gross_eur","other_gross_eur","eligible_expenses_eur","monthly_eligible_eur","opening_balance_eur","requested_eur","reported_eur","closing_balance_eur","pending_home_delta_eur")},
    "odometer_km": (None,"km"), "monthly_distance_km": (None,"km"),
    "current_home_kwh": (SensorDeviceClass.ENERGY,UnitOfEnergy.KILO_WATT_HOUR),
    "vat_rate_pct": (None,"%"), "home_cost_net": (SensorDeviceClass.MONETARY,"EUR"), "home_vat_cost": (SensorDeviceClass.MONETARY,"EUR"),
    "electricity_price_gross": (None,"EUR/kWh"), "home_data_quality": (None,None), "home_missing_hours": (None,"h"),
    "latest_import_state": (None,None),
    "status": (None, None), "data_quality": (None, None), "issue_count": (None, None), "last_sync": (SensorDeviceClass.TIMESTAMP, None),
    "bill_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "bill_peak_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "bill_offpeak_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR),
    "bill_net": (SensorDeviceClass.MONETARY, "EUR"), "bill_vat": (SensorDeviceClass.MONETARY, "EUR"), "bill_gross": (SensorDeviceClass.MONETARY, "EUR"),
    "grid_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "grid_peak_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "grid_offpeak_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR),
    **{f"grid_block_{i}": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR) for i in range(1,6)},
    "variance_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "variance_pct": (None, "%"),
    "home_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "home_cost": (SensorDeviceClass.MONETARY, "EUR"), "home_session_count": (None,None),
    "public_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "public_paid_cost": (SensorDeviceClass.MONETARY,"EUR"), "public_reimbursable_cost": (SensorDeviceClass.MONETARY,"EUR"), "public_session_count": (None,None), "missing_evidence_count": (None,None),
    "total_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "total_cost": (SensorDeviceClass.MONETARY,"EUR"), "reimbursable_cost": (SensorDeviceClass.MONETARY,"EUR"),
    "gas_m3": (SensorDeviceClass.GAS, UnitOfVolume.CUBIC_METERS), "gas_kwh": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR), "gas_gross": (SensorDeviceClass.MONETARY,"EUR"),
    "pricing_method": (None,None), "report_id": (None,None)
}


async def async_setup_entry(hass, entry, add_entities):
    coordinator=hass.data[DOMAIN][entry.entry_id]
    add_entities([LedgerSensor(coordinator,key,*meta) for key,meta in FIELDS.items()])


class LedgerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, device_class, unit):
        super().__init__(coordinator); self.key=key
        self._attr_unique_id=f"energy_ledger_report_{key}"
        self._attr_name=f"{coordinator.vehicle_name} report {key.replace('_',' ')}"
        self._attr_device_class=device_class; self._attr_native_unit_of_measurement=unit
        self.entity_id=f"sensor.energy_ledger_report_{key}"

    @property
    def native_value(self):
        if self.key.startswith("mileage_"):
            data=self.coordinator.data.get("mileage_forecast") or {}
            key=self.key.removeprefix("mileage_")
            if key=="status": return "forecast" if data.get("available") else "waiting_for_history"
            if not data.get("available"): return None
            if key=="predicted_final_odometer_km": return (data.get("final") or {}).get("predicted_odometer_km")
            if key=="excess_km": return (data.get("final") or {}).get("excess_km")
            if key=="history_months": return data.get("historical_months")
            return data.get(key)
        register=self.coordinator.data.get("register") or {}
        if self.key == "claim_status": return register.get("status")
        if self.key == "current_home_kwh": return register.get("current_home_kwh",register.get("home_kwh"))
        if self.key in register and (self.key.endswith("_eur") or self.key in {"reimbursement_rate","odometer_km","monthly_distance_km"}): return register[self.key]
        value = self.coordinator.data.get(self.key)
        return timestamp_value(value) if self.key == "last_sync" else value

    @property
    def available(self): return super().available and self.native_value is not None

    @property
    def extra_state_attributes(self):
        if self.key=="mileage_status":
            data=self.coordinator.data.get("mileage_forecast") or {}
            return {k:data.get(k) for k in ("model","anchor_month","anchor_odometer_km","history_counts","calibration","final","current_odometer_km","current_odometer_received_at")}
        if self.key == "claim_status":
            return self.coordinator.data.get("register") or {}
        if self.key in {"home_kwh","home_cost","home_data_quality"}:
            return {k:self.coordinator.data.get(k) for k in ("month","home_data_source","home_data_detail","pricing_method","vat_rate_pct","vat_rate_source","vat_effective_month")}
        if self.key == "latest_import_state":
            return {"detail":self.coordinator.data.get("latest_import_detail"),"progress":self.coordinator.data.get("latest_import_progress"),"month":self.coordinator.data.get("latest_import_month")}
        if self.key != "status": return {}
        return {k:self.coordinator.data.get(k) for k in ("primary_issue","next_action","processing","row_version","report_id","supersedes_report_id","updated_at")}
