"""Preserve existing credentials and user mappings when upgrading old entries."""


async def async_migrate_entry(hass, entry):
    if entry.version > 3:
        return False
    if entry.version < 3:
        data = dict(entry.data)
        data.setdefault("vehicle_name", "EV")
        data.setdefault("timezone", hass.config.time_zone)
        data.setdefault("odometer_entity", "")
        data.setdefault("home_energy_statistic", "")
        hass.config_entries.async_update_entry(entry, data=data, version=3)
    return True
