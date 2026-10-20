"""In-process calculation and invoice engine; never exposed as a server."""
import asyncio
import contextlib
import csv
import hashlib
import hmac
import time
import io
import json
import logging
import os
import re
import shutil
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from zoneinfo import ZoneInfo
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from . import __version__
from .db import Database, utcnow
from .mojelektro_service import MojElektroService
from .invoice_pipeline import InvoicePipeline
from . import ev_register
from . import mileage_forecast

_LOGGER = logging.getLogger(__name__)

def create_app(data_dir: Path, config: dict):
    """Build an instance-local engine used only through an in-memory transport.

    No server is started and no network port is opened. Home Assistant owns
    authentication, executor scheduling, startup and shutdown.
    """
    from types import SimpleNamespace
    data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    data_dir.chmod(0o700)
    for name in ("evidence", "inbox", "outbox", "backups", "reports"):
        (data_dir / name).mkdir(parents=True, exist_ok=True, mode=0o700)
    settings = SimpleNamespace(data_dir=data_dir, config=config,
        timezone=config.get("timezone", "UTC"), vehicle_name=config.get("vehicle_name", "EV"),
        shadow_mode=True)
    db = Database(data_dir / "ledger.sqlite3", Path(__file__).parent / "migrations", settings.timezone)
    db.migrate()
    db.ensure_month(datetime.now(ZoneInfo(settings.timezone)).strftime("%Y-%m"))
    db.path.chmod(0o600)
    @contextlib.asynccontextmanager
    async def lifespan(_app):
        await _start_automation()
        try:
            yield
        finally:
            await _stop_automation()

    app = FastAPI(lifespan=lifespan, title="Energy Ledger local engine", version=__version__,
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.state.ledger_db = db
    invoice_pipeline = InvoicePipeline(db)
    _outbox_lock = threading.Lock()
    _automation_task = None

    def auth_read():
        return "home-assistant"

    def auth_write(x_ha_user: Optional[str] = Header(default=None)):
        return x_ha_user or "ha-system"

    def _hash_file(path: Path) -> tuple[str, int]:
        h = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                size += len(chunk)
                h.update(chunk)
        return h.hexdigest(), size

    def _save_evidence(temp: Path, original_name: str, media_type: str) -> tuple[int, str]:
        digest, size = _hash_file(temp)
        if size <= 0 or size > 15 * 1024 * 1024:
            raise HTTPException(413, "evidence must be between 1 byte and 15 MiB")
        final = settings.data_dir / "evidence" / digest[:2] / digest
        final.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        final.parent.chmod(0o700)
        if not final.exists():
            os.replace(temp, final)
            final.chmod(0o600)
        elif temp.exists():
            temp.unlink()
        with db.transaction() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO evidence(sha256,media_type,size_bytes,original_name,storage_path,created_at) VALUES(?,?,?,?,?,?)",
                (digest, media_type, size, original_name, str(final), utcnow()),
            )
            row = conn.execute("SELECT id FROM evidence WHERE sha256=?", (digest,)).fetchone()
            return int(row[0]), digest

    def _consume_outbox_unlocked() -> None:
        for result_path in sorted((settings.data_dir / "outbox").glob("*.json")):
            result = json.loads(result_path.read_text())
            job_id = result_path.stem
            if result.get("error"):
                state = "REVIEW" if result.get("status") == "REVIEW" else "REJECTED"
                suffix = ".review" if state == "REVIEW" else ".rejected"
                with db.transaction() as conn:
                    conn.execute("UPDATE invoice_import_job SET state=?,detail=?,updated_at=? WHERE job_id=?",
                                 (state, json.dumps({"error": result.get("error"), "detail": result.get("detail")}, sort_keys=True), utcnow(), job_id))
                result_path.rename(result_path.with_suffix(suffix))
                (settings.data_dir / "inbox" / f"{job_id}.pdf").unlink(missing_ok=True)
                continue
            data = result["invoice"]
            invoice_id = None
            with db.transaction() as conn:
                evidence = conn.execute("SELECT id FROM evidence WHERE sha256=?", (result["sha256"],)).fetchone()
                if not evidence:
                    continue
                duplicate = conn.execute("SELECT id,evidence_id FROM invoice WHERE supplier=? AND invoice_number=?", (data["supplier"],data["invoice_number"])).fetchone()
                if duplicate and duplicate["evidence_id"] != evidence[0]:
                    conn.execute("UPDATE invoice_import_job SET state='CONFLICT',detail=?,updated_at=? WHERE job_id=?",
                                 (json.dumps({"error":"invoice_number_conflict"}), utcnow(), job_id))
                    result_path.rename(result_path.with_suffix(".conflict"))
                    continue
                conn.execute(
                    "INSERT OR IGNORE INTO invoice(supplier,invoice_number,period_start_utc,period_end_utc,peak_wh,offpeak_wh,electricity_wh,electricity_net_micro_eur,gas_millim3,gas_wh,gas_net_micro_eur,net_micro_eur,vat_basis_points,vat_micro_eur,gross_micro_eur,evidence_id,parser_version,parse_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'VALID')",
                    (data["supplier"],data["invoice_number"],data["period_start"],data["period_end"],data["peak_wh"],data["offpeak_wh"],data["electricity_wh"],data["electricity_net_micro_eur"],data["gas_millim3"],data["gas_wh"],data["gas_net_micro_eur"],data["net_micro_eur"],data["vat_basis_points"],data["vat_micro_eur"],data["gross_micro_eur"],evidence[0],data["parser_version"]),
                )
                invoice_id = int(conn.execute(
                    "SELECT id FROM invoice WHERE supplier=? AND invoice_number=?",
                    (data["supplier"], data["invoice_number"]),
                ).fetchone()[0])
            month = invoice_pipeline.enqueue(invoice_id, data["period_start"])
            with db.transaction() as conn:
                conn.execute("UPDATE invoice_import_job SET state='VALID',invoice_id=?,year_month=?,detail=?,updated_at=? WHERE job_id=?",
                             (invoice_id, month, json.dumps({"parser_version":data["parser_version"]}, sort_keys=True), utcnow(), job_id))
            result_path.rename(result_path.with_suffix(".done"))
            (settings.data_dir / "inbox" / f"{job_id}.pdf").unlink(missing_ok=True)

    def _consume_outbox() -> None:
        with _outbox_lock:
            _consume_outbox_unlocked()

    def _month_row(month: str):
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
            raise HTTPException(422, "month must be YYYY-MM")
        try:
            rid = db.ensure_month(month, settings.timezone)
        except ValueError:
            raise HTTPException(422, "invalid calendar month")
        with db.connect() as conn:
            return conn.execute("SELECT * FROM month_revision WHERE id=?", (rid,)).fetchone()

    def _eur(value: int | None) -> str | None:
        return None if value is None else str((Decimal(value)/Decimal(1_000_000)).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))

    def _ha_connected() -> bool:
        with db.connect() as conn:
            row = conn.execute("SELECT value_json,updated_at FROM runtime_state WHERE key='ha_heartbeat'").fetchone()
        if not row:
            return False
        try:
            updated = datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")).astimezone(timezone.utc)
            return datetime.now(timezone.utc) - updated <= timedelta(minutes=3)
        except (TypeError, ValueError):
            return False

    def _register_delta(conn:sqlite3.Connection,meter_hash:str | None,reading_type:str,start:str,end:str) -> int | None:
        if not meter_hash:
            return None
        rows=conn.execute(
            "SELECT value_wh FROM meter_register_latest WHERE meter_key_hash=? AND reading_type=? AND observed_utc>=? AND observed_utc<=? ORDER BY observed_utc",
            (meter_hash,reading_type,start,end),
        ).fetchall()
        if len(rows)<2:
            return None
        delta=int(rows[-1][0])-int(rows[0][0])
        return delta if delta>=0 else None

    def summary(month: str) -> dict:
        _consume_outbox()
        row = _month_row(month)
        usage_point=settings.config.get("moj_elektro",{}).get("usage_point")
        meter_hash=hashlib.sha256(usage_point.encode()).hexdigest() if usage_point else None
        with db.connect() as conn:
            invoice = conn.execute("SELECT * FROM invoice WHERE period_start_utc=? ORDER BY id DESC LIMIT 1", (row["period_start_utc"],)).fetchone()
            home = conn.execute("SELECT COALESCE(SUM(energy_wh),0),COUNT(*) FROM charge_session WHERE state='CLOSED' AND datetime(started_at)>=datetime(?) AND datetime(started_at)<datetime(?)", (row["period_start_utc"],row["period_end_utc"])).fetchone()
            public = conn.execute("SELECT COALESCE(SUM(energy_wh),0),COALESCE(SUM(gross_micro_eur),0),COALESCE(SUM(CASE WHEN claimable=1 THEN gross_micro_eur ELSE 0 END),0),COUNT(*),COALESCE(SUM(CASE WHEN evidence_id IS NULL THEN 1 ELSE 0 END),0) FROM public_charge WHERE datetime(started_at)>=datetime(?) AND datetime(started_at)<datetime(?) AND verification_state!='VOID'", (row["period_start_utc"],row["period_end_utc"])).fetchone()
            rec = conn.execute("SELECT * FROM reconciliation WHERE month_revision_id=? AND dimension='total'", (row["id"],)).fetchone()
            grid_peak_wh=_register_delta(conn,meter_hash,"peak",row["period_start_utc"],row["period_end_utc"])
            grid_offpeak_wh=_register_delta(conn,meter_hash,"offpeak",row["period_start_utc"],row["period_end_utc"])
            report = conn.execute("SELECT id FROM report_artifact WHERE month_revision_id=? ORDER BY id DESC LIMIT 1", (row["id"],)).fetchone()
            pipeline = conn.execute(
                "SELECT p.* FROM invoice_pipeline p JOIN invoice i ON i.id=p.invoice_id "
                "WHERE p.year_month=? ORDER BY i.id DESC LIMIT 1", (month,),
            ).fetchone()
            usage = conn.execute("SELECT * FROM home_month_usage WHERE year_month=?", (month,)).fetchone()
            vat_setting = conn.execute("SELECT * FROM vat_rate_schedule WHERE effective_month<=? ORDER BY effective_month DESC LIMIT 1", (month,)).fetchone()
            latest_import = conn.execute("SELECT job_id,invoice_id,year_month,state,detail,updated_at FROM invoice_import_job ORDER BY created_at DESC LIMIT 1").fetchone()
            latest_pipeline = conn.execute("SELECT state,detail,last_error,retryable,next_attempt_at FROM invoice_pipeline WHERE invoice_id=?",(latest_import['invoice_id'],)).fetchone() if latest_import and latest_import['invoice_id'] else None
        issue_count = 0 if rec and rec["result"] == "PASS" else 1
        if row["state"] == "LOCKED": status = "locked"
        elif settings.shadow_mode: status = "needs_review"
        elif rec and rec["result"] == "FAIL": status = "mismatch"
        elif rec and rec["result"] == "PASS": status = "ready"
        elif invoice: status = "needs_review"
        else: status = "draft"
        bill_wh = invoice["electricity_wh"] if invoice else None
        measured_wh = rec["measured_wh"] if rec else None
        delta_wh = rec["delta_wh"] if rec else None
        pct = None if delta_wh is None or not bill_wh else f"{(delta_wh / bill_wh) * 100:.3f}"
        public_wh, public_paid, public_claimable = int(public[0]), int(public[1]), int(public[2])
        # Recorder's reset-aware counter is the month source. Session rows alone
        # cannot prove that a whole month was observed and must not fabricate zero.
        home_wh = usage["energy_wh"] if usage else None
        usage_detail = json.loads(usage["detail_json"]) if usage else {}
        # Full provider evidence stays in the ledger, not in every frontend state.
        usage_detail.pop("history_rows", None)
        vat_bp = vat_setting["basis_points"] if vat_setting else (invoice["vat_basis_points"] if invoice else None)
        home_net = home_gross = None
        unit_net = unit_gross = None
        if invoice and invoice["electricity_wh"] > 0:
            unit_net = Decimal(invoice["electricity_net_micro_eur"]) / Decimal(1000 * invoice["electricity_wh"])
            unit_gross = unit_net * Decimal(10000 + vat_bp) / Decimal(10000)
            if home_wh is not None:
                base = Decimal(home_wh) * Decimal(invoice["electricity_net_micro_eur"]) / Decimal(invoice["electricity_wh"])
                home_net = int(base.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
                home_gross = int((base * Decimal(10000 + vat_bp) / Decimal(10000)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        pipeline_state = pipeline["state"] if pipeline else None
        processing = pipeline_state in {"PENDING", "RUNNING"}
        pipeline_error = pipeline["last_error"] if pipeline and pipeline_state == "ERROR" else None
        pipeline_retryable = bool(pipeline["retryable"]) if pipeline else False
        if pipeline_error:
            primary_issue = "automatic_processing_error"
            next_action = "automatic_retry_scheduled" if pipeline_retryable else "check_moj_elektro_credentials"
        elif pipeline_state == "INCOMPLETE":
            primary_issue, next_action = "waiting_for_complete_meter_data", "automatic_retry_scheduled"
        elif settings.shadow_mode:
            primary_issue, next_action = "shadow_exit_gates_not_passed", "complete_shadow_exit_gates"
        else:
            primary_issue = None if issue_count == 0 else "reconciliation_incomplete"
            next_action = "reconcile"
        from .import_progress import import_progress
        latest_progress = import_progress(dict(latest_import),dict(latest_pipeline) if latest_pipeline else None) if latest_import else None
        return {
            "schema_version": 1, "month": month, "status": status,
            "register": ev_register.get_register(db,month),
            "mileage_forecast": mileage_forecast.get_mileage_forecast(db,month,settings.timezone,settings.config.get("mileage_plan")),
            "primary_issue": primary_issue, "next_action": next_action,
            "processing": processing, "pipeline_status": pipeline_state, "pipeline_error": pipeline_error,
            "latest_import_progress":latest_progress, "latest_import_month":latest_import['year_month'] if latest_import else None,
            "pipeline_attempts": int(pipeline["attempts"]) if pipeline else 0,
            "pipeline_retryable": pipeline_retryable,
            "pipeline_next_attempt": pipeline["next_attempt_at"] if pipeline and pipeline_state in {"INCOMPLETE", "ERROR"} and pipeline_retryable else None,
            "row_version": row["row_version"], "report_id": report[0] if report else None,
            "supersedes_report_id": row["supersedes_revision_id"], "updated_at": utcnow(),
            "data_quality": "shadow" if settings.shadow_mode else ("verified" if issue_count == 0 else "incomplete"),
            "issue_count": issue_count, "last_sync": utcnow(),
            "bill_kwh": None if bill_wh is None else f"{bill_wh/1000:.3f}",
            "bill_peak_kwh": None if not invoice else f"{invoice['peak_wh']/1000:.3f}",
            "bill_offpeak_kwh": None if not invoice else f"{invoice['offpeak_wh']/1000:.3f}",
            "bill_net": None if not invoice else _eur(invoice["net_micro_eur"]),
            "bill_vat": None if not invoice else _eur(invoice["vat_micro_eur"]),
            "bill_gross": None if not invoice else _eur(invoice["gross_micro_eur"]),
            "grid_kwh": None if measured_wh is None else f"{measured_wh/1000:.3f}",
            "grid_peak_kwh": None if grid_peak_wh is None else f"{grid_peak_wh/1000:.3f}", "grid_offpeak_kwh": None if grid_offpeak_wh is None else f"{grid_offpeak_wh/1000:.3f}",
            **{f"grid_block_{i}": None for i in range(1,6)},
            "variance_kwh": None if delta_wh is None else f"{delta_wh/1000:.3f}", "variance_pct": pct,
            "home_kwh": None if home_wh is None else f"{home_wh/1000:.3f}", "home_cost": _eur(home_gross), "home_session_count": int(home[1]),
            "home_cost_net": _eur(home_net),
            # Allocate cent rounding to VAT so displayed net + VAT = gross.
            "home_vat_cost": None if home_net is None else f"{Decimal(_eur(home_gross))-Decimal(_eur(home_net)):.2f}",
            "vat_rate_pct": None if vat_bp is None else f"{vat_bp/100:.2f}", "vat_rate_source": "nastavitev" if vat_setting else "račun" if invoice else None,
            "vat_effective_month": vat_setting["effective_month"] if vat_setting else None,
            "electricity_price_net": None if unit_net is None else f"{unit_net:.6f}",
            "electricity_price_gross": None if unit_gross is None else f"{unit_gross:.6f}",
            "home_data_quality": usage["quality"] if usage else "missing", "home_data_source": usage["source"] if usage else None,
            "home_missing_hours": usage_detail.get("missing_hours"), "home_expected_hours": usage_detail.get("expected_hours"),
            "home_data_detail": usage_detail,
            "latest_import_state": latest_import["state"] if latest_import else None,
            "latest_import_detail": json.loads(latest_import["detail"]) if latest_import and latest_import["detail"] else None,
            "public_kwh": f"{public_wh/1000:.3f}", "public_paid_cost": _eur(public_paid),
            "public_reimbursable_cost": _eur(public_claimable), "public_session_count": int(public[3]), "missing_evidence_count": int(public[4]),
            "total_kwh": None if home_wh is None else f"{(home_wh+public_wh)/1000:.3f}", "total_cost": _eur(None if home_gross is None else home_gross+public_paid), "reimbursable_cost": _eur(public_claimable),
            "gas_m3": None if not invoice or invoice["gas_millim3"] is None else f"{invoice['gas_millim3']/1000:.3f}",
            "gas_kwh": None if not invoice or invoice["gas_wh"] is None else f"{invoice['gas_wh']/1000:.3f}",
            "gas_gross": None if not invoice or invoice["gas_net_micro_eur"] is None else _eur((invoice["gas_net_micro_eur"] * (10000+invoice["vat_basis_points"]) + 5000)//10000),
            "pricing_method": "invoice-average-electricity-only" if home_gross is not None else "waiting-for-invoice-or-energy", "ready": False if settings.shadow_mode else issue_count == 0,
            "locked": row["state"] == "LOCKED"
        }

    @app.get("/healthz")
    def healthz(): return {"status":"ok","version":__version__,"shadow":settings.shadow_mode}

    class RegisterExpenseInput(BaseModel):
        month: str
        date: str
        kind: str
        provider: str = Field(default="",max_length=200)
        gross_eur: str
        energy_kwh: Optional[str] = None
        eligible: bool = False
        notes: str = Field(default="",max_length=3000)
        idempotency_key: str

    class RegisterReportedInput(BaseModel):
        amount_eur: str
        idempotency_key: str

    class RegisterRateInput(BaseModel):
        rate_eur_per_kwh: str

    class RegisterOdometerInput(BaseModel):
        odometer_km: int = Field(ge=0,le=10000000)
        observed_at: str
        source: str = "manual"

    def _register_call(function,*args):
        try:
            return function(db,*args)
        except ev_register.RegisterError as exc:
            raise HTTPException(exc.status,str(exc))

    @app.get("/api/v1/months/{month}/register",dependencies=[Depends(auth_read)])
    def register_get(month:str):
        return _register_call(ev_register.get_register,month)

    @app.get("/api/v1/months/{month}/mileage-forecast",dependencies=[Depends(auth_read)])
    def mileage_forecast_get(month:str):
        try:
            return mileage_forecast.get_mileage_forecast(db,month,settings.timezone,settings.config.get("mileage_plan"))
        except ev_register.RegisterError as exc:
            raise HTTPException(exc.status,str(exc))

    @app.get("/api/v1/register/history",dependencies=[Depends(auth_read)])
    def register_history():
        return ev_register.history(db)

    @app.post("/api/v1/register/expense",status_code=201)
    def register_expense(data:RegisterExpenseInput,actor:str=Depends(auth_write)):
        return _register_call(ev_register.add_expense,data.model_dump(),actor)

    @app.post("/api/v1/months/{month}/reported")
    def register_reported(month:str,data:RegisterReportedInput,actor:str=Depends(auth_write)):
        return _register_call(ev_register.report_month,month,data.model_dump(),actor)

    @app.post("/api/v1/months/{month}/reimbursement-rate")
    def register_rate(month:str,data:RegisterRateInput,actor:str=Depends(auth_write)):
        return _register_call(ev_register.set_rate,month,data.rate_eur_per_kwh,actor)

    @app.post("/api/v1/months/{month}/odometer")
    def register_odometer(month:str,data:RegisterOdometerInput,actor:str=Depends(auth_write)):
        if data.source not in {"manual","ha_entity"}:
            raise HTTPException(422,"source must be manual or ha_entity")
        return _register_call(ev_register.set_odometer,month,data.model_dump(),actor)

    @app.get("/readyz")
    def readyz():
        migrations=db.migration_status()
        writable=all(os.access(settings.data_dir/name,os.W_OK) for name in ("inbox","outbox","evidence","backups"))
        integrity=db.verify_sqlite(db.path)
        core=bool(writable and migrations["ok"] and integrity["ok"])
        moj_cfg=settings.config.get("moj_elektro",{})
        moj=bool(moj_cfg.get("enabled") and moj_cfg.get("usage_point") and (settings.data_dir / "moj_elektro_token").exists() and (settings.data_dir / "moj_elektro_token").stat().st_size)
        return {"ready":core,"shadow":settings.shadow_mode,"exit_ready":False,"dependencies":{"core":core,"writable_storage":writable,"database_integrity":integrity["ok"],"migration_checksums":migrations["ok"],"moj_elektro":moj,"ha_config_entry":_ha_connected()}}

    @app.get("/api/v1/months", dependencies=[Depends(auth_read)])
    def months():
        now = datetime.now(ZoneInfo(settings.timezone))
        db.ensure_month(now.strftime("%Y-%m"),settings.timezone)
        db.ensure_month((now.replace(day=1)-timedelta(days=1)).strftime("%Y-%m"),settings.timezone)
        with db.connect() as conn:
            month_list=[r[0] for r in conn.execute("SELECT year_month FROM month_head UNION SELECT year_month FROM ev_register_month UNION SELECT year_month FROM home_month_usage ORDER BY year_month DESC")]
            latest=conn.execute("SELECT year_month FROM invoice_pipeline ORDER BY invoice_id DESC LIMIT 1").fetchone()
            return {"months":month_list,"latest_imported_month":latest[0] if latest else None}

    class HomeUsageInput(BaseModel):
        energy_wh: Optional[int] = Field(default=None, ge=0)
        source: str = Field(max_length=160)
        quality: str = Field(pattern="^(complete|partial|missing)$")
        detail: dict = Field(default_factory=dict)

    class VatInput(BaseModel):
        rate_pct: Decimal = Field(ge=0, le=100, decimal_places=2)

    @app.post("/api/v1/months/{month}/home-usage")
    def update_home_usage(month: str, payload: HomeUsageInput, actor: str=Depends(auth_write)):
        row = _month_row(month)
        if row["state"] == "LOCKED": raise HTTPException(409, "month locked")
        if payload.quality == "complete" and payload.energy_wh is None:
            raise HTTPException(422, "complete coverage needs energy")
        with db.transaction() as conn:
            previous=conn.execute("SELECT source,quality,detail_json FROM home_month_usage WHERE year_month=?",(month,)).fetchone()
            if previous and previous["quality"]=="complete" and json.loads(previous["detail_json"]).get("month_complete") and not (payload.quality=="complete" and payload.detail.get("month_complete")):
                return {"month":month,"quality":"complete","retained_complete_history":True}
            conn.execute("INSERT INTO home_month_usage VALUES(?,?,?,?,?,?) ON CONFLICT(year_month) DO UPDATE SET energy_wh=excluded.energy_wh,source=excluded.source,quality=excluded.quality,detail_json=excluded.detail_json,updated_at=excluded.updated_at",
                         (month,payload.energy_wh,payload.source,payload.quality,json.dumps(payload.detail,sort_keys=True),utcnow()))
        return {"month":month,"quality":payload.quality}

    @app.post("/api/v1/months/{month}/vat")
    def update_vat(month: str, payload: VatInput, actor: str=Depends(auth_write)):
        row = _month_row(month)
        # Effective-month changes must never alter an already locked report.
        with db.transaction() as conn:
            if conn.execute("SELECT 1 FROM month_revision WHERE year_month>=? AND state='LOCKED' LIMIT 1",(month,)).fetchone():
                raise HTTPException(409, "VAT change affects locked report")
            bp = int(payload.rate_pct * 100)
            conn.execute("INSERT INTO vat_rate_schedule VALUES(?,?,?,?) ON CONFLICT(effective_month) DO UPDATE SET basis_points=excluded.basis_points,actor=excluded.actor,updated_at=excluded.updated_at", (month,bp,actor,utcnow()))
            db.audit(conn, actor, "vat_rate_changed", "vat_rate_schedule", month, {"effective_month":month,"basis_points":bp})
        return {"effective_month":month,"rate_pct":f"{bp/100:.2f}"}

    @app.get("/api/v1/months/{month}/summary", dependencies=[Depends(auth_read)])
    def month_summary(month: str): return summary(month)

    def _invoice_job_status(job_id=None):
        with db.connect() as conn:
            query="SELECT job_id,state,invoice_id,year_month,detail,created_at,updated_at FROM invoice_import_job"
            row=conn.execute(query+" WHERE job_id=?",(job_id,)).fetchone() if job_id else conn.execute(query+" ORDER BY created_at DESC LIMIT 1").fetchone()
            pipeline=conn.execute("SELECT state,detail,last_error,retryable,next_attempt_at FROM invoice_pipeline WHERE invoice_id=?",(row['invoice_id'],)).fetchone() if row and row['invoice_id'] else None
        if not row: raise HTTPException(404,"invoice job not found")
        from .import_progress import import_progress
        result=dict(row)
        result['progress']=import_progress(result,dict(pipeline) if pipeline else None)
        result['pipeline_state']=pipeline['state'] if pipeline else None
        return result

    @app.get("/api/v1/invoice-jobs/latest", dependencies=[Depends(auth_read)])
    def latest_invoice_job_status():
        return _invoice_job_status()

    @app.get("/api/v1/invoice-jobs/{job_id}", dependencies=[Depends(auth_read)])
    def invoice_job_status(job_id: str):
        return _invoice_job_status(job_id)

    @app.post("/api/v1/invoices", status_code=202)
    async def upload_invoice(file: UploadFile=File(...), idempotency_key: str=Header(alias="Idempotency-Key"), actor: str=Depends(auth_write)):
        if file.content_type != "application/pdf": raise HTTPException(415,"PDF required")
        temp = settings.data_dir / "inbox" / f".{uuid.uuid4().hex}.upload"
        total = 0
        with temp.open("wb") as out:
            while chunk := await file.read(1024*1024):
                total += len(chunk)
                if total > 15*1024*1024: temp.unlink(missing_ok=True); raise HTTPException(413,"PDF too large")
                out.write(chunk)
        if temp.read_bytes()[:5] != b"%PDF-": temp.unlink(missing_ok=True); raise HTTPException(415,"invalid PDF signature")
        evidence_id,digest = _save_evidence(temp,file.filename or "invoice.pdf",file.content_type)
        request_hash = hashlib.sha256(digest.encode()).hexdigest()
        with db.transaction() as conn:
            old = conn.execute("SELECT * FROM idempotency_record WHERE scope='invoice' AND key=?",(idempotency_key,)).fetchone()
            if old:
                if old["request_hash"] != request_hash: raise HTTPException(409,"idempotency conflict")
                return JSONResponse(json.loads(old["response_json"]),status_code=old["response_code"])
            job_id=uuid.uuid4().hex
            shutil.copyfile(settings.data_dir/"evidence"/digest[:2]/digest,settings.data_dir/"inbox"/f"{job_id}.pdf")
            payload={"job_id":job_id,"evidence_id":evidence_id,"sha256":digest,"status":"pending"}
            now=utcnow()
            conn.execute("INSERT INTO invoice_import_job(job_id,evidence_id,state,created_at,updated_at) VALUES(?,?,'PENDING',?,?)",(job_id,evidence_id,now,now))
            conn.execute("INSERT INTO idempotency_record VALUES(?,?,?,?,?,?)",("invoice",idempotency_key,request_hash,202,json.dumps(payload),now))
            db.audit(conn,actor,"invoice_uploaded","evidence",str(evidence_id),{"sha256":digest,"job_id":job_id})
        return payload

    @app.post("/api/v1/public-charges", status_code=201)
    async def public_charge(started_at:str=Form(...),provider:str=Form(...),energy_kwh:str=Form(...),gross_eur:str=Form(...),external_key:str=Form(...),evidence:Optional[UploadFile]=File(default=None),idempotency_key:str=Header(alias="Idempotency-Key"),actor:str=Depends(auth_write)):
        from decimal import Decimal
        try: started_at=datetime.fromisoformat(started_at.replace("Z","+00:00")).astimezone(timezone.utc).isoformat()
        except ValueError as exc: raise HTTPException(422,"invalid started_at") from exc
        energy_wh=int((Decimal(energy_kwh)*1000).quantize(Decimal("1")))
        amount=int((Decimal(gross_eur)*1_000_000).quantize(Decimal("1")))
        evidence_id=None
        if evidence:
            temp=settings.data_dir/"inbox"/f".{uuid.uuid4().hex}.evidence"
            content=await evidence.read(15*1024*1024+1)
            if len(content)>15*1024*1024: raise HTTPException(413,"evidence too large")
            temp.write_bytes(content); evidence_id,_=_save_evidence(temp,evidence.filename or "evidence",evidence.content_type or "application/octet-stream")
        body_hash=hashlib.sha256(f"{started_at}|{provider}|{energy_wh}|{amount}|{external_key}|{evidence_id}".encode()).hexdigest()
        with db.transaction() as conn:
            old=conn.execute("SELECT * FROM idempotency_record WHERE scope='public_charge' AND key=?",(idempotency_key,)).fetchone()
            if old:
                if old["request_hash"]!=body_hash: raise HTTPException(409,"idempotency conflict")
                return JSONResponse(json.loads(old["response_json"]),status_code=old["response_code"])
            cur=conn.execute("INSERT INTO public_charge(external_key,revision,started_at,provider,energy_wh,gross_micro_eur,evidence_id,verification_state,claimable) VALUES(?,1,?,?,?,?,?,?,?)",(external_key,started_at,provider,energy_wh,amount,evidence_id,"UNVERIFIED",0))
            payload={"id":cur.lastrowid,"evidence_present":bool(evidence_id),"verified":False,"claimable":False}
            conn.execute("INSERT INTO idempotency_record VALUES(?,?,?,?,?,?)",("public_charge",idempotency_key,body_hash,201,json.dumps(payload),utcnow()))
            db.audit(conn,actor,"public_charge_created","public_charge",str(cur.lastrowid),payload)
        return payload

    @app.post("/api/v1/public-charges/{charge_id}/verify")
    def verify_public_charge(charge_id:int,actor:str=Depends(auth_write)):
        with db.transaction() as conn:
            row=conn.execute("SELECT * FROM public_charge WHERE id=?",(charge_id,)).fetchone()
            if not row: raise HTTPException(404,"public charge not found")
            if row["evidence_id"] is None: raise HTTPException(409,"evidence is required before verification")
            conn.execute("UPDATE public_charge SET verification_state='VERIFIED',claimable=1 WHERE id=?",(charge_id,))
            db.audit(conn,actor,"public_charge_verified","public_charge",str(charge_id),{"evidence_id":row["evidence_id"]})
        return {"id":charge_id,"verified":True,"claimable":True}

    class HAHeartbeatPayload(BaseModel):
        entry_id: str = Field(min_length=8, max_length=128)

    @app.post("/api/v1/runtime/ha-heartbeat")
    def ha_heartbeat(payload:HAHeartbeatPayload,actor:str=Depends(auth_write)):
        now=utcnow()
        value=json.dumps({"entry_id":payload.entry_id,"actor":actor},sort_keys=True,separators=(",",":"))
        with db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO runtime_state(key,value_json,updated_at) VALUES('ha_heartbeat',?,?)",(value,now))
        return {"accepted":True,"updated_at":now}

    def _backfill_month(month: str) -> dict:
        row=_month_row(month)
        service=MojElektroService(db,settings.data_dir,settings.config.get("moj_elektro",{}),(settings.data_dir / "moj_elektro_token"))
        return service.backfill(row)

    @app.post("/api/v1/months/{month}/backfill-moj-elektro")
    def backfill_moj_elektro(month:str, actor:str=Depends(auth_write)):
        return _backfill_month(month)

    def _reconcile_month(month: str) -> dict:
        row=_month_row(month)
        usage_point=settings.config.get("moj_elektro",{}).get("usage_point")
        meter_hash=hashlib.sha256(usage_point.encode()).hexdigest() if usage_point else None
        with db.transaction() as conn:
            invoice=conn.execute("SELECT electricity_wh,peak_wh,offpeak_wh FROM invoice WHERE period_start_utc=? ORDER BY id DESC LIMIT 1",(row["period_start_utc"],)).fetchone()
            measured=conn.execute("SELECT SUM(energy_wh) FROM meter_interval_latest WHERE meter_key_hash=? AND reading_type='interval' AND start_utc>=? AND end_utc<=?",(meter_hash,row["period_start_utc"],row["period_end_utc"])).fetchone()[0] if meter_hash else None
            measured_values={"total":measured,"peak":_register_delta(conn,meter_hash,"peak",row["period_start_utc"],row["period_end_utc"]),"offpeak":_register_delta(conn,meter_hash,"offpeak",row["period_start_utc"],row["period_end_utc"])}
            invoice_values={"total":invoice["electricity_wh"] if invoice else None,"peak":invoice["peak_wh"] if invoice else None,"offpeak":invoice["offpeak_wh"] if invoice else None}
            results={}
            for dimension in ("total","peak","offpeak"):
                billed=invoice_values[dimension]; actual=measured_values[dimension]
                tolerance=None if billed is None else max(2000,int(billed*.01))
                result="INCOMPLETE" if billed is None or actual is None else ("PASS" if abs(billed-actual)<=tolerance else "FAIL")
                results[dimension]=result
                conn.execute("INSERT OR REPLACE INTO reconciliation(month_revision_id,dimension,invoice_wh,measured_wh,delta_wh,tolerance_wh,result,created_at) VALUES(?,?,?,?,?,?,?,?)",(row["id"],dimension,billed,actual,None if billed is None or actual is None else actual-billed,tolerance,result,utcnow()))
        return {"result":results["total"],"dimensions":results,"shadow":settings.shadow_mode}

    @app.post("/api/v1/months/{month}/reconcile", dependencies=[Depends(auth_write)])
    def reconcile(month:str):
        return _reconcile_month(month)

    @app.post("/api/v1/months/{month}/refresh", dependencies=[Depends(auth_write)])
    def refresh(month:str):
        _consume_outbox()
        invoice_pipeline.enqueue_missing()
        return summary(month)

    def _automation_cycle() -> dict | None:
        from .worker import process_once
        process_once(settings.data_dir / "inbox", settings.data_dir / "outbox", settings.timezone)
        _consume_outbox()
        invoice_pipeline.enqueue_missing()
        return invoice_pipeline.run_one(_backfill_month, _reconcile_month)

    async def _automation_loop() -> None:
        while True:
            try:
                await asyncio.to_thread(_automation_cycle)
            except Exception:
                # A malformed outbox item or temporary database problem must not
                # permanently kill automatic invoice processing.
                _LOGGER.exception("Automatic invoice pipeline cycle failed")
            await asyncio.sleep(5)

    async def _start_automation() -> None:
        nonlocal _automation_task
        _automation_task = asyncio.create_task(_automation_loop(), name="invoice-pipeline")

    async def _stop_automation() -> None:
        nonlocal _automation_task
        if _automation_task:
            _automation_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await _automation_task
            _automation_task = None

    @app.post("/api/v1/months/{month}/lock", dependencies=[Depends(auth_write)])
    def lock(month:str):
        if settings.shadow_mode: raise HTTPException(409,"lock disabled in shadow mode")
        raise HTTPException(501,"production lock requires completed exit gates")

    @app.post("/api/v1/months/{month}/create-revision", dependencies=[Depends(auth_write)])
    def create_revision(month:str):
        row=_month_row(month)
        if row["state"] != "LOCKED": raise HTTPException(409,"a superseding revision requires a locked month")
        raise HTTPException(501,"disabled until shadow exit gates pass")

    @app.post("/api/v1/months/{month}/export", dependencies=[Depends(auth_write)])
    def prepare_export(month:str):
        return {"report_id":None,"draft_url":f"/api/v1/months/{month}/report.csv","shadow":settings.shadow_mode}

    @app.get("/api/v1/months/{month}/report.csv", dependencies=[Depends(auth_read)])
    def export_csv(month:str):
        data=summary(month); output=io.StringIO(); writer=csv.writer(output); writer.writerow(["field","value"])
        for key,value in data.items():
            if not isinstance(value,(dict,list)): writer.writerow([key,value])
        slug=re.sub(r"[^a-z0-9-]+","-",settings.vehicle_name.lower()).strip("-") or "vehicle"
        return PlainTextResponse(output.getvalue(),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="{slug}-{month}-draft.csv"'})

    return app
