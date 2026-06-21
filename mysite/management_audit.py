from __future__ import annotations

import json
from datetime import datetime

import frappe

from mysite.management_permissions import get_roles


def _doctype_exists(doctype: str) -> bool:
    try:
        return bool(frappe.db.exists("DocType", doctype))
    except Exception:
        return False


def _request_meta() -> dict:
    req = getattr(frappe, "request", None)
    if not req:
        return {"request_id": "", "ip_address": "", "user_agent": ""}

    request_id = str(req.headers.get("X-Request-ID") or req.headers.get("X-Correlation-ID") or "").strip()
    ip_address = str(getattr(frappe.local, "request_ip", "") or req.remote_addr or "").strip()
    user_agent = str(req.headers.get("User-Agent") or "").strip()

    return {
        "request_id": request_id,
        "ip_address": ip_address,
        "user_agent": user_agent[:500],
    }


def log_event(
    *,
    module_key: str,
    action_key: str,
    target_type: str,
    target_key: str,
    result: str = "success",
    details: dict | None = None,
    change_request: str | None = None,
    actor: str | None = None,
):
    if not _doctype_exists("MS Management Audit Log"):
        return

    actor_user = str(actor or frappe.session.user or "Guest").strip() or "Guest"
    roles = sorted(get_roles(actor_user)) if actor_user != "Guest" else []
    meta = _request_meta()

    payload = {
        "doctype": "MS Management Audit Log",
        "module_key": str(module_key or "system").strip() or "system",
        "action_key": str(action_key or "unknown").strip() or "unknown",
        "target_type": str(target_type or "unknown").strip() or "unknown",
        "target_key": str(target_key or "").strip(),
        "change_request": str(change_request or "").strip(),
        "actor": actor_user,
        "actor_roles": ", ".join(roles),
        "result": str(result or "success").strip() or "success",
        "request_id": meta["request_id"],
        "ip_address": meta["ip_address"],
        "user_agent": meta["user_agent"],
        "details_json": json.dumps(details or {}, ensure_ascii=False),
        "occurred_at": datetime.utcnow().isoformat(sep=" ", timespec="seconds"),
    }

    try:
        frappe.get_doc(payload).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "MS Management Audit Log Failed")
