"""Employer reimbursement register, deliberately separate from invoice cost estimates.

Reported figures are immutable accounting snapshots. Changing telemetry exposes a
pending difference, never an automatic correction to previously emailed claims.
"""
from __future__ import annotations

import calendar
import json
import re
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .db import utcnow


class RegisterError(ValueError):
    def __init__(self, detail, status=422):
        super().__init__(detail)
        self.status = status


def month_valid(month):
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise RegisterError("month must be YYYY-MM")
    try:
        date.fromisoformat(month + "-01")
    except ValueError:
        raise RegisterError("invalid month")
    return month


def number(value, maximum=Decimal("1000000000")):
    try:
        result = Decimal(str(value))
        if not result.is_finite() or result < 0 or result > maximum:
            raise ValueError
        return result
    except (InvalidOperation, ValueError):
        raise RegisterError("invalid nonnegative decimal")


def cents(value):
    return int((number(value) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def money(value):
    return None if value is None else format(Decimal(value) / 100, ".2f")


def signed_cents(value):
    try:
        n = Decimal(str(value))
        if not n.is_finite() or abs(n) > 1000000000:
            raise ValueError
        return int((n * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (ValueError, InvalidOperation):
        raise RegisterError("invalid signed amount")


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _retry(conn, key, payload):
    if not isinstance(key, str) or not 8 <= len(key) <= 200:
        raise RegisterError("idempotency_key must contain 8 to 200 characters")
    row = conn.execute("SELECT * FROM ev_register_request WHERE idempotency_key=?", (key,)).fetchone()
    if row:
        if row["payload_json"] != _canonical(payload):
            raise RegisterError("idempotency key reused with different data", 409)
        return json.loads(row["response_json"])


def _remember(conn, key, payload, response):
    conn.execute("INSERT INTO ev_register_request VALUES(?,?,?,?)", (key, _canonical(payload), _canonical(response), utcnow()))


def _ensure(conn, month):
    conn.execute("INSERT OR IGNORE INTO ev_register_month(year_month,updated_at) VALUES(?,?)", (month, utcnow()))


def _opening(conn, month):
    # Only an actually reported earlier month can create a financial carry.
    rows = conn.execute("SELECT snapshot_json FROM ev_register_month WHERE year_month<? AND snapshot_json IS NOT NULL ORDER BY year_month DESC LIMIT 1", (month,)).fetchone()
    return json.loads(rows[0])["closing_balance_cents"] if rows else 0


def _calculate(db, conn, month):
    record = conn.execute("SELECT * FROM ev_register_month WHERE year_month=?", (month,)).fetchone()
    legacy = json.loads(record["legacy_json"]) if record and record["legacy_json"] else {}
    usage = conn.execute("SELECT * FROM home_month_usage WHERE year_month=?", (month,)).fetchone()
    wh = usage["energy_wh"] if usage else legacy.get("home_wh")
    quality = usage["quality"] if usage else ("legacy_manual" if wh is not None else "missing")
    month_complete = bool(usage and json.loads(usage["detail_json"]).get("month_complete",False))
    rate_row = conn.execute("SELECT rate FROM ev_reimbursement_rate WHERE effective_month<=? ORDER BY effective_month DESC LIMIT 1", (month,)).fetchone()
    rate = Decimal(rate_row[0]) if rate_row else (Decimal(str(legacy["rate"])) if legacy.get("rate") is not None else None)
    expenses = [dict(row) for row in conn.execute("SELECT * FROM ev_register_expense WHERE year_month=? ORDER BY occurred_date,id", (month,))]
    # Existing per-session public entries remain in the register; they are not
    # copied into the new expense table (which would double-count them).
    from zoneinfo import ZoneInfo
    local=ZoneInfo(db.timezone)
    for row in conn.execute("SELECT * FROM public_charge WHERE verification_state!='VOID'"):
        if datetime.fromisoformat(row["started_at"].replace("Z","+00:00")).astimezone(local).strftime("%Y-%m") == month:
            expenses.append({"id":f"public-{row['id']}","year_month":month,"occurred_date":row["started_at"][:10],"kind":"PUBLIC","provider":row["provider"],"gross_cents":int((Decimal(row["gross_micro_eur"])/10000).quantize(Decimal("1"),rounding=ROUND_HALF_UP)),"energy_wh":row["energy_wh"],"eligible":row["claimable"],"notes":"Existing public session"})
    public = sum(r["gross_cents"] for r in expenses if r["kind"] == "PUBLIC")
    other = sum(r["gross_cents"] for r in expenses if r["kind"] == "OTHER")
    eligible = sum(r["gross_cents"] for r in expenses if r["eligible"])
    unknown_energy = any(r["kind"] == "PUBLIC" and r["energy_wh"] is None for r in expenses)
    public_wh = sum(r["energy_wh"] or 0 for r in expenses if r["kind"] == "PUBLIC")
    home_cents = None if wh is None or rate is None else int((Decimal(wh) * rate / 10).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    monthly = None if home_cents is None else home_cents + eligible
    opening = _opening(conn, month)
    odo = record["odometer_km"] if record else None
    previous = conn.execute("SELECT odometer_km FROM ev_register_month WHERE year_month<? AND odometer_km IS NOT NULL ORDER BY year_month DESC LIMIT 1", (month,)).fetchone()
    distance = odo - previous[0] if odo is not None and previous else None
    # Missing adjacent month is not exact calendar distance.
    prev_month = f"{int(month[:4]) - (month[5:] == '01'):04d}-{12 if month[5:] == '01' else int(month[5:])-1:02d}"
    adjacent = conn.execute("SELECT odometer_km FROM ev_register_month WHERE year_month=?", (prev_month,)).fetchone()
    if not adjacent or adjacent[0] is None:
        distance = None
    return {
        "month": month, "status": "DRAFT", "home_kwh": None if wh is None else format(Decimal(wh)/1000, ".3f"),
        "reimbursement_rate": None if rate is None else format(rate, "f"), "home_reimbursement_eur": money(home_cents),
        "public_gross_eur": money(public), "other_gross_eur": money(other), "eligible_expenses_eur": money(eligible),
        "monthly_eligible_eur": money(monthly), "opening_balance_eur": money(opening),
        "requested_eur": money(None if monthly is None else monthly + opening),
        "reported_eur": None, "closing_balance_eur": None, "pending_home_delta_eur": None,
        "total_kwh": None if wh is None or unknown_energy else format(Decimal(wh+public_wh)/1000, ".3f"),
        "energy_complete": wh is not None and quality == "complete" and month_complete and not unknown_energy,
        "month_complete": month_complete,
        "ready_to_report": wh is not None and quality == "complete" and month_complete,
        "public_energy_complete": not unknown_energy, "source_quality": quality,
        "odometer_km": odo, "monthly_distance_km": distance,
        "odometer_observed_at": record["observed_at"] if record else None,
        "odometer_source": record["odometer_source"] if record else None,
        "expenses": [{**r, "gross_eur": money(r["gross_cents"]), "energy_kwh": None if r["energy_wh"] is None else format(Decimal(r["energy_wh"])/1000, ".3f"), "eligible": bool(r["eligible"])} for r in expenses],
        "source_sha256": record["source_sha256"] if record else None,
        "legacy": legacy or None,
    }


def get_register(db, month, conn=None):
    month_valid(month)
    if conn is None:
        with db.connect() as connection:
            return get_register(db, month, connection)
    live = _calculate(db, conn, month)
    row = conn.execute("SELECT snapshot_json FROM ev_register_month WHERE year_month=?", (month,)).fetchone()
    if row and row[0]:
        frozen = json.loads(row[0])
        result = frozen["register"]
        baseline = frozen.get("verified_home_cents", frozen.get("home_cents"))
        current = live["home_reimbursement_eur"]
        result["pending_home_delta_eur"] = money(None if baseline is None or current is None else cents(current)-baseline)
        result["current_home_kwh"] = live["home_kwh"]
        result["current_source_quality"] = live["source_quality"]
        result["pending_delta_verified"] = live["source_quality"] == "complete" and live["month_complete"]
        result["ready_to_report"] = False
        return result
    return live


def add_expense(db, payload, actor):
    month = month_valid(payload["month"])
    try:
        occurred = date.fromisoformat(payload["date"])
    except ValueError:
        raise RegisterError("date must be YYYY-MM-DD")
    if occurred.strftime("%Y-%m") != month:
        raise RegisterError("expense date must belong to selected month")
    kind = payload["kind"]
    if kind not in ("PUBLIC", "OTHER"):
        raise RegisterError("kind must be PUBLIC or OTHER")
    gross = cents(payload["gross_eur"])
    wh = None if payload.get("energy_kwh") is None else int((number(payload["energy_kwh"]) * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if kind == "OTHER" and wh is not None:
        raise RegisterError("OTHER expenses cannot contain charging energy")
    request = {"action": "expense", **payload}
    with db.transaction() as conn:
        retry = _retry(conn, payload["idempotency_key"], request)
        if retry is not None:
            return retry
        _ensure(conn, month)
        if conn.execute("SELECT snapshot_json FROM ev_register_month WHERE year_month=?", (month,)).fetchone()[0]:
            raise RegisterError("reported month is immutable; add correction to a draft month", 409)
        cursor = conn.execute("INSERT INTO ev_register_expense(year_month,occurred_date,kind,provider,gross_cents,energy_wh,eligible,notes,actor,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (month, payload["date"], kind, payload.get("provider", ""), gross, wh, int(payload.get("eligible", False)), payload.get("notes", ""), actor, utcnow()))
        result = {"id": cursor.lastrowid, "register": get_register(db, month, conn)}
        _remember(conn, payload["idempotency_key"], request, result)
        db.audit(conn, actor, "REGISTER_EXPENSE", "month", month, {"id": cursor.lastrowid, "gross_cents": gross})
        return result


def report_month(db, month, payload, actor):
    month_valid(month)
    amount = cents(payload["amount_eur"])
    request = {"action": "reported", "month": month, **payload}
    with db.transaction() as conn:
        retry = _retry(conn, payload["idempotency_key"], request)
        if retry is not None:
            return retry
        _ensure(conn, month)
        if conn.execute("SELECT snapshot_json FROM ev_register_month WHERE year_month=?", (month,)).fetchone()[0]:
            raise RegisterError("already reported; snapshot is immutable", 409)
        result = _calculate(db, conn, month)
        if result["monthly_eligible_eur"] is None:
            raise RegisterError("home energy is missing; cannot mark reported", 409)
        usage = conn.execute("SELECT detail_json,quality FROM home_month_usage WHERE year_month=?", (month,)).fetchone()
        if not usage or usage["quality"] != "complete" or not json.loads(usage["detail_json"]).get("month_complete", False):
            raise RegisterError("closed month with complete home energy is required", 409)
        # Do not let a backdated report silently change a later frozen carry.
        if conn.execute("SELECT 1 FROM ev_register_month WHERE year_month>? AND snapshot_json IS NOT NULL", (month,)).fetchone():
            raise RegisterError("later reported month exists; backdated report requires a revision", 409)
        closing = signed_cents(result["requested_eur"]) - amount
        result.update(status="REPORTED", reported_eur=money(amount), closing_balance_eur=money(closing), reported_at=utcnow())
        snapshot = {"register": result, "home_cents": cents(result["home_reimbursement_eur"]), "closing_balance_cents": closing}
        conn.execute("UPDATE ev_register_month SET snapshot_json=?,updated_at=? WHERE year_month=?", (_canonical(snapshot), utcnow(), month))
        _remember(conn, payload["idempotency_key"], request, result)
        db.audit(conn, actor, "REGISTER_REPORTED", "month", month, snapshot)
        return result


def set_rate(db, month, rate, actor):
    month_valid(month)
    value = number(rate, Decimal("10"))
    if value == 0 or value.as_tuple().exponent < -6:
        raise RegisterError("rate must be positive with at most 6 decimal places")
    with db.transaction() as conn:
        if conn.execute("SELECT 1 FROM ev_register_month WHERE year_month>=? AND snapshot_json IS NOT NULL", (month,)).fetchone():
            raise RegisterError("rate affects a reported month; select a later effective month", 409)
        conn.execute("INSERT INTO ev_reimbursement_rate VALUES(?,?,?,?) ON CONFLICT(effective_month) DO UPDATE SET rate=excluded.rate,actor=excluded.actor,updated_at=excluded.updated_at", (month, format(value,"f"),actor,utcnow()))
        db.audit(conn,actor,"REGISTER_RATE","month",month,{"rate":str(value)})
    return get_register(db,month)


def set_odometer(db, month, payload, actor):
    month_valid(month)
    odo = number(payload["odometer_km"], Decimal("10000000"))
    if odo != odo.to_integral_value():
        raise RegisterError("odometer must be integer kilometres")
    try:
        observed = datetime.fromisoformat(payload["observed_at"].replace("Z", "+00:00"))
        from zoneinfo import ZoneInfo
        if observed.tzinfo is None or observed.astimezone(ZoneInfo(db.timezone)).strftime("%Y-%m") != month:
            raise ValueError
        if observed.astimezone(timezone.utc) > datetime.now(timezone.utc)+timedelta(minutes=5):
            raise ValueError
    except ValueError:
        raise RegisterError("observed_at must be timezone-aware, in selected month and not in the future")
    with db.transaction() as conn:
        _ensure(conn, month)
        record = conn.execute("SELECT snapshot_json,odometer_source FROM ev_register_month WHERE year_month=?", (month,)).fetchone()
        if record[0]:
            raise RegisterError("reported month odometer is immutable", 409)
        # Automated Home Assistant readings must not overwrite a manual reading.
        if record[1] == "manual" and payload.get("source") != "manual":
            return get_register(db, month, conn)
        previous=conn.execute("SELECT odometer_km FROM ev_register_month WHERE year_month<? AND odometer_km IS NOT NULL ORDER BY year_month DESC LIMIT 1",(month,)).fetchone()
        if previous and odo < previous[0]:
            raise RegisterError("odometer cannot decrease")
        following=conn.execute("SELECT odometer_km FROM ev_register_month WHERE year_month>? AND odometer_km IS NOT NULL ORDER BY year_month LIMIT 1",(month,)).fetchone()
        if following and odo > following[0]:
            raise RegisterError("odometer cannot exceed a later known reading")
        conn.execute("UPDATE ev_register_month SET odometer_km=?,observed_at=?,odometer_source=?,updated_at=? WHERE year_month=?",(int(odo),payload["observed_at"],payload.get("source","manual"),utcnow(),month))
        db.audit(conn,actor,"REGISTER_ODOMETER","month",month,{"odometer_km":int(odo),"source":payload.get("source","manual")})
    return get_register(db,month)


def history(db):
    with db.connect() as conn:
        months = [row[0] for row in conn.execute("SELECT year_month FROM ev_register_month UNION SELECT year_month FROM home_month_usage ORDER BY year_month DESC")]
        return {"months": [get_register(db,m,conn) for m in months]}


def import_legacy(db, rows, source_sha256, actor="legacy-migration"):
    """Import supplied, reviewed source rows. Original workbooks are never edited.

    Explicit source request and balance win over reconstructed arithmetic, since
    early worksheet rows used inconsistent carry formulas. Raw cells remain proof.
    """
    if not re.fullmatch(r"[a-f0-9]{64}", source_sha256):
        raise RegisterError("source SHA256 required")
    imported = []
    with db.transaction() as conn:
        for item in sorted(rows, key=lambda r:r["month"]):
            month = month_valid(item["month"])
            existing = conn.execute("SELECT source_sha256,legacy_json FROM ev_register_month WHERE year_month=?", (month,)).fetchone()
            raw = _canonical(item)
            if existing and existing["legacy_json"]:
                if existing["source_sha256"] != source_sha256 or existing["legacy_json"] != raw:
                    raise RegisterError("legacy source conflict", 409)
                continue
            if existing:
                has_expense = conn.execute("SELECT 1 FROM ev_register_expense WHERE year_month=?",(month,)).fetchone()
                has_snapshot = conn.execute("SELECT snapshot_json FROM ev_register_month WHERE year_month=?",(month,)).fetchone()[0]
                if has_expense or has_snapshot:
                    raise RegisterError("existing register cannot be replaced by legacy import",409)
            _ensure(conn,month)
            conn.execute("UPDATE ev_register_month SET legacy_json=?,source_sha256=?,source_sheet=?,source_row=?,odometer_km=?,odometer_source=?,updated_at=? WHERE year_month=?",(raw,source_sha256,item.get("sheet","legacy"),item.get("row"),item.get("odometer_km"),"legacy_manual" if item.get("odometer_km") is not None else None,utcnow(),month))
            public = cents(item.get("public_gross_eur","0"))
            # A source monthly aggregate cannot be mixed with pre-existing
            # per-session entries without a reviewed deduplication decision.
            if public:
                from zoneinfo import ZoneInfo
                for session in conn.execute("SELECT started_at FROM public_charge WHERE verification_state!='VOID'"):
                    at=datetime.fromisoformat(session[0].replace("Z","+00:00"))
                    if at.astimezone(ZoneInfo(db.timezone)).strftime("%Y-%m")==month:
                        raise RegisterError("legacy aggregate overlaps existing public sessions",409)
            if public or item.get("public_energy_wh"):
                conn.execute("INSERT INTO ev_register_expense(year_month,occurred_date,kind,provider,gross_cents,energy_wh,eligible,notes,actor,created_at) VALUES(?,?,'PUBLIC','Legacy monthly aggregate',?,?,1,?,?,?)",(month,month+f"-{calendar.monthrange(int(month[:4]),int(month[5:]))[1]:02d}",public,item.get("public_energy_wh"),item.get("notes",""),actor,utcnow()))
            if item.get("reported_eur") is not None:
                result = _calculate(db,conn,month)
                home_cents = cents(item.get("home_reimbursement_eur",str(Decimal(item["home_wh"])*Decimal(item["rate"])/1000)))
                monthly = cents(item["monthly_eligible_eur"])
                request = signed_cents(item["requested_eur"])
                balance = signed_cents(item["closing_balance_eur"])
                result.update(status="REPORTED",home_kwh=format(Decimal(item["home_wh"])/1000,".3f"),reimbursement_rate=item["rate"],home_reimbursement_eur=money(home_cents),monthly_eligible_eur=money(monthly),requested_eur=money(request),opening_balance_eur=money(request-monthly),reported_eur=money(cents(item["reported_eur"])),closing_balance_eur=money(balance),source_quality="legacy_manual",energy_complete=False,reported_at=None)
                result["total_kwh"] = None if item.get("public_energy_wh") is None and public else format(Decimal(item["home_wh"]+(item.get("public_energy_wh") or 0))/1000,".3f")
                result["public_energy_complete"] = not(public and item.get("public_energy_wh") is None)
                # Independent legacy balance is retained, not 'fixed' silently.
                result["legacy_balance_arithmetic_difference_eur"]=money(balance-(request-cents(item["reported_eur"])))
                snapshot={"register":result,"home_cents":home_cents,"closing_balance_cents":balance}
                conn.execute("UPDATE ev_register_month SET snapshot_json=? WHERE year_month=?",(_canonical(snapshot),month))
            db.audit(conn,actor,"REGISTER_LEGACY_IMPORT","month",month,{"source_sha256":source_sha256,"sheet":item.get("sheet","legacy"),"row":item.get("row")})
            imported.append(month)
    return {"imported":imported,"source_sha256":source_sha256}
