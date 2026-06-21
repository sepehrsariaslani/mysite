from __future__ import annotations

import json
from datetime import date, timedelta

import frappe
from frappe import _
from frappe.utils import cint, now_datetime

from mysite.management_audit import log_event as audit_log_event
from mysite.management_permissions import has_capability, is_super_admin, require_capability

WORKFLOW_STATES = {
    "Draft",
    "In Review",
    "Approved",
    "Rejected",
    "Published",
    "Cancelled",
}

WORKFLOW_ACTIONS = {
    "create_draft",
    "submit_review",
    "return_to_draft",
    "approve",
    "reject",
    "publish",
    "cancel",
}

CONTENT_TARGETS = {
    "page_config",
    "page_content_override",
    "page_visual_override",
    "visual_source",
    "blog_post",
    "blog_delete",
}

PRODUCT_TARGETS = {
    "product_update",
    "product_media_attach",
    "product_media_remove",
    "product_media_primary",
}


def _doctype_exists(doctype: str) -> bool:
    try:
        return bool(frappe.db.exists("DocType", doctype))
    except Exception:
        return False


def _workflow_settings() -> dict:
    defaults = {
        "enforce_workflow": 0,
        "shadow_mode": 1,
        "shadow_until": (date.today() + timedelta(days=7)).isoformat(),
        "allow_system_manager_bypass": 1,
        "notify_on_submit_review": 1,
        "notify_on_approve": 1,
    }

    if not _doctype_exists("MS Management Workflow Settings"):
        return defaults

    try:
        doc = frappe.get_cached_doc("MS Management Workflow Settings", "MS Management Workflow Settings")
        for key in defaults:
            value = doc.get(key)
            if value not in (None, ""):
                defaults[key] = value
    except Exception:
        pass
    return defaults


def workflow_mode() -> dict:
    cfg = _workflow_settings()
    return {
        "enforce_workflow": cint(cfg.get("enforce_workflow") or 0) == 1,
        "shadow_mode": cint(cfg.get("shadow_mode") if cfg.get("shadow_mode") is not None else 1) == 1,
        "shadow_until": str(cfg.get("shadow_until") or ""),
        "allow_system_manager_bypass": cint(cfg.get("allow_system_manager_bypass") if cfg.get("allow_system_manager_bypass") is not None else 1)
        == 1,
        "notify_on_submit_review": cint(cfg.get("notify_on_submit_review") if cfg.get("notify_on_submit_review") is not None else 1)
        == 1,
        "notify_on_approve": cint(cfg.get("notify_on_approve") if cfg.get("notify_on_approve") is not None else 1) == 1,
    }


def _capability_for_action(module_key: str, action: str) -> str:
    module = str(module_key or "").strip().lower()
    action = str(action or "").strip().lower()

    if module == "content":
        if action in {"submit_review", "create_draft"}:
            return "content.edit"
        if action in {"approve", "reject", "return_to_draft"}:
            return "content.review"
        if action in {"publish", "cancel"}:
            return "content.publish"
        return "content.edit"

    if module == "product":
        if action in {"submit_review", "create_draft"}:
            return "product.edit"
        if action in {"approve", "reject", "return_to_draft"}:
            return "product.review"
        if action in {"publish", "cancel"}:
            return "product.publish"
        return "product.edit"

    return "management.access"


def should_enforce(module_key: str, *, user: str | None = None, bypass_requested: bool = False) -> bool:
    mode = workflow_mode()
    if not mode["enforce_workflow"]:
        return False

    if bypass_requested and mode["allow_system_manager_bypass"] and is_super_admin(user):
        return False

    return str(module_key or "").strip().lower() in {"content", "product"}


def _normalize_json(value) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        try:
            json.loads(value)
            return value
        except Exception:
            return json.dumps({"value": value}, ensure_ascii=False)
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps({"value": value}, ensure_ascii=False)


def _ensure_request_event_table(doc, action: str, from_state: str, to_state: str, comment: str = ""):
    row = {
        "action": action,
        "from_state": from_state,
        "to_state": to_state,
        "actor": frappe.session.user,
        "comment": str(comment or "").strip(),
        "action_at": now_datetime(),
    }
    doc.append("events", row)


def create_change_request(
    *,
    module_key: str,
    target_type: str,
    target_key: str,
    request_payload,
    current_snapshot=None,
    diff_summary=None,
    source_endpoint: str = "",
    initial_state: str = "Draft",
    is_shadow_record: bool = False,
    publish_result=None,
    error_message: str = "",
):
    if not _doctype_exists("MS Management Change Request"):
        return {"name": "", "state": initial_state, "available": False}

    state = str(initial_state or "Draft").strip()
    if state not in WORKFLOW_STATES:
        state = "Draft"

    payload = {
        "doctype": "MS Management Change Request",
        "module_key": str(module_key or "").strip(),
        "target_type": str(target_type or "").strip(),
        "target_key": str(target_key or "").strip(),
        "state": state,
        "request_payload_json": _normalize_json(request_payload),
        "current_snapshot_json": _normalize_json(current_snapshot or {}),
        "diff_summary_json": _normalize_json(diff_summary or {}),
        "requested_by": frappe.session.user,
        "requested_at": now_datetime(),
        "latest_comment": "",
        "source_endpoint": str(source_endpoint or "").strip(),
        "is_shadow_record": 1 if is_shadow_record else 0,
        "publish_result_json": _normalize_json(publish_result or {}),
        "error_message": str(error_message or "").strip(),
    }

    doc = frappe.get_doc(payload)
    _ensure_request_event_table(doc, "create_draft", "", state)
    doc.insert(ignore_permissions=True)

    return {"name": doc.name, "state": doc.state, "available": True}


