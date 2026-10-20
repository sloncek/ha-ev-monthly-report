from datetime import datetime

from energy_ledger.db import Database
from energy_ledger.ev_register import get_register
from energy_ledger.mileage_forecast import get_mileage_forecast
# Load the pure calculation module without importing the HA runtime package.
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_usage_spec = spec_from_file_location(
    "monthly_usage", Path(__file__).parents[1] / "custom_components/energy_ledger/monthly_usage.py"
)
_usage_module = module_from_spec(_usage_spec)
_usage_spec.loader.exec_module(_usage_module)
usage_payload = _usage_module.usage_payload


def database(tmp_path):
    db = Database(tmp_path / "ledger.sqlite3", __import__("pathlib").Path(__file__).parents[1] / "migrations")
    db.migrate()
    return db


def test_forecast_uses_only_this_instance_month_end_readings(tmp_path):
    db = database(tmp_path)
    with db.transaction() as conn:
        for month, km, observed in [
            ("2025-12", 10000, "2025-12-31T12:00:00+01:00"),
            ("2026-01", 10300, "2026-01-31T12:00:00+01:00"),
            ("2026-02", 10650, "2026-02-28T12:00:00+01:00"),
            ("2026-03", 11000, "2026-03-31T12:00:00+02:00"),
        ]:
            conn.execute(
                "INSERT INTO ev_register_month(year_month,odometer_km,observed_at,odometer_source,updated_at) VALUES(?,?,?,?,?)",
                (month, km, observed, "ha_entity", observed),
            )
    result = get_mileage_forecast(
        db, "2026-03", "Europe/Ljubljana",
        {"allowance_km": 20000, "contract_end_month": "2026-06"},
        datetime.fromisoformat("2026-04-02T12:00:00+02:00"),
    )
    assert result["available"] is True
    assert result["anchor_odometer_km"] == 11000
    assert result["historical_months"] == 3
    assert result["months"][0]["month"] == "2026-04"
    assert result["final"]["allowance_km"] == 20000
    assert result["final"]["excess_km"] == 0


def test_forecast_is_unavailable_without_instance_history(tmp_path):
    result = get_mileage_forecast(database(tmp_path), "2026-03", "Europe/Ljubljana", None,
                                  datetime.fromisoformat("2026-04-02T12:00:00+02:00"))
    assert result["available"] is False
    assert result["historical_months"] == 0
    assert result["history_comparison"] == []
    assert result["final"] == {}


def test_reimbursement_rate_has_no_bundled_default(tmp_path):
    db = database(tmp_path)
    db.ensure_month("2026-03", "Europe/Ljubljana")
    with db.transaction() as conn:
        conn.execute(
            "INSERT INTO home_month_usage(year_month,energy_wh,source,quality,detail_json,updated_at) VALUES(?,?,?,?,?,?)",
            ("2026-03", 10000, "test-recorder", "complete", '{"month_complete":true}', "test"),
        )
    report = get_register(db, "2026-03")
    assert report["home_kwh"] == "10.000"
    assert report["reimbursement_rate"] is None
    assert report["home_reimbursement_eur"] is None


def test_home_usage_payload_uses_configured_timezone_and_statistic():
    from datetime import timezone
    start = int(datetime.fromisoformat("2026-03-01T00:00:00+01:00").astimezone(timezone.utc).timestamp())
    rows = [{"start": start - 3600, "sum": 1.0}, {"start": start, "sum": 1.25}]
    now = datetime.fromisoformat("2026-03-01T01:00:00+01:00").astimezone(timezone.utc)
    result = usage_payload("2026-03", rows, "sensor.ev_home_energy_total", "Europe/Ljubljana", now)
    assert result["source"] == "ha-recorder:sensor.ev_home_energy_total"
    assert result["energy_wh"] == 250
    assert result["quality"] == "complete"


def test_entry_migration_preserves_credentials_and_user_mappings():
    import asyncio
    from types import SimpleNamespace
    spec = spec_from_file_location(
        "ledger_migration", Path(__file__).parents[1] / "custom_components/energy_ledger/migration.py"
    )
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    updates = []
    hass = SimpleNamespace(
        config=SimpleNamespace(time_zone="Europe/Ljubljana"),
        config_entries=SimpleNamespace(async_update_entry=lambda entry, **kwargs: updates.append(kwargs)),
    )
    data = {"url": "http://backend:8099", "read_token": "test-read",
            "write_token": "test-write", "signing_secret": "test-signing",
            "vehicle_name": "Test EV", "odometer_entity": "sensor.test_odometer",
            "home_energy_statistic": "sensor.test_energy"}
    entry = SimpleNamespace(version=2, data=data)
    assert asyncio.run(module.async_migrate_entry(hass, entry)) is True
    assert updates == [{"data": {**data, "timezone": "Europe/Ljubljana"}, "version": 3}]
    assert "timezone" not in data
    updates.clear()
    entry.version = 4
    assert asyncio.run(module.async_migrate_entry(hass, entry)) is False
    assert updates == []
