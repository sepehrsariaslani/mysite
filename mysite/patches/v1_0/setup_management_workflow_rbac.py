from __future__ import annotations

from datetime import date, timedelta

import frappe
from frappe.utils import now_datetime


ROLE_NAMES = [
    "Mysite Content Editor",
    "Mysite Content Reviewer",
    "Mysite Content Publisher",
    "Mysite Product Editor",
    "Mysite Product Reviewer",
    "Mysite Product Publisher",
    "Mysite Support Manager",
    "Mysite Analytics Manager",
    "Mysite Audit Viewer",
]

DEFAULT_ALERTS = [
    {
        "metric_key": "conversion_rate",
        "operator": "<",
        "threshold_value": 1,
        "window_days": 7,
        "is_active": 0,
        "notify_email": 1,
        "notify_notification_log": 1,
        "recipients": "",
    },
    {
        "metric_key": "revenue_drop_percent",
        "operator": ">=",
        "threshold_value": 25,
        "window_days": 7,
        "is_active": 0,
        "notify_email": 1,
        "notify_notification_log": 1,
        "recipients": "",
    },
    {
        "metric_key": "sla_failed_ratio",
        "operator": ">=",
        "threshold_value": 15,
        "window_days": 7,
        "is_active": 0,
        "notify_email": 1,
        "notify_notification_log": 1,
        "recipients": "",
    },
]


def _doctype_exists(doctype: str) -> bool:
    return bool(frappe.db.exists("DocType", doctype))


def _ensure_role(role_name: str):
    if frappe.db.exists("Role", role_name):
        return
    frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)


def _map_website_manager_users():
    users = frappe.get_all(
        "Has Role",
        filters={"role": "Website Manager", "parenttype": "User"},
        fields=["parent"],
        limit_page_length=0,
    )

    for row in users:
        user = str(row.get("parent") or "").strip()
        if not user:
            continue
        for role_name in ROLE_NAMES:
            if frappe.db.exists("Has Role", {"parent": user, "parenttype": "User", "role": role_name}):
                continue
            frappe.get_doc(
                {
                    "doctype": "Has Role",
                    "parent": user,
                    "parenttype": "User",
                    "parentfield": "roles",
                    "role": role_name,
                }
            ).insert(ignore_permissions=True)


def _ensure_workflow_settings():
    if not _doctype_exists("MS Management Workflow Settings"):
        return

    if not frappe.db.exists("MS Management Workflow Settings", "MS Management Workflow Settings"):
        doc = frappe.new_doc("MS Management Workflow Settings")
        doc.enforce_workflow = 0
        doc.shadow_mode = 1
        doc.shadow_until = (date.today() + timedelta(days=7)).isoformat()
        doc.allow_system_manager_bypass = 1
        doc.notify_on_submit_review = 1
        doc.notify_on_approve = 1
        doc.insert(ignore_permissions=True)
        return

    doc = frappe.get_doc("MS Management Workflow Settings", "MS Management Workflow Settings")
    if not doc.get("shadow_until"):
        doc.shadow_until = (date.today() + timedelta(days=7)).isoformat()
    if doc.get("shadow_mode") in (None, ""):
        doc.shadow_mode = 1
    if doc.get("enforce_workflow") in (None, ""):
        doc.enforce_workflow = 0
    if doc.get("allow_system_manager_bypass") in (None, ""):
        doc.allow_system_manager_bypass = 1
    if doc.get("notify_on_submit_review") in (None, ""):
        doc.notify_on_submit_review = 1
    if doc.get("notify_on_approve") in (None, ""):
        doc.notify_on_approve = 1
    doc.save(ignore_permissions=True)


def _ensure_alert_rules():
    if not _doctype_exists("Analytics Alert Rule"):
        return

    for row in DEFAULT_ALERTS:
        metric_key = row["metric_key"]
        if frappe.db.exists("Analytics Alert Rule", {"metric_key": metric_key}):
            continue
        doc = frappe.get_doc({"doctype": "Analytics Alert Rule", **row})
        doc.insert(ignore_permissions=True)


def execute():
    for role_name in ROLE_NAMES:
        _ensure_role(role_name)

    _map_website_manager_users()
    _ensure_workflow_settings()
    _ensure_alert_rules()

    frappe.db.commit()
    frappe.clear_cache()
