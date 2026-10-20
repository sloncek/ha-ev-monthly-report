from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlencode

import httpx


READING_TYPES = {
    "interval": "32.0.2.4.1.2.12.0.0.0.0.0.0.0.0.3.72.0",
    "total": "32.0.4.1.1.2.12.0.0.0.0.0.0.0.0.3.72.0",
    "peak": "32.0.4.1.1.2.12.0.0.0.0.1.0.0.0.3.72.0",
    "offpeak": "32.0.4.1.1.2.12.0.0.0.0.2.0.0.0.3.72.0",
}


class MojElektroAdapter:
    def __init__(self, base_url: str, usage_point: str, token_file: Path):
        self.base_url = base_url.rstrip("/")
        self.usage_point = usage_point
        self.token_file = token_file

    def _token(self) -> str:
        token = self.token_file.read_text().strip()
        if not token:
            raise RuntimeError("Moj Elektro token is not configured")
        return token

    def fetch(self, start: date, end_exclusive: date, reading_type: str) -> tuple[bytes, dict]:
        params = [("usagePoint", self.usage_point), ("startTime", start.isoformat()), ("endTime", end_exclusive.isoformat()), ("option", f"ReadingType={reading_type}")]
        request_hash = hashlib.sha256(urlencode(params).encode()).hexdigest()
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{self.base_url}/meter-readings", params=params, headers={"accept":"application/json","X-API-TOKEN":self._token()})
            response.raise_for_status()
            return response.content, {"request_hash": request_hash, "json": response.json()}

    @staticmethod
    def chunks(start: date, end_exclusive: date):
        cursor = start
        while cursor < end_exclusive:
            chunk_end = min(cursor + timedelta(days=31), end_exclusive)
            yield cursor, chunk_end
            cursor = chunk_end - timedelta(days=3) if chunk_end < end_exclusive else chunk_end

    @staticmethod
    def wh(value: str) -> int:
        return int((Decimal(value) * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
