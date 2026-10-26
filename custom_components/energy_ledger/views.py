"""Home Assistant HTTP views backed by the local reporting engine."""
import base64
import binascii
import hmac
import re
import uuid

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.auth import KEY_HASS_USER
from homeassistant.helpers.http import KEY_HASS

from .const import DOMAIN
from .local import LedgerError

_MAX_FILE = 15 * 1024 * 1024
_MONTH = r"\d{4}-(0[1-9]|1[0-2])"
_SHEET_EXPORT_FIELDS = (
    "month", "status", "odometer_km", "monthly_distance_km", "home_kwh",
    "reimbursement_rate", "home_reimbursement_eur", "public_gross_eur",
    "other_gross_eur", "eligible_expenses_eur", "monthly_eligible_eur",
    "opening_balance_eur", "requested_eur", "reported_eur", "closing_balance_eur",
    "pending_home_delta_eur", "pending_delta_verified", "energy_complete",
    "month_complete", "source_quality", "ready_to_report", "public_energy_complete",
    "current_home_kwh", "current_source_quality", "reported_at",
)


def coordinator_for(request):
    if not request[KEY_HASS_USER].is_admin:
        raise web.HTTPForbidden()
    entries = request.app[KEY_HASS].data.get(DOMAIN, {})
    for value in entries.values():
        if hasattr(value, "request"):
            return value
    raise web.HTTPServiceUnavailable(text="Energy Ledger is not loaded")


def coordinator_for_sheet_export(request):
    """Find the configured ledger without granting general HA API access."""
    entries = request.app[KEY_HASS].data.get(DOMAIN, {})
    for value in entries.values():
        if hasattr(value, "request"):
            return value
    raise web.HTTPServiceUnavailable(text="Energy Ledger is not loaded")


class LedgerProxyView(HomeAssistantView):
    url = "/api/energy_ledger/{action}"
    name = "api:energy_ledger"
    requires_auth = True

    async def get(self, request, action):
        coordinator = coordinator_for(request)
        if action == "register-history":
            path = "/api/v1/register/history"
        elif re.fullmatch(rf"register-{_MONTH}", action):
            path = f"/api/v1/months/{action.removeprefix('register-')}/register"
        elif re.fullmatch(rf"mileage-forecast-{_MONTH}", action):
            path = f"/api/v1/months/{action.removeprefix('mileage-forecast-')}/mileage-forecast"
        elif re.fullmatch(r"invoice-job-(latest|[a-f0-9]{32})", action):
            path = f"/api/v1/invoice-jobs/{action.removeprefix('invoice-job-')}"
        else:
            raise web.HTTPNotFound()
        try:
            return web.json_response(await coordinator.request("GET", path))
        except LedgerError as exc:
            return web.json_response({"detail": exc.detail}, status=exc.status)

    async def post(self, request, action):
        coordinator = coordinator_for(request)
        payload = await request.json()
        if not isinstance(payload, dict):
            raise web.HTTPBadRequest(text="JSON object required")
        actor = str(request[KEY_HASS_USER].id)
        register_actions = {"register-expense": "/api/v1/register/expense",
                            "register-reported": "reported", "register-rate": "reimbursement-rate",
                            "register-odometer": "odometer"}
        try:
            if action in register_actions:
                month = payload.get("month", "")
                if not isinstance(month, str) or not re.fullmatch(_MONTH, month):
                    raise web.HTTPBadRequest(text="invalid month")
                path = register_actions[action] if action == "register-expense" else f"/api/v1/months/{month}/{register_actions[action]}"
                if action != "register-expense":
                    payload.pop("month")
                result = await coordinator.request("POST", path, actor=actor, json=payload)
                await coordinator.async_request_refresh()
                return web.json_response(result, status=201 if action == "register-expense" else 200)
            if action not in {"invoice", "public-charge"}:
                raise web.HTTPNotFound()
            encoded = payload.pop("data_base64", "")
            if not isinstance(encoded, str) or len(encoded) > 4 * ((_MAX_FILE + 2) // 3):
                raise web.HTTPRequestEntityTooLarge(max_size=_MAX_FILE, actual_size=len(encoded) if isinstance(encoded, str) else 0)
            try:
                raw = base64.b64decode(encoded, validate=True) if encoded else b""
            except (binascii.Error, ValueError, TypeError):
                raise web.HTTPBadRequest(text="invalid base64 evidence") from None
            if len(raw) > _MAX_FILE:
                raise web.HTTPRequestEntityTooLarge(max_size=_MAX_FILE, actual_size=len(raw))
            filename = str(payload.get("filename", "invoice.pdf"))[:200]
            headers = {"Idempotency-Key": str(payload.get("idempotency_key", uuid.uuid4().hex))[:200]}
            if action == "invoice":
                result = await coordinator.request("POST", "/api/v1/invoices", actor=actor,
                    files={"file": (filename, raw, "application/pdf")}, headers=headers)
                return web.json_response(result, status=202)
            keys = ("started_at", "provider", "energy_kwh", "gross_eur", "external_key")
            if any(key not in payload for key in keys):
                raise web.HTTPBadRequest(text="missing charge fields")
            files = {"evidence": (filename, raw, str(payload.get("content_type", "application/octet-stream")))} if raw else None
            result = await coordinator.request("POST", "/api/v1/public-charges", actor=actor,
                data={key: str(payload[key]) for key in keys}, files=files, headers=headers)
            await coordinator.async_request_refresh()
            return web.json_response(result, status=201)
        except LedgerError as exc:
            return web.json_response({"detail": exc.detail}, status=exc.status)


class LedgerSheetExportView(HomeAssistantView):
    """Read-only, token-scoped export containing monthly summary fields only."""

    url = "/api/energy_ledger/sheet-export"
    name = "api:energy_ledger:sheet-export"
    requires_auth = False

    async def get(self, request):
        coordinator = coordinator_for_sheet_export(request)
        expected = coordinator.config.get("sheet_export_token", "")
        authorization = request.headers.get("Authorization", "")
        supplied = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
        if not expected or not supplied or not hmac.compare_digest(
            supplied.encode("utf-8"), expected.encode("utf-8")
        ):
            raise web.HTTPUnauthorized(headers={"Cache-Control": "no-store"})

        try:
            history = await coordinator.request("GET", "/api/v1/register/history")
        except LedgerError as exc:
            return web.json_response(
                {"detail": exc.detail}, status=exc.status, headers={"Cache-Control": "no-store"}
            )

        months = history.get("months", []) if isinstance(history, dict) else []
        projected = [
            {field: month.get(field) for field in _SHEET_EXPORT_FIELDS}
            for month in months
            if isinstance(month, dict) and re.fullmatch(_MONTH, str(month.get("month", "")))
        ]
        return web.json_response(
            {"schema_version": 1, "months": projected},
            headers={"Cache-Control": "no-store"},
        )
