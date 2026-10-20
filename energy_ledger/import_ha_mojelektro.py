from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Moj Elektro credentials from a local HA config-entry export")
    parser.add_argument("--entries", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--token-file", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.entries.read_text())
    entries = [entry for entry in payload["data"]["entries"] if entry.get("domain") == "mojelektro" and not entry.get("disabled_by")]
    if len(entries) != 1:
        raise SystemExit(f"expected exactly one active mojelektro entry, found {len(entries)}")
    source = entries[0].get("data", {})
    token = source.get("token", "").strip()
    meter_id = source.get("meter_id", "").strip()
    if not token or not meter_id:
        raise SystemExit("active mojelektro entry is missing token or meter_id")
    config = json.loads(args.config.read_text())
    config.setdefault("moj_elektro", {}).update({"enabled": True, "usage_point": meter_id})
    token_temp = args.token_file.with_name(f".{args.token_file.name}.tmp")
    config_temp = args.config.with_name(f".{args.config.name}.tmp")
    token_temp.write_text(token)
    token_temp.chmod(0o600)
    config_temp.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    config_temp.chmod(0o600)
    os.replace(token_temp, args.token_file)
    os.replace(config_temp, args.config)
    print(json.dumps({"enabled": True, "token_present": True, "usage_point_present": True}))


if __name__ == "__main__":
    main()
