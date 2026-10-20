from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: Path, migrations: Path, timezone_name: str = "UTC"):
        self.path = path
        self.migrations = migrations
        self.timezone = timezone_name

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=15000")
        return conn

    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def migrate(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS schema_migration(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL, checksum TEXT NOT NULL)")
            applied = {r[0]: r[1] for r in conn.execute("SELECT version,checksum FROM schema_migration")}
            for file in sorted(self.migrations.glob("[0-9][0-9][0-9]_*.sql")):
                version = int(file.name.split("_", 1)[0])
                sql = file.read_text()
                checksum = hashlib.sha256(sql.encode()).hexdigest()
                if version in applied:
                    if applied[version] != checksum:
                        raise RuntimeError(f"migration checksum mismatch for version {version}")
                    continue
                conn.executescript(sql)
                conn.execute(
                    "INSERT OR REPLACE INTO schema_migration VALUES(?,?,?)",
                    (version, utcnow(), checksum),
                )

    def migration_status(self) -> dict:
        expected = {}
        for file in sorted(self.migrations.glob("[0-9][0-9][0-9]_*.sql")):
            version = int(file.name.split("_", 1)[0])
            expected[version] = hashlib.sha256(file.read_bytes()).hexdigest()
        with self.connect() as conn:
            applied = {int(row[0]): row[1] for row in conn.execute("SELECT version,checksum FROM schema_migration")}
        missing = sorted(set(expected) - set(applied))
        unexpected = sorted(set(applied) - set(expected))
        mismatched = sorted(version for version in set(expected) & set(applied) if expected[version] != applied[version])
        return {"ok": not (missing or unexpected or mismatched), "missing": missing, "unexpected": unexpected, "mismatched": mismatched}

    @staticmethod
    def verify_sqlite(path: Path) -> dict:
        if not path.is_file() or path.stat().st_size <= 0:
            return {"ok": False, "detail": "backup_missing_or_empty"}
        try:
            with sqlite3.connect(path, timeout=15) as conn:
                conn.execute("PRAGMA query_only=ON")
                integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
                tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                required = {"schema_migration", "invoice", "charge_session", "audit_event"}
                ok = integrity == "ok" and required <= tables
                return {"ok": ok, "integrity": integrity, "missing_tables": sorted(required - tables)}
        except sqlite3.Error as exc:
            return {"ok": False, "detail": type(exc).__name__}

    def online_backup(self, destination: Path) -> dict:
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        destination.parent.chmod(0o700)
        temp = destination.with_name(f".{destination.name}.tmp")
        temp.unlink(missing_ok=True)
        try:
            with self.connect() as source, sqlite3.connect(temp) as target:
                source.backup(target)
            temp.chmod(0o600)
            os.replace(temp, destination)
        finally:
            temp.unlink(missing_ok=True)
        result = self.verify_restore(destination)
        if not result["ok"]:
            raise RuntimeError(f"backup restore verification failed: {result}")
        return {**result, "path": str(destination), "size_bytes": destination.stat().st_size}

    def verify_restore(self, backup: Path) -> dict:
        # Verify a copied restore candidate, not the live backup inode.
        with tempfile.TemporaryDirectory(prefix="energy-ledger-restore-") as directory:
            restored = Path(directory) / "ledger.sqlite3"
            shutil.copy2(backup, restored)
            result = self.verify_sqlite(restored)
            if not result["ok"]:
                return result
            try:
                with sqlite3.connect(restored) as conn:
                    applied = {int(row[0]): row[1] for row in conn.execute("SELECT version,checksum FROM schema_migration")}
                expected = {
                    int(file.name.split("_", 1)[0]): hashlib.sha256(file.read_bytes()).hexdigest()
                    for file in self.migrations.glob("[0-9][0-9][0-9]_*.sql")
                }
                missing = sorted(set(expected) - set(applied))
                mismatched = sorted(v for v in set(expected) & set(applied) if expected[v] != applied[v])
                result.update({"ok": result["ok"] and not missing and not mismatched, "missing_migrations": missing, "mismatched_migrations": mismatched})
                return result
            finally:
                restored.unlink(missing_ok=True)

    def ensure_month(self, year_month: str, timezone_name: str | None = None) -> int:
        year, month = map(int, year_month.split("-"))
        local = ZoneInfo(timezone_name or self.timezone)
        start = datetime(year, month, 1, tzinfo=local)
        end = datetime(year + (month == 12), 1 if month == 12 else month + 1, 1, tzinfo=local)
        with self.transaction() as conn:
            row = conn.execute("SELECT revision_id FROM month_head WHERE year_month=?", (year_month,)).fetchone()
            if row:
                return int(row[0])
            cur = conn.execute(
                "INSERT INTO month_revision(year_month,revision,state,policy_version_id,period_start_utc,period_end_utc) VALUES(?,1,'OPEN',1,?,?)",
                (year_month, start.astimezone(timezone.utc).isoformat(), end.astimezone(timezone.utc).isoformat()),
            )
            rid = int(cur.lastrowid)
            conn.execute("INSERT INTO month_head VALUES(?,?)", (year_month, rid))
            return rid

    def audit(self, conn: sqlite3.Connection, actor: str, action: str, object_type: str, object_id: str, payload: dict) -> None:
        previous = conn.execute("SELECT event_hash FROM audit_event ORDER BY id DESC LIMIT 1").fetchone()
        prev = previous[0] if previous else None
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        occurred = utcnow()
        digest = hashlib.sha256(f"{prev or ''}|{occurred}|{actor}|{action}|{object_type}|{object_id}|{body}".encode()).hexdigest()
        conn.execute(
            "INSERT INTO audit_event(occurred_at,actor,action,object_type,object_id,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)",
            (occurred, actor, action, object_type, object_id, body, prev, digest),
        )

    def verify_audit_chain(self) -> dict:
        previous = None
        count = 0
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM audit_event ORDER BY id")
            for row in rows:
                count += 1
                expected = hashlib.sha256(
                    f"{previous or ''}|{row['occurred_at']}|{row['actor']}|{row['action']}|{row['object_type']}|{row['object_id']}|{row['payload_json']}".encode()
                ).hexdigest()
                if row["previous_hash"] != previous or row["event_hash"] != expected:
                    return {"ok": False, "events": count, "broken_at": int(row["id"])}
                previous = row["event_hash"]
        return {"ok": True, "events": count, "head": previous}