def _allowed_transition(doc, action: str):
    current = str(doc.state or "Draft")
    if action == "submit_review" and current == "Draft":
        return "In Review"
    if action == "return_to_draft" and current == "In Review":
        return "Draft"
    if action == "approve" and current == "In Review":
        return "Approved"
    if action == "reject" and current == "In Review":
        return "Rejected"
    if action == "publish" and current == "Approved":
        return "Published"
    if action == "cancel" and current in {"Draft", "In Review", "Approved"}:
        return "Cancelled"
    return ""


def transition_change_request(name: str, action: str, comment: str = ""):
    if not _doctype_exists("MS Management Change Request"):
        frappe.throw(_("DocType گردش‌کار مدیریت در سیستم موجود نیست."))

    req_name = str(name or "").strip()
    if not req_name or not frappe.db.exists("MS Management Change Request", req_name):
        frappe.throw(_("درخواست تغییر پیدا نشد."))

    action_key = str(action or "").strip()
    if action_key not in WORKFLOW_ACTIONS:
        frappe.throw(_("اکشن گردش‌کار معتبر نیست."))

    doc = frappe.get_doc("MS Management Change Request", req_name)

    capability = _capability_for_action(doc.module_key, action_key)
    require_capability(capability)

    next_state = _allowed_transition(doc, action_key)
    if not next_state:
        frappe.throw(_("تغییر وضعیت درخواست در این مرحله مجاز نیست."), frappe.ValidationError)

    previous = str(doc.state or "Draft")
    doc.state = next_state
    doc.latest_comment = str(comment or "").strip()

    if action_key in {"approve", "reject", "return_to_draft"}:
        doc.reviewed_by = frappe.session.user
        doc.reviewed_at = now_datetime()

    if action_key == "approve":
        doc.approved_by = frappe.session.user
        doc.approved_at = now_datetime()

    if action_key == "publish":
        doc.published_by = frappe.session.user
        doc.published_at = now_datetime()

    _ensure_request_event_table(doc, action_key, previous, next_state, comment=comment)
    doc.save(ignore_permissions=True)
    return doc


def list_change_requests(module_key: str | None = None, state: str | None = None, limit: int = 50, offset: int = 0):
    if not _doctype_exists("MS Management Change Request"):
        return {"items": [], "total": 0, "limit": 0, "offset": 0}

    filters = {}
    module = str(module_key or "").strip()
    if module:
        filters["module_key"] = module
    state_value = str(state or "").strip()
    if state_value:
        filters["state"] = state_value

    limit = min(max(int(limit or 50), 1), 200)
    offset = max(int(offset or 0), 0)

    rows = frappe.get_all(
        "MS Management Change Request",
        filters=filters,
        fields=[
            "name",
            "module_key",
            "target_type",
            "target_key",
            "state",
            "requested_by",
            "requested_at",
            "reviewed_by",
            "reviewed_at",
            "approved_by",
            "approved_at",
            "published_by",
            "published_at",
            "latest_comment",
            "is_shadow_record",
            "modified",
        ],
        order_by="modified desc",
        start=offset,
        limit_page_length=limit,
    )

    total = frappe.db.count("MS Management Change Request", filters=filters)
    return {
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def get_change_request(name: str):
    if not _doctype_exists("MS Management Change Request"):
        return None
    req_name = str(name or "").strip()
    if not req_name or not frappe.db.exists("MS Management Change Request", req_name):
        return None
    return frappe.get_doc("MS Management Change Request", req_name)


def parse_request_payload(doc) -> dict:
    try:
        payload = json.loads(str(doc.request_payload_json or "{}"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def shadow_create_if_enabled(
    *,
    module_key: str,
    target_type: str,
    target_key: str,
    request_payload,
    current_snapshot=None,
    diff_summary=None,
    source_endpoint: str = "",
    publish_result=None,
):
    mode = workflow_mode()
    if not mode.get("shadow_mode", True):
        return {"name": "", "state": "Published", "available": False}

    return create_change_request(
        module_key=module_key,
        target_type=target_type,
        target_key=target_key,
        request_payload=request_payload,
        current_snapshot=current_snapshot,
        diff_summary=diff_summary,
        source_endpoint=source_endpoint,
        initial_state="Published",
        is_shadow_record=True,
        publish_result=publish_result or {},
    )


def module_for_target_type(target_type: str) -> str:
    value = str(target_type or "").strip()
    if value in CONTENT_TARGETS:
        return "content"
    if value in PRODUCT_TARGETS:
        return "product"
    return "content"


def default_capability_for_target(target_type: str, action: str = "create_draft") -> str:
    return _capability_for_action(module_for_target_type(target_type), action)


def can_publish_target(target_type: str, user: str | None = None) -> bool:
    capability = default_capability_for_target(target_type, "publish")
    return has_capability(capability, user=user)


def auto_enable_enforce_if_due():
    if not _doctype_exists("MS Management Workflow Settings"):
        return

    settings = workflow_mode()
    if not settings.get("shadow_mode", True):
        return
    shadow_until = str(settings.get("shadow_until") or "").strip()
    if not shadow_until:
        return

    today = date.today().isoformat()
    if shadow_until > today:
        return

    doc = frappe.get_doc("MS Management Workflow Settings", "MS Management Workflow Settings")
    if cint(doc.get("enforce_workflow") or 0) == 1:
        return

    doc.shadow_mode = 0
    doc.enforce_workflow = 1
    doc.save(ignore_permissions=True)
    audit_log_event(
        module_key="system",
        action_key="workflow.auto_enforce_enabled",
        target_type="workflow_settings",
        target_key="MS Management Workflow Settings",
        result="success",
        details={"shadow_until": shadow_until, "enabled_at": now_datetime().isoformat()},
    )
    frappe.db.commit()
