import base64
import binascii
import uuid
import re
from aiohttp import FormData, web
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.auth import KEY_HASS_USER
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.http import KEY_HASS
from .const import DOMAIN

class LedgerProxyView(HomeAssistantView):
    url="/api/energy_ledger/{action}"; name="api:energy_ledger"; requires_auth=True
    async def get(self,request,action):
        if not request[KEY_HASS_USER].is_admin: raise web.HTTPForbidden()
        if re.fullmatch(r"mileage-forecast-\d{4}-(0[1-9]|1[0-2])",action):
            coordinator=next(v for k,v in request.app[KEY_HASS].data[DOMAIN].items() if k!="panel_registered")
            month=action.removeprefix("mileage-forecast-")
            try: return web.json_response(await coordinator.request("GET",f"/api/v1/months/{month}/mileage-forecast"))
            except UpdateFailed: return web.json_response({"detail":"Napovedi trenutno ni mogoče pridobiti."},status=503)
        if action == "register-history" or re.fullmatch(r"register-\d{4}-(0[1-9]|1[0-2])",action):
            coordinator=next(v for k,v in request.app[KEY_HASS].data[DOMAIN].items() if k!="panel_registered")
            path="/api/v1/register/history" if action=="register-history" else f"/api/v1/months/{action.removeprefix('register-')}/register"
            try: return web.json_response(await coordinator.request("GET",path))
            except UpdateFailed: return web.json_response({"detail":"Evidence trenutno ni mogoče pridobiti."},status=503)
        if not action.startswith("invoice-job-"): raise web.HTTPNotFound()
        job_id=action.removeprefix("invoice-job-")
        if job_id!="latest" and (len(job_id)!=32 or any(c not in "0123456789abcdef" for c in job_id)): raise web.HTTPBadRequest()
        coordinator=next(v for k,v in request.app[KEY_HASS].data[DOMAIN].items() if k!="panel_registered")
        try:
            result=await coordinator.request("GET",f"/api/v1/invoice-jobs/{job_id}")
        except UpdateFailed as exc:
            if str(exc)=="ledger returned HTTP 404":
                return web.json_response({"detail":"invoice job not found"},status=404)
            return web.json_response({"detail":"Stanja obdelave trenutno ni mogoče pridobiti. Poskusi ponovno."},status=503)
        return web.json_response(result)
    async def post(self,request,action):
        user=request[KEY_HASS_USER]
        if not user.is_admin: raise web.HTTPForbidden()
        payload=await request.json()
        register_actions={"register-expense":"/api/v1/register/expense","register-reported":"reported","register-rate":"reimbursement-rate","register-odometer":"odometer"}
        if action in register_actions:
            if not isinstance(payload,dict): raise web.HTTPBadRequest()
            month=payload.get("month","")
            if not isinstance(month,str) or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])",month): raise web.HTTPBadRequest(text="invalid month")
            coordinator=next(v for k,v in request.app[KEY_HASS].data[DOMAIN].items() if k!="panel_registered")
            path=register_actions[action] if action=="register-expense" else f"/api/v1/months/{month}/{register_actions[action]}"
            if action!="register-expense": payload.pop("month")
            async with async_get_clientsession(request.app[KEY_HASS]).post(coordinator.base_url+path,headers=coordinator.headers("POST",str(user.id)),json=payload) as response:
                try: body=await response.json()
                except Exception: body={"detail":"Servis evidence trenutno ni dosegljiv."}
                result=web.json_response(body,status=response.status)
            if response.status<400: await coordinator.async_request_refresh()
            return result
        if action not in {"invoice","public-charge"}: raise web.HTTPNotFound()
        try:
            raw=base64.b64decode(payload.pop("data_base64",""),validate=True) if payload.get("data_base64") else b""
        except (binascii.Error, ValueError, TypeError):
            raise web.HTTPBadRequest(text="invalid base64 evidence")
        if len(raw)>15*1024*1024: raise web.HTTPRequestEntityTooLarge(max_size=15*1024*1024,actual_size=len(raw))
        coordinator=next(v for k,v in request.app[KEY_HASS].data[DOMAIN].items() if k!="panel_registered")
        form=FormData()
        if action=="invoice":
            form.add_field("file",raw,filename=payload.get("filename","invoice.pdf"),content_type="application/pdf"); path="/api/v1/invoices"
        else:
            for key in ("started_at","provider","energy_kwh","gross_eur","external_key"): form.add_field(key,str(payload[key]))
            if raw: form.add_field("evidence",raw,filename=payload.get("filename","evidence.bin"),content_type=payload.get("content_type","application/octet-stream"))
            path="/api/v1/public-charges"
        headers={**coordinator.headers("POST",str(user.id)),"Idempotency-Key":payload.get("idempotency_key",uuid.uuid4().hex)}
        async with async_get_clientsession(request.app[KEY_HASS]).post(coordinator.base_url+path,headers=headers,data=form) as response:
            try:
                body=await response.json()
            except Exception:
                body={"error":"energy_ledger_backend_error","status":response.status}
            return web.json_response(body,status=response.status)
