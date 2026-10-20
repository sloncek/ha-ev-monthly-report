import hashlib
import hmac
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from aiohttp import ClientTimeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util


def validate_backend_url(value):
    parsed=urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
        raise ValueError("backend URL must be a plain HTTP(S) origin without credentials, path, query or fragment")
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ValueError("invalid backend port")
    return value.rstrip("/")


class LedgerCoordinator(DataUpdateCoordinator):
    def __init__(self,hass,entry):
        super().__init__(hass,logger=__import__("logging").getLogger(__name__),name="energy_ledger",update_interval=timedelta(seconds=60))
        self.entry=entry; self.base_url=validate_backend_url(entry.data["url"]); self.read_token=entry.data["read_token"]; self.write_token=entry.data["write_token"]; self.signing_secret=entry.data["signing_secret"]; self.entry_id=entry.entry_id
        self.vehicle_name=entry.data.get("vehicle_name","EV")
        self.timezone=entry.data.get("timezone",hass.config.time_zone)
        self.selected_month=entry.options.get("selected_month",datetime.now(ZoneInfo(self.timezone)).strftime("%Y-%m")); self.months=[self.selected_month]
        self._usage_synced={}

    def _persist_month(self, month, latest_imported_month=None):
        options=dict(self.entry.options)
        options["selected_month"]=month
        if latest_imported_month is not None:
            options["last_imported_month"]=latest_imported_month
        if options != dict(self.entry.options):
            self.hass.config_entries.async_update_entry(self.entry, options=options)

    async def async_select_month(self, month):
        if month not in self.months:
            raise ValueError("month is not available")
        self.selected_month=month
        self._persist_month(month)
        await self.async_request_refresh()

    def headers(self,method,actor="ha-system"):
        if method.upper()=="GET": return {"Authorization":f"Bearer {self.read_token}"}
        timestamp=str(int(time.time())); signature=hmac.new(self.signing_secret.encode(),f"{timestamp}:{actor}".encode(),hashlib.sha256).hexdigest()
        return {"Authorization":f"Bearer {self.write_token}","X-HA-User":actor,"X-HA-Timestamp":timestamp,"X-HA-Signature":signature}

    async def request(self,method,path,actor="ha-system",**kwargs):
        if not path.startswith("/api/v1/"): raise UpdateFailed("backend path is not allowlisted")
        session=async_get_clientsession(self.hass)
        async with session.request(method,self.base_url+path,headers=self.headers(method,actor),timeout=ClientTimeout(total=15,connect=3),**kwargs) as response:
            if response.status>=400: raise UpdateFailed(f"ledger returned HTTP {response.status}")
            return await response.json()

    async def _async_update_data(self):
        try:
            months=await self.request("GET","/api/v1/months"); self.months=months.get("months") or [self.selected_month]
            latest=months.get("latest_imported_month")
            if latest and latest in self.months and latest != self.entry.options.get("last_imported_month"):
                self.selected_month=latest
                self._persist_month(latest, latest)
            if self.selected_month not in self.months: self.months.insert(0,self.selected_month)
            from .monthly_usage import async_sync_month
            now=datetime.now(ZoneInfo(self.timezone))
            current=now.strftime("%Y-%m")
            previous=(now.replace(day=1)-timedelta(days=1)).strftime("%Y-%m")
            for month in dict.fromkeys((self.selected_month,previous,current)):
                if time.monotonic()-self._usage_synced.get(month,-3601) >= 3600:
                    try:
                        await async_sync_month(self.hass,self,month)
                        self._usage_synced[month]=time.monotonic()
                    except Exception as exc:
                        __import__("logging").getLogger(__name__).warning("Vehicle energy history deferred for %s: %s",month,type(exc).__name__)
            await self.request("POST","/api/v1/runtime/ha-heartbeat",json={"entry_id":self.entry_id})
            # A selection can change while the network request is in flight.
            # Never publish the previous month's values under the new selector.
            while True:
                month=self.selected_month
                data=await self.request("GET",f"/api/v1/months/{month}/summary")
                if month==self.selected_month:
                    if data.get("month")!=month: raise UpdateFailed("backend returned a different report month")
                    break
            return data
        except Exception as exc: raise UpdateFailed(str(exc)) from exc
