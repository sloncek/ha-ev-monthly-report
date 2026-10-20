from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .db import Database, utcnow
from .settings import configured_timezone
from .mojelektro import MojElektroAdapter, READING_TYPES


class MojElektroService:
    def __init__(self, db: Database, data_dir: Path, config: dict, token_file: Path):
        self.db, self.data_dir, self.config, self.token_file = db, data_dir, config, token_file

    def enabled(self) -> bool:
        return bool(self.config.get("enabled") and self.config.get("usage_point") and self.token_file.exists() and self.token_file.stat().st_size)

    def _evidence(self, content: bytes, request_hash: str) -> tuple[int, str]:
        digest = hashlib.sha256(content).hexdigest()
        path = self.data_dir / "evidence" / digest[:2] / digest
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not path.exists():
            temp = path.with_suffix(".tmp")
            temp.write_bytes(content); temp.chmod(0o600); os.replace(temp, path)
        with self.db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO evidence(sha256,media_type,size_bytes,original_name,storage_path,created_at) VALUES(?,?,?,?,?,?)",(digest,"application/json",len(content),f"mojelektro-{request_hash}.json",str(path),utcnow()))
            return int(conn.execute("SELECT id FROM evidence WHERE sha256=?",(digest,)).fetchone()[0]), digest

    def backfill(self, month_row) -> dict:
        if not self.enabled():
            return {"status":"INCOMPLETE","detail":"moj_elektro_not_configured"}
        cfg=self.config
        adapter=MojElektroAdapter(cfg.get("base_url","https://api.informatika.si/mojelektro/v1"),cfg["usage_point"],self.token_file)
        local=ZoneInfo(configured_timezone())
        start=datetime.fromisoformat(month_row["period_start_utc"]).astimezone(local)
        end=datetime.fromisoformat(month_row["period_end_utc"]).astimezone(local)
        meter_hash=hashlib.sha256(cfg["usage_point"].encode()).hexdigest()
        expected=int((end.astimezone(timezone.utc)-start.astimezone(timezone.utc)).total_seconds()//900)
        run_id=None
        with self.db.transaction() as conn:
            run_id=conn.execute("INSERT INTO sync_run(source,period_start_utc,period_end_utc,status,expected_intervals,started_at) VALUES('moj_elektro',?,?,'RUNNING',?,?)",(month_row["period_start_utc"],month_row["period_end_utc"],expected,utcnow())).lastrowid
        try:
            for name,reading_type in READING_TYPES.items():
                for chunk_start,chunk_end in adapter.chunks(start.date(),end.date()):
                    raw,meta=adapter.fetch(chunk_start,chunk_end,reading_type)
                    evidence_id,revision=self._evidence(raw,meta["request_hash"])
                    fetched=utcnow()
                    with self.db.transaction() as conn:
                        conn.execute("INSERT OR IGNORE INTO source_fetch(source,request_hash,fetched_at,evidence_id,status) VALUES('moj_elektro',?,?,?,'OK')",(meta["request_hash"],fetched,evidence_id))
                        fetch_id=int(conn.execute("SELECT id FROM source_fetch WHERE source='moj_elektro' AND request_hash=? AND evidence_id=? ORDER BY id DESC LIMIT 1",(meta["request_hash"],evidence_id)).fetchone()[0])
                        for block in meta["json"].get("intervalBlocks",[]):
                            if block.get("readingType") != reading_type: continue
                            for reading in block.get("intervalReadings",[]):
                                observed=datetime.fromisoformat(reading["timestamp"]).astimezone(timezone.utc)
                                value_wh=adapter.wh(str(reading["value"]))
                                if name=="interval":
                                    interval_start=observed-timedelta(minutes=15)
                                    conn.execute("INSERT OR IGNORE INTO meter_interval(meter_key_hash,reading_type,start_utc,end_utc,energy_wh,source_fetch_id,source_revision) VALUES(?,?,?,?,?,?,?)",(meter_hash,name,interval_start.isoformat(),observed.isoformat(),value_wh,fetch_id,revision))
                                else:
                                    conn.execute("INSERT OR IGNORE INTO meter_register(meter_key_hash,reading_type,observed_utc,value_wh,source_fetch_id,source_revision) VALUES(?,?,?,?,?,?)",(meter_hash,name,observed.isoformat(),value_wh,fetch_id,revision))
            with self.db.connect() as conn:
                actual=int(conn.execute("SELECT COUNT(*) FROM meter_interval_latest WHERE meter_key_hash=? AND reading_type='interval' AND start_utc>=? AND end_utc<=?",(meter_hash,month_row["period_start_utc"],month_row["period_end_utc"])).fetchone()[0])
            status="COMPLETE" if actual==expected else "INCOMPLETE"
            with self.db.transaction() as conn:
                conn.execute("UPDATE sync_run SET status=?,actual_intervals=?,detail=?,finished_at=? WHERE id=?",(status,actual,None if status=="COMPLETE" else "interval_coverage_mismatch",utcnow(),run_id))
            return {"status":status,"expected_intervals":expected,"actual_intervals":actual}
        except Exception as exc:
            with self.db.transaction() as conn:
                conn.execute("UPDATE sync_run SET status='ERROR',detail=?,finished_at=? WHERE id=?",(type(exc).__name__,utcnow(),run_id))
            raise
