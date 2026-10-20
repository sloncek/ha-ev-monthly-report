CREATE UNIQUE INDEX IF NOT EXISTS uq_source_fetch_payload
ON source_fetch(source,request_hash,evidence_id);

CREATE INDEX IF NOT EXISTS ix_meter_interval_lookup
ON meter_interval(meter_key_hash,reading_type,start_utc,end_utc,source_fetch_id);

CREATE VIEW IF NOT EXISTS meter_interval_latest AS
SELECT mi.*
FROM meter_interval mi
JOIN source_fetch sf ON sf.id=mi.source_fetch_id
WHERE NOT EXISTS (
  SELECT 1
  FROM meter_interval newer
  JOIN source_fetch nsf ON nsf.id=newer.source_fetch_id
  WHERE newer.meter_key_hash=mi.meter_key_hash
    AND newer.reading_type=mi.reading_type
    AND newer.start_utc=mi.start_utc
    AND newer.end_utc=mi.end_utc
    AND (nsf.fetched_at>sf.fetched_at OR (nsf.fetched_at=sf.fetched_at AND newer.id>mi.id))
);

CREATE TABLE IF NOT EXISTS ha_outbox (
  id INTEGER PRIMARY KEY,
  event_key TEXT NOT NULL UNIQUE,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  next_attempt_at TEXT NOT NULL,
  delivered_at TEXT,
  last_error TEXT
);

CREATE TABLE IF NOT EXISTS sync_run (
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,
  period_start_utc TEXT NOT NULL,
  period_end_utc TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('RUNNING','COMPLETE','INCOMPLETE','ERROR')),
  expected_intervals INTEGER,
  actual_intervals INTEGER,
  detail TEXT,
  started_at TEXT NOT NULL,
  finished_at TEXT
);
