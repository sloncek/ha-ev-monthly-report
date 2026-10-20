"""Sync the user-mapped odometer only when HA has a month-end observation."""
import calendar
from datetime import datetime
from zoneinfo import ZoneInfo

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event


async def async_register_odometer(hass, coordinator, entry):
    entity_id = coordinator.config.get("odometer_entity", "").strip()
    if not entity_id:
        return lambda: None

    async def send(state):
        if state is None or state.state in {"unknown", "unavailable"}:
            return
        try:
            km = int(float(state.state))
            if km < 0 or str(float(state.state)) != str(float(km)):
                return
            timezone_name = coordinator.config.get("timezone", hass.config.time_zone)
            observed = state.last_updated.astimezone(ZoneInfo(timezone_name))
            last_day = calendar.monthrange(observed.year, observed.month)[1]
            if observed.day != last_day:
                return
            month = observed.strftime("%Y-%m")
            await coordinator.request("POST", f"/api/v1/months/{month}/odometer",
                                      json={"odometer_km": km, "observed_at": state.last_updated.isoformat(), "source": "ha_entity"})
        except (TypeError, ValueError):
            return
        except Exception as exc:
            __import__("logging").getLogger(__name__).warning("HA odometer sync deferred: %s", type(exc).__name__)

    @callback
    def changed(_event):
        hass.async_create_task(send(hass.states.get(entity_id)))

    unsubscribe = async_track_state_change_event(hass, [entity_id], changed)
    await send(hass.states.get(entity_id))
    return unsubscribe
