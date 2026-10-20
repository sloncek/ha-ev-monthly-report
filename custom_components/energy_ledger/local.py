"""In-memory adapter for the bundled engine. This never opens a network socket."""
import asyncio
from pathlib import Path

import httpx

from .backend.engine import create_app


class LedgerError(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail


class LocalLedgerClient:
    def __init__(self, data_dir: Path, config: dict):
        self.app = create_app(data_dir, config)

    async def async_start(self):
        self._lifespan = self.app.router.lifespan_context(self.app)
        await self._lifespan.__aenter__()

    async def async_stop(self):
        await self._lifespan.__aexit__(None, None, None)

    def request(self, method, path, actor="ha-system", **kwargs):
        """Run in HA's executor; file IO and PDF uploads stay off its event loop."""
        if not path.startswith("/api/v1/"):
            raise LedgerError(400, "invalid internal path")
        async def call():
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(transport=transport, base_url="http://ledger.internal") as client:
                headers = {"X-HA-User": actor, **kwargs.pop("headers", {})}
                response = await client.request(method, path, headers=headers, **kwargs)
                if response.status_code >= 400:
                    try:
                        detail = response.json().get("detail", "Ledger request failed")
                    except ValueError:
                        detail = "Ledger request failed"
                    raise LedgerError(response.status_code, detail if isinstance(detail, str) else "Invalid input")
                return response.json()
        return asyncio.run(call())
