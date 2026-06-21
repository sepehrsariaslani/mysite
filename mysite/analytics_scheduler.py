import json

import frappe
from frappe.utils import add_days, nowdate

from mysite import analytics_service


def process_event_async(payload=None):
    payload = payload or {}
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            payload = {}

    try:
        analytics_service.track_event_payload(payload, from_fallback=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Analytics Fallback Event Error")


def _operator_eval(current_value, operator, threshold):
    if operator == "<":
        return current_value < threshold
    if operator == "<=":
        return current_value <= threshold
    if operator == "=":
        return current_value == threshold
    if operator == ">=":
        return current_value >= threshold
    if operator == ">":
        return current_value > threshold
    return False


def _alert_recipients(rule):
    raw = (rule.get("recipients") or "").replace("\n", ",")
    recipients = [item.strip() for item in raw.split(",") if item.strip()]
    if recipients:
        return recipients

    try:
        role_names = ["System Manager", "Mysite Analytics Manager", "Mysite Support Manager"]
        return [
            row.parent
            for row in frappe.get_all(
                "Has Role",
                filters={"role": ["in", role_names], "parenttype": "User"},
                fields=["parent"],
                limit_page_length=0,
            )
            if row.get("parent")
        ]
    except Exception:
        return []


def _metric_evaluation(metric_key, window_days):
    metric_key = str(metric_key or "").strip()
    window_days = max(int(window_days or 7), 1)
    from_date = add_days(nowdate(), -1 * (window_days - 1))
    to_date = nowdate()

    if metric_key == "conversion_rate":
        summary = analytics_service._summary_metrics(from_date, to_date)
        current = float(summary.get("conversion_rate") or 0)
        return {
            "current": current,
            "from_date": from_date,
            "to_date": to_date,
            "message": (
                f"هشدار آنالیتیکس: نرخ تبدیل در {window_days} روز اخیر برابر {current:.2f}% ثبت شده است."
            ),
        }

    if metric_key == "revenue_drop_percent":
        current_summary = analytics_service._summary_metrics(from_date, to_date)
        current_revenue = float(current_summary.get("revenue") or 0)
        prev_to = add_days(from_date, -1)
        prev_from = add_days(prev_to, -1 * (window_days - 1))
        prev_summary = analytics_service._summary_metrics(prev_from, prev_to)
        previous_revenue = float(prev_summary.get("revenue") or 0)
        drop_percent = 0.0
        if previous_revenue > 0:
            drop_percent = max(0.0, ((previous_revenue - current_revenue) / previous_revenue) * 100)
        return {
            "current": drop_percent,
            "from_date": from_date,
            "to_date": to_date,
            "message": (
                f"هشدار آنالیتیکس: افت درآمد در بازه {window_days} روزه اخیر برابر {drop_percent:.2f}% است. "
                f"(درآمد جاری: {current_revenue:.0f}، بازه قبل: {previous_revenue:.0f})"
            ),
        }

    if metric_key == "sla_failed_ratio":
        if not frappe.db.exists("DocType", "MS Support Ticket"):
            return {"current": 0.0, "from_date": from_date, "to_date": to_date, "message": ""}
        filters = {"creation": ["between", [f"{from_date} 00:00:00", f"{to_date} 23:59:59"]]}
        total = float(frappe.db.count("MS Support Ticket", filters=filters) or 0)
        failed = float(
            frappe.db.count("MS Support Ticket", filters={**filters, "agreement_status": "Failed"}) or 0
        )
        failed_ratio = (failed / total) * 100 if total else 0.0
        return {
            "current": failed_ratio,
            "from_date": from_date,
            "to_date": to_date,
            "message": (
                f"هشدار پشتیبانی: نسبت SLA Failed در {window_days} روز اخیر برابر {failed_ratio:.2f}% است "
                f"(Failed: {int(failed)} از {int(total)} تیکت)."
            ),
        }

    return {"current": 0.0, "from_date": from_date, "to_date": to_date, "message": ""}


def evaluate_alert_rules():
    if not frappe.db.exists("DocType", "Analytics Alert Rule"):
        return

    rules = frappe.get_all(
        "Analytics Alert Rule",
        filters={"is_active": 1},
        fields=[
            "name",
            "metric_key",
            "operator",
            "threshold_value",
            "window_days",
            "notify_email",
            "notify_notification_log",
            "recipients",
        ],
        limit_page_length=0,
    )

    for rule in rules:
        metric_key = (rule.get("metric_key") or "").strip()
        if metric_key not in {"conversion_rate", "revenue_drop_percent", "sla_failed_ratio"}:
            continue

        window_days = max(int(rule.get("window_days") or 7), 1)
        metric_payload = _metric_evaluation(metric_key, window_days)
        current = float(metric_payload.get("current") or 0)
        threshold = float(rule.get("threshold_value") or 0)
        operator = (rule.get("operator") or "<").strip()

        if not _operator_eval(current, operator, threshold):
            continue

        message = (
            f"{metric_payload.get('message')}\n"
            f"شرط فعال‌شده: {metric_key} {operator} {threshold:.2f}"
        ).strip()

        dedupe = f"analytics-alert::{rule.get('name')}::{nowdate()}"
        if frappe.cache().get_value(dedupe):
            continue
        frappe.cache().set_value(dedupe, 1, expires_in_sec=60 * 60 * 24)

        if int(rule.get("notify_notification_log") or 0):
            recipients = _alert_recipients(rule)
            for user in recipients:
                try:
                    frappe.get_doc(
                        {
                            "doctype": "Notification Log",
                            "subject": "Analytics Alert",
                            "email_content": message,
                            "for_user": user,
                            "type": "Alert",
                        }
                    ).insert(ignore_permissions=True)
                except Exception:
                    frappe.log_error(frappe.get_traceback(), "Analytics Alert Notification Log Error")

        if int(rule.get("notify_email") or 0):
            recipients = _alert_recipients(rule)
            if recipients:
                try:
                    frappe.sendmail(recipients=recipients, subject="Analytics Alert", message=message)
                except Exception:
                    frappe.log_error(frappe.get_traceback(), "Analytics Alert Email Error")

    frappe.db.commit()


def daily_cleanup(retention_days=730):
    cutoff_date = add_days(nowdate(), -1 * max(int(retention_days), 30))

    targets = [
        ("Analytics Event", "occurred_at"),
        ("Page View", "entered_at"),
        ("Cart Event", "occurred_at"),
        ("Funnel Step", "occurred_at"),
    ]

    for doctype, fieldname in targets:
        if not frappe.db.exists("DocType", doctype):
            continue
        try:
            frappe.db.sql(
                f"DELETE FROM `tab{doctype}` WHERE `{fieldname}` < %s",
                (f"{cutoff_date} 00:00:00",),
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Analytics Cleanup Error - {doctype}")

    frappe.db.commit()
