from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Callable
from zoneinfo import ZoneInfo

from .db import Database, utcnow

RETRY_DELAY = timedelta(minutes=15)
STALE_AFTER = timedelta(minutes=15)


def classify_error(exc: Exception) -> tuple[str, bool]:
    """Return a safe error code and whether automatic retry is appropriate."""
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status in {401, 403}:
        return "moj_elektro_auth", False
    if isinstance(status, int) and 400 <= status < 500 and status != 429:
        return f"moj_elektro_http_{status}", False
    if isinstance(status, int):
        return f"moj_elektro_http_{status}", status == 429 or status >= 500
    return type(exc).__name__, True


def invoice_month(period_start_utc: str, timezone_name: str = "UTC") -> str:
    """Map an invoice UTC boundary to its configured local calendar month."""
    instant = datetime.fromisoformat(period_start_utc.replace("Z", "+00:00"))
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=timezone.utc)
    return instant.astimezone(ZoneInfo(timezone_name)).strftime("%Y-%m")


class InvoicePipeline:
    def __init__(self, db: Database):
        self.db = db

    def enqueue(self, invoice_id: int, period_start_utc: str) -> str:
        month = invoice_month(period_start_utc, self.db.timezone)
        self.db.ensure_month(month)
        now = utcnow()
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO invoice_pipeline(invoice_id,year_month,state,next_attempt_at,created_at,updated_at) "
                "VALUES(?,?,'PENDING',?,?,?)",
                (invoice_id, month, now, now, now),
            )
            if cur.rowcount:
                self.db.audit(conn, "system", "invoice_pipeline_enqueued", "invoice", str(invoice_id), {"month": month})
        return month

    def enqueue_missing(self) -> int:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT i.id,i.period_start_utc FROM invoice i LEFT JOIN invoice_pipeline p ON p.invoice_id=i.id "
                "WHERE p.id IS NULL ORDER BY i.id"
            ).fetchall()
        for row in rows:
            self.enqueue(int(row["id"]), row["period_start_utc"])
        return len(rows)

    def claim(self) -> dict | None:
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        stale = (now_dt - STALE_AFTER).isoformat()
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE invoice_pipeline SET state='ERROR',last_error='interrupted',detail='stale_running_recovered',"
                "next_attempt_at=?,updated_at=?,row_version=row_version+1 WHERE state='RUNNING' AND started_at<?",
                (now, now, stale),
            )
            row = conn.execute(
                "SELECT * FROM invoice_pipeline WHERE state IN ('PENDING','INCOMPLETE','ERROR') "
                "AND retryable=1 AND next_attempt_at<=? ORDER BY id LIMIT 1",
                (now,),
            ).fetchone()
            if not row:
                return None
            changed = conn.execute(
                "UPDATE invoice_pipeline SET state='RUNNING',attempts=attempts+1,last_error=NULL,started_at=?,"
                "finished_at=NULL,updated_at=?,row_version=row_version+1 WHERE id=? AND state=?",
                (now, now, row["id"], row["state"]),
            ).rowcount
            if not changed:
                return None
            return dict(conn.execute("SELECT * FROM invoice_pipeline WHERE id=?", (row["id"],)).fetchone())

    def finish(self, job_id: int, state: str, detail: dict, error: str | None = None, retryable: bool = True) -> None:
        if state not in {"COMPLETE", "INCOMPLETE", "ERROR"}:
            raise ValueError("invalid terminal pipeline state")
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        with self.db.transaction() as conn:
            job = conn.execute("SELECT invoice_id,year_month,attempts FROM invoice_pipeline WHERE id=?", (job_id,)).fetchone()
            if not job:
                return
            delay_minutes = min(360, int(RETRY_DELAY.total_seconds() // 60) * (2 ** max(0, int(job["attempts"]) - 1)))
            retry_at = now if state == "COMPLETE" else (now_dt + timedelta(minutes=delay_minutes)).isoformat()
            serialized = json.dumps(detail, sort_keys=True, separators=(",", ":"))
            changed = conn.execute(
                "UPDATE invoice_pipeline SET state=?,last_error=?,retryable=?,detail=?,next_attempt_at=?,finished_at=?,"
                "updated_at=?,row_version=row_version+1 WHERE id=? AND state='RUNNING'",
                (state, error, int(retryable), serialized, retry_at, now, now, job_id),
            ).rowcount
            if changed:
                self.db.audit(conn, "system", "invoice_pipeline_finished", "invoice", str(job["invoice_id"]),
                              {"month": job["year_month"], "state": state, "error": error})

    def run_one(self, backfill: Callable[[str], dict], reconcile: Callable[[str], dict]) -> dict | None:
        job = self.claim()
        if not job:
            return None
        try:
            backfill_result = backfill(job["year_month"])
            if backfill_result.get("status") != "COMPLETE":
                detail = {"stage": "backfill", "backfill": backfill_result}
                self.finish(job["id"], "INCOMPLETE", detail)
                return {"id": job["id"], "month": job["year_month"], "state": "INCOMPLETE", "detail": detail}
            reconciliation = reconcile(job["year_month"])
            dimensions = reconciliation.get("dimensions", {})
            # PASS and FAIL are both final comparison outcomes. A mismatch must
            # be shown for human review, not retried forever as missing data.
            complete = all(dimensions.get(name) in {"PASS", "FAIL"} for name in ("total", "peak", "offpeak"))
            state = "COMPLETE" if complete else "INCOMPLETE"
            detail = {"stage": "reconcile", "backfill": backfill_result, "reconciliation": reconciliation}
            self.finish(job["id"], state, detail)
            return {"id": job["id"], "month": job["year_month"], "state": state, "detail": detail}
        except Exception as exc:
            error, retryable = classify_error(exc)
            detail = {"stage": "automatic_processing", "error": error}
            self.finish(job["id"], "ERROR", detail, error, retryable=retryable)
            return {"id": job["id"], "month": job["year_month"], "state": "ERROR", "error": error, "retryable": retryable}
