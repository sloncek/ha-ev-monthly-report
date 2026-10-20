"""Migrate service-based entries without retaining obsolete API credentials."""


async def async_migrate_entry(hass, entry):
    if entry.version > 4:
        return False
    if entry.version < 4:
        data = dict(entry.data)
        for key in ("url", "read_token", "write_token", "signing_secret"):
            data.pop(key, None)
        data.setdefault("vehicle_name", "EV")
        data.setdefault("timezone", hass.config.time_zone)
        data.setdefault("odometer_entity", "")
        data.setdefault("home_energy_statistic", "")
        hass.config_entries.async_update_entry(entry, data=data, version=4)
    return True
