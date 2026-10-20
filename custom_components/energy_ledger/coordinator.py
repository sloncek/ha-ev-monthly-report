import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .local import LocalLedgerClient, LedgerError

_LOGGER = logging.getLogger(__name__)


class LedgerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, logger=_LOGGER, name="energy_ledger", update_interval=timedelta(seconds=60))
        self.entry = entry
        self.entry_id = entry.entry_id
        self.config = {**entry.data, **entry.options}
        self.vehicle_name = self.config.get("vehicle_name", "EV")
        self.timezone = self.config.get("timezone", hass.config.time_zone)
        self.selected_month = entry.options.get("selected_month", datetime.now(ZoneInfo(self.timezone)).strftime("%Y-%m"))
        self.months = [self.selected_month]
        self._usage_synced = {}
        self._client = None

    async def async_initialize(self):
        data_dir = Path(self.hass.config.path(".storage", "energy_ledger", self.entry_id))
        config = {**self.config, "timezone": self.timezone, "vehicle_name": self.vehicle_name}
        token = config.get("moj_elektro_token", "")
        usage_point = config.get("moj_elektro_usage_point", "")
        if token and usage_point:
            config["moj_elektro"] = {"enabled": True, "usage_point": usage_point}
        if config.get("allowance_km") and config.get("contract_end_month"):
            config["mileage_plan"] = {"allowance_km": config["allowance_km"], "contract_end_month": config["contract_end_month"]}
        def initialize():
            client = LocalLedgerClient(data_dir, config)
            if token:
                token_file = data_dir / "moj_elektro_token"
                token_file.write_text(token)
                token_file.chmod(0o600)
            return client
        self._client = await self.hass.async_add_executor_job(initialize)
        await self._client.async_start()

    async def async_stop(self, _event=None):
        if self._client:
            await self._client.async_stop()
            self._client = None

    def _persist_month(self, month, latest_imported_month=None):
        options = dict(self.entry.options)
        options["selected_month"] = month
        if latest_imported_month is not None:
            options["last_imported_month"] = latest_imported_month
        if options != dict(self.entry.options):
            self.hass.config_entries.async_update_entry(self.entry, options=options)

    async def async_select_month(self, month):
        if month not in self.months:
            raise ValueError("month is not available")
        self.selected_month = month
        self._persist_month(month)
        await self.async_request_refresh()

    async def request(self, method, path, actor="ha-system", **kwargs):
        if self._client is None:
            raise UpdateFailed("Local ledger is not initialized")
        return await self.hass.async_add_executor_job(
            lambda: self._client.request(method, path, actor=actor, **kwargs)
        )

    async def _async_update_data(self):
        try:
            months = await self.request("GET", "/api/v1/months")
            self.months = months.get("months") or [self.selected_month]
            latest = months.get("latest_imported_month")
            if latest and latest in self.months and latest != self.entry.options.get("last_imported_month"):
                self.selected_month = latest
                self._persist_month(latest, latest)
            if self.selected_month not in self.months:
                self.months.insert(0, self.selected_month)
            from .monthly_usage import async_sync_month
            now = datetime.now(ZoneInfo(self.timezone))
            current = now.strftime("%Y-%m")
            previous = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
            for month in dict.fromkeys((self.selected_month, previous, current)):
                if time.monotonic() - self._usage_synced.get(month, -3601) >= 3600:
                    try:
                        await async_sync_month(self.hass, self, month)
                        self._usage_synced[month] = time.monotonic()
                    except Exception as exc:
                        _LOGGER.warning("Vehicle energy history deferred for %s: %s", month, type(exc).__name__)
            await self.request("POST", "/api/v1/runtime/ha-heartbeat", json={"entry_id": self.entry_id})
            while True:
                month = self.selected_month
                data = await self.request("GET", f"/api/v1/months/{month}/summary")
                if month == self.selected_month:
                    if data.get("month") != month:
                        raise UpdateFailed("Local ledger returned a different report month")
                    return data
        except Exception as exc:
            raise UpdateFailed(f"Local ledger update failed: {type(exc).__name__}") from exc
