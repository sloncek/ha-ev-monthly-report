CREATE TABLE home_month_usage (
    year_month TEXT PRIMARY KEY,
    energy_wh INTEGER CHECK(energy_wh >= 0),
    source TEXT NOT NULL,
    quality TEXT NOT NULL,
    detail_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE vat_rate_schedule (
    effective_month TEXT PRIMARY KEY,
    basis_points INTEGER NOT NULL CHECK(basis_points BETWEEN 0 AND 10000),
    actor TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
