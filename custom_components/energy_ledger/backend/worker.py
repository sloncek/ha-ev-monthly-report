from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from .parser import ParseReject, ParseReview, parse_invoice_pdf


def process_once(inbox: Path, outbox: Path, timezone_name: str = "UTC") -> int:
    count = 0
    for path in sorted(inbox.glob("*.pdf")):
        if any(outbox.glob(f"{path.stem}.*")):
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            payload = {"sha256": digest, "status": "VALID", "invoice": parse_invoice_pdf(path, timezone_name).to_dict()}
        except ParseReview as exc:
            payload = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "status": "REVIEW", "error": type(exc).__name__, "detail": str(exc)[:500]}
        except (ParseReject, Exception) as exc:
            payload = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "status": "REJECTED", "error": type(exc).__name__, "detail": str(exc)[:500]}
        target = outbox / f"{path.stem}.json"
        temp = outbox / f".{path.stem}.tmp"
        temp.write_text(json.dumps(payload, sort_keys=True))
        os.replace(temp, target)
        count += 1
    return count


def main() -> None:
    inbox = Path(os.getenv("LEDGER_INBOX", "/inbox"))
    outbox = Path(os.getenv("LEDGER_OUTBOX", "/outbox"))
    while True:
        process_once(inbox, outbox)
        time.sleep(2)


if __name__ == "__main__":
    main()
