CREATE TABLE ev_register_month (
 year_month TEXT PRIMARY KEY,
 legacy_json TEXT,
 source_sha256 TEXT,
 source_sheet TEXT,
 source_row INTEGER,
 odometer_km INTEGER CHECK(odometer_km >= 0),
 observed_at TEXT,
 odometer_source TEXT,
 snapshot_json TEXT,
 updated_at TEXT NOT NULL
);
CREATE TABLE ev_reimbursement_rate (
 effective_month TEXT PRIMARY KEY,
 rate TEXT NOT NULL,
 actor TEXT NOT NULL,
 updated_at TEXT NOT NULL
);
CREATE TABLE ev_register_expense (
 id INTEGER PRIMARY KEY,
 year_month TEXT NOT NULL,
 occurred_date TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('PUBLIC','OTHER')),
 provider TEXT NOT NULL,
 gross_cents INTEGER NOT NULL CHECK(gross_cents >= 0),
 energy_wh INTEGER CHECK(energy_wh >= 0),
 eligible INTEGER NOT NULL CHECK(eligible IN (0,1)),
 notes TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE INDEX ev_register_expense_month ON ev_register_expense(year_month);
CREATE TABLE ev_register_request (
 idempotency_key TEXT PRIMARY KEY,
 payload_json TEXT NOT NULL,
 response_json TEXT NOT NULL,
 created_at TEXT NOT NULL
);
