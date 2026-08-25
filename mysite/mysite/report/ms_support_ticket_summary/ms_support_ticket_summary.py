import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate

from mysite import support_service


def execute(filters=None):
    filters = frappe._dict(filters or {})
    from_date = str(getdate(filters.from_date)) if filters.get("from_date") else str(add_days(nowdate(), -29))
    to_date = str(getdate(filters.to_date)) if filters.get("to_date") else str(getdate(nowdate()))
    based_on = str(filters.get("based_on") or "status").strip() or "status"

    columns = [
        {"label": _("گروه"), "fieldname": "group", "fieldtype": "Data", "width": 220},
        {"label": _("تعداد کل تیکت"), "fieldname": "total_tickets", "fieldtype": "Int", "width": 120},
        {"label": _("نقض SLA"), "fieldname": "sla_failed", "fieldtype": "Int", "width": 110},
        {"label": _("تحقق SLA"), "fieldname": "sla_fulfilled", "fieldtype": "Int", "width": 120},
        {"label": _("میانگین زمان اولین پاسخ"), "fieldname": "avg_first_response_time", "fieldtype": "Duration", "width": 180},
        {"label": _("میانگین زمان پاسخ"), "fieldname": "avg_response_time", "fieldtype": "Duration", "width": 160},
    ]

    data = support_service.ticket_summary_rows(from_date=from_date, to_date=to_date, based_on=based_on)
    return columns, data
