import frappe
from frappe import _, scrub
from frappe.utils import add_days, getdate, nowdate

from mysite import support_service


def execute(filters=None):
    filters = frappe._dict(filters or {})
    from_date = str(getdate(filters.from_date)) if filters.get("from_date") else str(add_days(nowdate(), -89))
    to_date = str(getdate(filters.to_date)) if filters.get("to_date") else str(getdate(nowdate()))
    based_on = str(filters.get("based_on") or "status").strip() or "status"
    range_key = str(filters.get("range") or "Monthly").strip() or "Monthly"

    series_payload = support_service.analytics_timeseries_rows(
        from_date=from_date,
        to_date=to_date,
        based_on=based_on,
        range_key=range_key,
    )

    columns = [{"label": _("گروه"), "fieldname": "group", "fieldtype": "Data", "width": 220}]
    for label in series_payload.get("labels") or []:
        columns.append(
            {
                "label": label,
                "fieldname": scrub(label),
                "fieldtype": "Int",
                "width": 120,
            }
        )
    columns.append({"label": _("جمع"), "fieldname": "total", "fieldtype": "Int", "width": 120})

    rows = []
    chart_datasets = []
    for entity_row in series_payload.get("series") or []:
        row = {"group": entity_row.get("entity")}
        total = 0
        values = []
        for item in entity_row.get("data") or []:
            key = scrub(item.get("period"))
            count = int(item.get("count") or 0)
            row[key] = count
            total += count
            values.append(count)
        row["total"] = total
        rows.append(row)
        chart_datasets.append({"name": entity_row.get("entity"), "values": values})

    chart = {
        "data": {
            "labels": series_payload.get("labels") or [],
            "datasets": chart_datasets,
        },
        "type": "line",
    }

    return columns, rows, None, chart
