import json

import frappe

from mysite.analytics_service import DEFAULT_EVENT_TOGGLES, DEFAULT_FUNNEL_STEPS


def _doctype_exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def execute():
    if _doctype_exists("Analytics Event Toggle"):
        for event_key, description in DEFAULT_EVENT_TOGGLES:
            name = frappe.db.get_value("Analytics Event Toggle", {"event_key": event_key}, "name")
            if name:
                continue
            frappe.get_doc(
                {
                    "doctype": "Analytics Event Toggle",
                    "event_key": event_key,
                    "is_active": 1,
                    "description": description,
                }
            ).insert(ignore_permissions=True)

    if _doctype_exists("Analytics Funnel Definition"):
        if not frappe.db.exists("Analytics Funnel Definition", {"title": "Default Conversion Funnel"}):
            frappe.get_doc(
                {
                    "doctype": "Analytics Funnel Definition",
                    "title": "Default Conversion Funnel",
                    "is_active": 1,
                    "is_default": 1,
                    "steps_json": json.dumps(DEFAULT_FUNNEL_STEPS, ensure_ascii=False),
                }
            ).insert(ignore_permissions=True)

    if _doctype_exists("Analytics Alert Rule"):
        defaults = [
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
        for row in defaults:
            if frappe.db.exists("Analytics Alert Rule", {"metric_key": row["metric_key"]}):
                continue
            frappe.get_doc({"doctype": "Analytics Alert Rule", **row}).insert(ignore_permissions=True)

    frappe.db.commit()
