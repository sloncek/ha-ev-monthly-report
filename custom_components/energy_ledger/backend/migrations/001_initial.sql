PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS schema_migration (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL,
  checksum TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS price_policy (
  id INTEGER PRIMARY KEY,
  version TEXT NOT NULL UNIQUE,
  effective_from TEXT NOT NULL,
  effective_to TEXT,
  status TEXT NOT NULL CHECK(status IN ('DRAFT','ACTIVE','RETIRED')),
  checksum TEXT NOT NULL
);

INSERT OR IGNORE INTO price_policy(id,version,effective_from,status,checksum)
VALUES(1,'shadow-unpriced-v1','2020-01-01','ACTIVE','shadow-unpriced-v1');

CREATE TABLE IF NOT EXISTS month_revision (
  id INTEGER PRIMARY KEY,
  year_month TEXT NOT NULL,
  revision INTEGER NOT NULL CHECK(revision > 0),
  state TEXT NOT NULL CHECK(state IN ('OPEN','RECONCILED','LOCKED')),
  supersedes_revision_id INTEGER REFERENCES month_revision(id),
  policy_version_id INTEGER NOT NULL REFERENCES price_policy(id),
  period_start_utc TEXT NOT NULL,
  period_end_utc TEXT NOT NULL,
  row_version INTEGER NOT NULL DEFAULT 1,
  locked_at TEXT,
  locked_by TEXT,
  UNIQUE(year_month,revision)
);

CREATE TABLE IF NOT EXISTS month_head (
  year_month TEXT PRIMARY KEY,
  revision_id INTEGER NOT NULL UNIQUE REFERENCES month_revision(id)
);

CREATE TABLE IF NOT EXISTS evidence (
  id INTEGER PRIMARY KEY,
  sha256 TEXT NOT NULL UNIQUE CHECK(length(sha256)=64),
  media_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL CHECK(size_bytes > 0),
  original_name TEXT NOT NULL,
  storage_path TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS invoice (
  id INTEGER PRIMARY KEY,
  supplier TEXT NOT NULL,
  invoice_number TEXT NOT NULL,
  period_start_utc TEXT NOT NULL,
  period_end_utc TEXT NOT NULL,
  peak_wh INTEGER,
  offpeak_wh INTEGER,
  electricity_wh INTEGER,
  electricity_net_micro_eur INTEGER,
  gas_millim3 INTEGER,
  gas_wh INTEGER,
  gas_net_micro_eur INTEGER,
  net_micro_eur INTEGER NOT NULL,
  vat_basis_points INTEGER NOT NULL,
  vat_micro_eur INTEGER NOT NULL,
  gross_micro_eur INTEGER NOT NULL,
  evidence_id INTEGER NOT NULL REFERENCES evidence(id),
  parser_version TEXT NOT NULL,
  parse_status TEXT NOT NULL CHECK(parse_status IN ('PENDING','VALID','REVIEW','REJECTED')),
  UNIQUE(supplier,invoice_number)
);

CREATE TABLE IF NOT EXISTS invoice_line (
  id INTEGER PRIMARY KEY,
  invoice_id INTEGER NOT NULL REFERENCES invoice(id),
  line_no INTEGER NOT NULL,
  category TEXT NOT NULL,
  dimension TEXT,
  quantity_scaled INTEGER,
  quantity_scale INTEGER,
  unit_price_decimal TEXT,
  net_micro_eur INTEGER,
  inclusion TEXT NOT NULL CHECK(inclusion IN ('VARIABLE','FIXED','DISCOUNT','INFORMATIVE','GAS')),
  raw_text TEXT NOT NULL,
  UNIQUE(invoice_id,line_no)
);

CREATE TABLE IF NOT EXISTS source_fetch (
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  evidence_id INTEGER NOT NULL REFERENCES evidence(id),
  status TEXT NOT NULL,
  UNIQUE(source,request_hash,fetched_at)
);

CREATE TABLE IF NOT EXISTS meter_interval (
  id INTEGER PRIMARY KEY,
  meter_key_hash TEXT NOT NULL,
  reading_type TEXT NOT NULL,
  start_utc TEXT NOT NULL,
  end_utc TEXT NOT NULL,
  energy_wh INTEGER NOT NULL,
  source_fetch_id INTEGER NOT NULL REFERENCES source_fetch(id),
  source_revision TEXT NOT NULL,
  UNIQUE(meter_key_hash,reading_type,start_utc,end_utc,source_revision)
);

CREATE TABLE IF NOT EXISTS charge_session (
  id INTEGER PRIMARY KEY,
  session_key TEXT NOT NULL UNIQUE,
  plug_epoch TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('ARMED','CHARGING','FINALIZING','CLOSED','ANOMALY')),
  started_at TEXT,
  ended_at TEXT,
  energy_wh INTEGER,
  max_counter_wh INTEGER NOT NULL DEFAULT 0,
  power_coverage_basis_points INTEGER,
  pricing_method TEXT,
  evidence_status TEXT NOT NULL,
  last_event_at TEXT NOT NULL,
  finalize_started_at TEXT,
  stable_count INTEGER NOT NULL DEFAULT 0,
  row_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS public_charge (
  id INTEGER PRIMARY KEY,
  external_key TEXT NOT NULL,
  revision INTEGER NOT NULL,
  supersedes_id INTEGER REFERENCES public_charge(id),
  started_at TEXT NOT NULL,
  provider TEXT NOT NULL,
  energy_wh INTEGER NOT NULL CHECK(energy_wh > 0),
  gross_micro_eur INTEGER NOT NULL CHECK(gross_micro_eur >= 0),
  evidence_id INTEGER REFERENCES evidence(id),
  verification_state TEXT NOT NULL CHECK(verification_state IN ('VERIFIED','UNVERIFIED','VOID')),
  claimable INTEGER NOT NULL CHECK(claimable IN (0,1)),
  CHECK(claimable=0 OR (verification_state='VERIFIED' AND evidence_id IS NOT NULL)),
  UNIQUE(external_key,revision)
);

CREATE TABLE IF NOT EXISTS reconciliation (
  id INTEGER PRIMARY KEY,
  month_revision_id INTEGER NOT NULL REFERENCES month_revision(id),
  dimension TEXT NOT NULL,
  invoice_wh INTEGER,
  measured_wh INTEGER,
  delta_wh INTEGER,
  tolerance_wh INTEGER,
  result TEXT NOT NULL CHECK(result IN ('PASS','FAIL','INCOMPLETE')),
  created_at TEXT NOT NULL,
  UNIQUE(month_revision_id,dimension)
);

CREATE TABLE IF NOT EXISTS idempotency_record (
  scope TEXT NOT NULL,
  key TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  response_code INTEGER NOT NULL,
  response_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(scope,key)
);

CREATE TABLE IF NOT EXISTS audit_event (
  id INTEGER PRIMARY KEY,
  occurred_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  object_type TEXT NOT NULL,
  object_id TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  previous_hash TEXT,
  event_hash TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS report_artifact (
  id INTEGER PRIMARY KEY,
  month_revision_id INTEGER NOT NULL REFERENCES month_revision(id),
  format TEXT NOT NULL CHECK(format IN ('CSV','PDF')),
  sha256 TEXT NOT NULL CHECK(length(sha256)=64),
  size_bytes INTEGER NOT NULL,
  storage_path TEXT NOT NULL UNIQUE,
  calculation_hash TEXT NOT NULL,
  UNIQUE(month_revision_id,format)
);

CREATE TABLE IF NOT EXISTS runtime_state (
  key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS locked_month_no_update
BEFORE UPDATE ON month_revision
WHEN OLD.state='LOCKED'
BEGIN SELECT RAISE(ABORT,'locked month revision is immutable'); END;

CREATE TRIGGER IF NOT EXISTS locked_month_no_delete
BEFORE DELETE ON month_revision
WHEN OLD.state='LOCKED'
BEGIN SELECT RAISE(ABORT,'locked month revision is immutable'); END;
