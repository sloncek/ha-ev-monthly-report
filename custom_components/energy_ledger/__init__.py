from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.helpers import entity_registry as er
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN, PLATFORMS
from .migration import async_migrate_entry
from .coordinator import LedgerCoordinator
from .views import LedgerProxyView
from .odometer_sync import async_register_odometer


async def async_setup_entry(hass, entry):
    coordinator = LedgerCoordinator(hass, entry)
    await coordinator.async_initialize()
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await coordinator.async_stop()
        raise
    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, coordinator.async_stop))
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(await async_register_odometer(hass, coordinator, entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    if not hass.data[DOMAIN].get("panel_registered"):
        panel_dir = Path(__file__).parent / "www"
        panel_url = f"/{DOMAIN}/energy_ledger_panel.js"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(panel_url, str(panel_dir / "energy_ledger_panel.js"), False)]
        )
        hass.http.register_view(LedgerProxyView)
        await panel_custom.async_register_panel(
            hass,
            webcomponent_name="energy-ledger-native-panel",
            frontend_url_path="energy-ledger",
            module_url=f"{panel_url}?v=0.4.1",
            sidebar_title=f"{coordinator.vehicle_name} · mesečno poročilo",
            sidebar_icon="mdi:car-electric",
            require_admin=True,
            config={
                "shadow": True,
                "vehicle_name": coordinator.vehicle_name,
                "odometer_entity": coordinator.config.get("odometer_entity", ""),
                "month_entity": er.async_get(hass).async_get_entity_id(
                    "select", DOMAIN, "energy_ledger_report_month"
                ) or "select.energy_ledger_report_month",
            },
        )
        hass.data[DOMAIN]["panel_registered"] = True
    return True


async def async_unload_entry(hass, entry):
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_stop()
    return ok


async def _async_options_updated(hass, entry):
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator and any(
        coordinator.config.get(key) != {**entry.data, **entry.options}.get(key)
        for key in ("vehicle_name", "timezone", "odometer_entity", "home_energy_statistic",
                    "allowance_km", "contract_end_month", "moj_elektro_usage_point", "moj_elektro_token")
    ):
        await hass.config_entries.async_reload(entry.entry_id)
