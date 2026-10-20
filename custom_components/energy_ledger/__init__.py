from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN, PLATFORMS
from .coordinator import LedgerCoordinator
from .views import LedgerProxyView
from .odometer_sync import async_register_odometer


async def async_setup_entry(hass, entry):
    coordinator = LedgerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
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
            webcomponent_name="energy-ledger-panel",
            frontend_url_path="energy-ledger",
            module_url=f"{panel_url}?v=0.3.1",
            sidebar_title=f"{entry.data.get('vehicle_name', 'EV')} · mesečno poročilo",
            sidebar_icon="mdi:car-electric",
            require_admin=True,
            config={"shadow": True, "vehicle_name": entry.data.get("vehicle_name", "EV")},
        )
        hass.data[DOMAIN]["panel_registered"] = True
    return True


async def async_unload_entry(hass, entry):
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return ok
