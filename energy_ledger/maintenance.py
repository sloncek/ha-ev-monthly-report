from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .db import Database
from .settings import Settings


def database() -> tuple[Database, Settings]:
    settings = Settings.load()
    settings.prepare()
    root = Path(__file__).resolve().parents[1]
    return Database(settings.data_dir / "ledger.sqlite3", root / "migrations"), settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Energy Ledger online backup and restore verifier")
    sub = parser.add_subparsers(dest="command", required=True)
    backup = sub.add_parser("backup")
    backup.add_argument("path", nargs="?")
    verify = sub.add_parser("verify")
    verify.add_argument("path")
    args = parser.parse_args()
    db, settings = database()
    if args.command == "backup":
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = Path(args.path) if args.path else settings.data_dir / "backups" / f"ledger-{stamp}.sqlite3"
        result = db.online_backup(destination)
    else:
        result = db.verify_restore(Path(args.path))
    print(json.dumps(result, sort_keys=True))
    if not result.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
