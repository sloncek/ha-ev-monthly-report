from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


def configured_timezone() -> str:
    config_path = Path(os.getenv("LEDGER_CONFIG", "./config/config.json"))
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    return str(config.get("timezone", "UTC"))


def secret(path_env: str, fallback: str) -> str:
    path = Path(os.getenv(path_env, fallback))
    return path.read_text().strip() if path.exists() else ""


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    config: dict
    vehicle_name: str
    timezone: str
    odometer_entity: str
    home_energy_statistic: str
    read_token: str
    write_token: str
    signing_secret: str
    shadow_mode: bool

    @classmethod
    def load(cls):
        data_dir = Path(os.getenv("LEDGER_DATA_DIR", "./data")).resolve()
        config_path = Path(os.getenv("LEDGER_CONFIG", "./config/config.json"))
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
        return cls(
            data_dir=data_dir,
            config=config,
            vehicle_name=str(config.get("vehicle_name", "Electric vehicle")),
            timezone=str(config.get("timezone", "UTC")),
            odometer_entity=str(config.get("odometer_entity", "")),
            home_energy_statistic=str(config.get("home_energy_statistic", "")),
            read_token=secret("LEDGER_READ_TOKEN_FILE", "./secrets/read_token"),
            write_token=secret("LEDGER_WRITE_TOKEN_FILE", "./secrets/write_token"),
            signing_secret=secret("LEDGER_HA_SIGNING_SECRET_FILE", "./secrets/ha_signing_secret"),
            shadow_mode=os.getenv("LEDGER_SHADOW_MODE", "true").lower() == "true",
        )

    def prepare(self):
        self.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in ("evidence", "inbox", "outbox", "reports/staging", "reports/final", "backups"):
            path = self.data_dir / name
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.chmod(0o700)
