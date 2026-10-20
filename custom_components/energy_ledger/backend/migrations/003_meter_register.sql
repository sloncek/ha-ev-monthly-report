CREATE TABLE IF NOT EXISTS meter_register (
  id INTEGER PRIMARY KEY,
  meter_key_hash TEXT NOT NULL,
  reading_type TEXT NOT NULL,
  observed_utc TEXT NOT NULL,
  value_wh INTEGER NOT NULL,
  source_fetch_id INTEGER NOT NULL REFERENCES source_fetch(id),
  source_revision TEXT NOT NULL,
  UNIQUE(meter_key_hash,reading_type,observed_utc,source_revision)
);

CREATE VIEW IF NOT EXISTS meter_register_latest AS
SELECT mr.*
FROM meter_register mr
JOIN source_fetch sf ON sf.id=mr.source_fetch_id
WHERE NOT EXISTS (
  SELECT 1 FROM meter_register newer
  JOIN source_fetch nsf ON nsf.id=newer.source_fetch_id
  WHERE newer.meter_key_hash=mr.meter_key_hash
    AND newer.reading_type=mr.reading_type
    AND newer.observed_utc=mr.observed_utc
    AND (nsf.fetched_at>sf.fetched_at OR (nsf.fetched_at=sf.fetched_at AND newer.id>mr.id))
);
