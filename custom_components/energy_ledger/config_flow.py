"""Set up the standalone integration without a backend URL or API credentials."""
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN


def valid_input(data):
    if not data["vehicle_name"].strip():
        raise ValueError("vehicle name is required")
    ZoneInfo(data["timezone"])
    end = data.get("contract_end_month", "")
    if end and not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", end):
        raise ValueError("invalid contract end month")
    if bool(data.get("moj_elektro_token")) != bool(data.get("moj_elektro_usage_point")):
        raise ValueError("both Moj Elektro fields are required")
    sheet_token = data.get("sheet_export_token", "")
    if sheet_token and (len(sheet_token) < 32 or sheet_token != sheet_token.strip()):
        raise ValueError("sheet export token must be at least 32 characters with no surrounding whitespace")
    return data


def schema(defaults, advanced=False):
    fields = {
        vol.Required("vehicle_name", default=defaults.get("vehicle_name", "EV")): str,
        vol.Required("timezone", default=defaults.get("timezone", "UTC")): str,
        vol.Optional("odometer_entity", default=defaults.get("odometer_entity", "")): str,
        vol.Optional("home_energy_statistic", default=defaults.get("home_energy_statistic", "")): str,
    }
    if advanced:
        fields.update({
            vol.Optional("allowance_km", default=defaults.get("allowance_km", 0)): vol.All(vol.Coerce(int), vol.Range(min=0)),
            vol.Optional("contract_end_month", default=defaults.get("contract_end_month", "")): str,
            vol.Optional("moj_elektro_usage_point", default=defaults.get("moj_elektro_usage_point", "")): str,
            vol.Optional("moj_elektro_token", default=defaults.get("moj_elektro_token", "")): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
            vol.Optional("sheet_export_token", default=defaults.get("sheet_export_token", "")): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
        })
    return vol.Schema(fields)


class EnergyLedgerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 4

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        errors = {}
        if user_input is not None:
            try:
                valid_input(user_input)
                return self.async_create_entry(title=user_input["vehicle_name"].strip(), data=user_input)
            except (ValueError, ZoneInfoNotFoundError):
                errors["base"] = "invalid_config"
        defaults = {"timezone": self.hass.config.time_zone, **(user_input or {})}
        return self.async_show_form(step_id="user", data_schema=schema(defaults), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EnergyLedgerOptionsFlow()


class EnergyLedgerOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                valid_input(user_input)
                return self.async_create_entry(title="", data={**self.config_entry.options, **user_input})
            except (ValueError, ZoneInfoNotFoundError):
                errors["base"] = "invalid_config"
        defaults = {**self.config_entry.data, **self.config_entry.options, **(user_input or {})}
        return self.async_show_form(step_id="init", data_schema=schema(defaults, advanced=True), errors=errors)
