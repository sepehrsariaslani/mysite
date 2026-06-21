import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate

from mysite import support_service


def execute(filters=None):
    filters = frappe._dict(filters or {})
    from_date = str(getdate(filters.from_date)) if filters.get("from_date") else str(add_days(nowdate(), -29))
    to_date = str(getdate(filters.to_date)) if filters.get("to_date") else str(getdate(nowdate()))

    columns = [
        {"fieldname": "creation_date", "label": _("تاریخ"), "fieldtype": "Date", "width": 180},
        {
            "fieldname": "first_response_time",
            "label": _("زمان اولین پاسخ"),
            "fieldtype": "Duration",
            "width": 240,
        },
    ]

    data = support_service.first_response_daily_rows(from_date=from_date, to_date=to_date)
    return columns, data
