CREATE TABLE ev_fleet_plan (
 id INTEGER PRIMARY KEY CHECK(id=1),
 source_sha256 TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 updated_at TEXT NOT NULL
);
