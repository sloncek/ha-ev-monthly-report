"""Per-instance mileage forecast built only from this ledger's own odometer readings."""
import calendar
import json
import re
import statistics
from datetime import datetime
from zoneinfo import ZoneInfo

from .ev_register import month_valid


def _add_month(month, amount=1):
    year, number = map(int, month.split("-"))
    index = year * 12 + number - 1 + amount
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def _is_month_end(row, timezone_name):
    if row.get("odometer_source") == "legacy_manual" and re.fullmatch(r"[a-f0-9]{64}", row.get("source_sha256") or ""):
        # Explicitly reviewed monthly readings retain their original provenance.
        return True
    try:
        observed = datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
        local = observed.astimezone(ZoneInfo(timezone_name))
        year, month = map(int, row["year_month"].split("-"))
        return local.strftime("%Y-%m") == row["year_month"] and local.day == calendar.monthrange(year, month)[1]
    except (AttributeError, ValueError, TypeError):
        return False


def get_mileage_forecast(db, month=None, timezone_name="UTC", plan=None, now=None):
    """Forecast this vehicle only; no seeded or cross-vehicle history is used.

    At least three consecutive measured monthly distances are required. An
    optional plan contains only user-supplied ``allowance_km`` and
    ``contract_end_month`` values.
    """
    tz = ZoneInfo(timezone_name)
    clock = now or datetime.now(tz)
    if clock.tzinfo is None:
        clock = clock.replace(tzinfo=tz)
    selected = month or clock.astimezone(tz).strftime("%Y-%m")
    month_valid(selected)
    current = clock.astimezone(tz).strftime("%Y-%m")
    with db.connect() as conn:
        rows = [dict(row) for row in conn.execute(
            "SELECT year_month,odometer_km,odometer_source,observed_at,source_sha256 FROM ev_register_month WHERE odometer_km IS NOT NULL ORDER BY year_month"
        )]
    readings, rejected = {}, []
    for row in rows:
        if row["year_month"] >= current or not _is_month_end(row, timezone_name):
            rejected.append(row["year_month"])
            continue
        readings[row["year_month"]] = int(row["odometer_km"])
    measured = []
    for read_month, odometer in sorted(readings.items()):
        previous = _add_month(read_month, -1)
        if previous in readings:
            distance = odometer - readings[previous]
            if distance >= 0:
                measured.append({"month": read_month, "km": distance})
            else:
                rejected.append(read_month)
    history = [row for row in measured if row["month"] <= selected]
    train = history[-12:]
    average = statistics.mean(row["km"] for row in train) if len(train) >= 3 else None
    anchor_month = max(readings, default=None)
    anchor_km = readings.get(anchor_month) if anchor_month else None
    if not isinstance(plan, dict):
        with db.connect() as conn:
            saved = conn.execute("SELECT payload_json FROM ev_fleet_plan WHERE id=1").fetchone()
        if saved:
            imported = json.loads(saved[0])
            months = [item.get("month", "") for item in imported.get("months", []) if isinstance(item, dict)]
            valid_months = [value for value in months if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value)]
            plan = {"allowance_km": imported.get("allowance_km"), "contract_end_month": max(valid_months, default="")}
    plan = plan if isinstance(plan, dict) else {}
    try:
        allowance = int(plan["allowance_km"]) if plan.get("allowance_km") is not None else None
        if allowance is not None and allowance < 0:
            allowance = None
    except (ValueError, TypeError):
        allowance = None
    contract_end = plan.get("contract_end_month")
    try:
        month_valid(contract_end)
    except (ValueError, TypeError):
        contract_end = None
    forecast, final = [], {}
    if average is not None and anchor_month and anchor_km is not None:
        horizon_end = contract_end or _add_month(anchor_month, 12)
        target, cumulative = _add_month(anchor_month), anchor_km
        while target <= horizon_end and len(forecast) < 600:
            cumulative += round(average)
            variance = None if allowance is None else cumulative - allowance
            forecast.append({"month": target, "predicted_distance_km": round(average),
                             "predicted_odometer_km": cumulative,
                             "allowed_odometer_km": allowance, "variance_km": variance})
            target = _add_month(target)
        if forecast:
            last = forecast[-1]
            final = {"month": last["month"], "predicted_odometer_km": last["predicted_odometer_km"],
                     "allowance_km": allowance,
                     "excess_km": None if allowance is None else max(0, last["predicted_odometer_km"] - allowance)}
    comparisons = []
    for actual in history:
        previous = [row["km"] for row in history if row["month"] < actual["month"]]
        expected = statistics.mean(previous[-12:]) if len(previous) >= 3 else None
        baseline = statistics.mean([row["km"] for row in history if row["month"] <= actual["month"]][-12:])
        delta = None if expected is None else actual["km"] - expected
        comparisons.append({"month": actual["month"], "actual_distance_km": actual["km"],
                            "expected_distance_km": None if expected is None else round(expected, 1),
                            "delta_forecast_km": None if delta is None else round(delta, 1),
                            "delta_forecast_pct": None if not expected else round(delta / expected * 100, 2),
                            "forecast_reference_months": len(previous),
                            "average_distance_km": round(baseline, 1),
                            "delta_average_km": round(actual["km"] - baseline, 1),
                            "delta_average_pct": None if not baseline else round((actual["km"] - baseline) / baseline * 100, 2),
                            "comparison_kind": "retrospective_prior_instance_history"})
    return {"available": average is not None and bool(forecast),
            "model": "single_vehicle_previous_12_month_mean", "month": selected,
            "timezone": timezone_name, "anchor_month": anchor_month,
            "anchor_odometer_km": anchor_km, "historical_months": len(history),
            "average_monthly_km": None if average is None else round(average, 1),
            "history_comparison": comparisons, "rejected_readings": sorted(set(rejected)),
            "months": forecast, "final": final,
            "contract_basis": "user_configured" if allowance is not None and contract_end else None,
            "financial_snapshots_modified": False}
