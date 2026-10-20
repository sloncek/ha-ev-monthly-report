import voluptuous as vol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from homeassistant import config_entries
from .const import DEFAULT_URL, DOMAIN
from .coordinator import validate_backend_url


class EnergyLedgerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            try:
                user_input["url"] = validate_backend_url(user_input["url"])
                if not all(user_input[key].strip() for key in ("read_token", "write_token", "signing_secret")):
                    raise ValueError
                if not user_input["vehicle_name"].strip() or not user_input["timezone"].strip():
                    raise ValueError
                ZoneInfo(user_input["timezone"].strip())
                user_input["timezone"] = user_input["timezone"].strip()
                return self.async_create_entry(title=f"{user_input['vehicle_name'].strip()} · mesečno poročilo", data=user_input)
            except (ValueError, ZoneInfoNotFoundError):
                errors["base"] = "invalid_config"
        schema = vol.Schema({
            vol.Required("url", default=DEFAULT_URL): str,
            vol.Required("vehicle_name", default="Audi e-tron"): str,
            vol.Required("timezone", default=self.hass.config.time_zone): str,
            vol.Optional("odometer_entity", default=""): str,
            vol.Optional("home_energy_statistic", default=""): str,
            vol.Required("read_token"): str,
            vol.Required("write_token"): str,
            vol.Required("signing_secret"): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
