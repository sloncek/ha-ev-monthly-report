CREATE TABLE IF NOT EXISTS invoice_pipeline (
  id INTEGER PRIMARY KEY,
  invoice_id INTEGER NOT NULL UNIQUE REFERENCES invoice(id),
  year_month TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('PENDING','RUNNING','COMPLETE','INCOMPLETE','ERROR')),
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  retryable INTEGER NOT NULL DEFAULT 1 CHECK(retryable IN (0,1)),
  detail TEXT,
  next_attempt_at TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  row_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS invoice_import_job (
  job_id TEXT PRIMARY KEY,
  evidence_id INTEGER NOT NULL REFERENCES evidence(id),
  state TEXT NOT NULL CHECK(state IN ('PENDING','VALID','REVIEW','REJECTED','CONFLICT')),
  invoice_id INTEGER REFERENCES invoice(id),
  year_month TEXT,
  detail TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_invoice_pipeline_work
ON invoice_pipeline(state,next_attempt_at,id);
