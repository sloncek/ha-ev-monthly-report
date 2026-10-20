"""Sync reset-aware monthly EV energy from a user-mapped HA recorder statistic."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo


def month_bounds(month, timezone_name):
    year, number = map(int, month.split("-"))
    start = datetime(year, number, 1, tzinfo=ZoneInfo(timezone_name))
    end = datetime(year + (number == 12), 1 if number == 12 else number + 1, 1, tzinfo=start.tzinfo)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def usage_payload(month, rows, statistic, timezone_name, now=None):
    start, end = month_bounds(month, timezone_name)
    now = now or datetime.now(timezone.utc)
    end = min(end, now.replace(minute=0, second=0, microsecond=0))
    expected = max(0, int((end - start).total_seconds() / 3600))
    by_time = {int(row["start"]): row for row in rows if row.get("sum") is not None}
    before = by_time.get(int((start - timedelta(hours=1)).timestamp()))
    final = by_time.get(int((end - timedelta(hours=1)).timestamp())) if expected else None
    present = sum(int(start.timestamp()) <= key < int(end.timestamp()) for key in by_time)
    energy = None
    if before is not None and final is not None:
        delta = Decimal(str(final["sum"])) - Decimal(str(before["sum"]))
        if delta >= 0:
            energy = int((delta * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    quality = "complete" if energy is not None and present == expected and expected > 0 else "partial" if energy is not None else "missing"
    return {"energy_wh": energy, "source": f"ha-recorder:{statistic}", "quality": quality,
            "detail": {"expected_hours": expected, "observed_hours": present,
                       "missing_hours": max(0, expected - present), "period_start": start.isoformat(),
                       "period_end": end.isoformat(), "baseline_sum_kwh": None if before is None else before["sum"],
                       "final_sum_kwh": None if final is None else final["sum"],
                       "method": "recorder-reset-aware-counter-delta",
                       "month_complete": now >= month_bounds(month, timezone_name)[1]}}


async def async_sync_month(hass, coordinator, month):
    statistic = coordinator.config.get("home_energy_statistic", "").strip()
    timezone_name = coordinator.config.get("timezone", hass.config.time_zone)
    if not statistic:
        return
    from homeassistant.components.recorder import get_instance
    from homeassistant.components.recorder.statistics import statistics_during_period
    start, end = month_bounds(month, timezone_name)
    try:
        result = await get_instance(hass).async_add_executor_job(
            statistics_during_period, hass, start - timedelta(hours=1), end,
            {statistic}, "hour", {"energy": "kWh"}, {"sum"})
        payload = usage_payload(month, result.get(statistic, []), statistic, timezone_name)
    except Exception as exc:
        __import__("logging").getLogger(__name__).warning("HA recorder energy history deferred for %s: %s", month, type(exc).__name__)
        payload = usage_payload(month, [], statistic, timezone_name)
    await coordinator.request("POST", f"/api/v1/months/{month}/home-usage", json=payload)
