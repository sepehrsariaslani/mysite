import json

import frappe
from frappe.utils import add_days, nowdate

from mysite import analytics_service


def _doctype_exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def _safe_json(value):
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _resolve_model_name(item_code, fallback=""):
    item_code = (item_code or "").strip()
    if not item_code:
        return (fallback or "").strip()

    model_name = frappe.db.get_value(
        "Item Variant Attribute",
        {"parent": item_code, "attribute": "مدل محصول"},
        "attribute_value",
    )
    if model_name:
        return model_name

    variant_of = frappe.db.get_value("Item", item_code, "variant_of")
    if variant_of:
        parent_model = frappe.db.get_value(
            "Item Variant Attribute",
            {"parent": variant_of, "attribute": "مدل محصول"},
            "attribute_value",
        )
        if parent_model:
            return parent_model

    return (fallback or item_code).strip()


def _insert_payload(payload):
    try:
        analytics_service.track_event_payload(payload, from_fallback=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Analytics Backfill Payload Error")


def _backfill_from_comment(from_date):
    rows = frappe.get_all(
        "Comment",
        filters={
            "subject": ["like", "WEB_FUNNEL::%"],
            "creation": [">=", f"{from_date} 00:00:00"],
        },
        fields=["name", "subject", "content", "creation"],
        order_by="creation asc",
        limit_page_length=0,
    )

    for row in rows:
        parsed = _safe_json(row.get("content"))
        step = (parsed.get("step") or str(row.get("subject") or "").replace("WEB_FUNNEL::", "", 1)).strip()
        payload = {
            "event_type": step,
            "funnel_step": step,
            "session_id": parsed.get("session_id"),
            "model_name": parsed.get("model_name"),
            "product_id": parsed.get("item_code"),
            "qty": parsed.get("qty") or 1,
            "amount": parsed.get("amount") or 0,
            "customer": parsed.get("customer"),
            "page_url": parsed.get("path"),
            "occurred_at": row.get("creation"),
            "properties": parsed.get("extra") if isinstance(parsed.get("extra"), dict) else {},
            "dedupe_key": f"backfill-comment::{row.get('name')}",
        }
        _insert_payload(payload)


def _backfill_from_sales_invoices(from_date):
    if not (_doctype_exists("Sales Invoice") and _doctype_exists("Sales Invoice Item")):
        return

    rows = frappe.db.sql(
        """
        SELECT
            si.name AS invoice_name,
            si.posting_date,
            si.customer,
            sii.item_code,
            sii.item_name,
            sii.qty,
            sii.amount,
            sii.parenttype,
            sii.idx
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND IFNULL(si.is_return, 0) = 0
          AND si.posting_date >= %(from_date)s
        ORDER BY si.posting_date ASC, si.name ASC, sii.idx ASC
        """,
        {"from_date": from_date},
        as_dict=True,
    )

    for row in rows:
        model_name = _resolve_model_name(row.get("item_code"), row.get("item_name") or row.get("item_code"))
        payload = {
            "event_type": "order_submit",
            "funnel_step": "order_submit",
            "session_id": f"si::{row.get('invoice_name')}",
            "model_name": model_name,
            "product_id": row.get("item_code"),
            "qty": row.get("qty") or 1,
            "amount": row.get("amount") or 0,
            "customer": row.get("customer"),
            "page_url": "/erpnext/sales-invoice",
            "occurred_at": f"{row.get('posting_date')} 12:00:00",
            "properties": {"source": "sales_invoice", "invoice": row.get("invoice_name")},
            "dedupe_key": f"backfill-si::{row.get('invoice_name')}::{row.get('idx')}",
        }
        _insert_payload(payload)


def _backfill_from_sales_orders(from_date):
    if not (_doctype_exists("Sales Order") and _doctype_exists("Sales Order Item")):
        return

    rows = frappe.db.sql(
        """
        SELECT
            so.name AS order_name,
            so.transaction_date,
            so.customer,
            soi.item_code,
            soi.item_name,
            soi.qty,
            soi.amount,
            soi.idx
        FROM `tabSales Order Item` soi
        INNER JOIN `tabSales Order` so ON so.name = soi.parent
        WHERE so.docstatus = 1
          AND so.transaction_date >= %(from_date)s
        ORDER BY so.transaction_date ASC, so.name ASC, soi.idx ASC
        """,
        {"from_date": from_date},
        as_dict=True,
    )

    for row in rows:
        model_name = _resolve_model_name(row.get("item_code"), row.get("item_name") or row.get("item_code"))
        payload = {
            "event_type": "checkout_start",
            "funnel_step": "checkout_start",
            "session_id": f"so::{row.get('order_name')}",
            "model_name": model_name,
            "product_id": row.get("item_code"),
            "qty": row.get("qty") or 1,
            "amount": row.get("amount") or 0,
            "customer": row.get("customer"),
            "page_url": "/erpnext/sales-order",
            "occurred_at": f"{row.get('transaction_date')} 12:00:00",
            "properties": {"source": "sales_order", "sales_order": row.get("order_name")},
            "dedupe_key": f"backfill-so::{row.get('order_name')}::{row.get('idx')}",
        }
        _insert_payload(payload)


def _backfill_from_quotation_requests(from_date):
    if not _doctype_exists("Quotation Request"):
        return

    rows = frappe.get_all(
        "Quotation Request",
        filters={"creation": [">=", f"{from_date} 00:00:00"]},
        fields=["name", "creation", "customer", "status"],
        limit_page_length=0,
    )
    for row in rows:
        payload = {
            "event_type": "checkout_start",
            "funnel_step": "checkout_start",
            "session_id": f"qr::{row.get('name')}",
            "model_name": "Quotation Request",
            "product_id": row.get("name"),
            "qty": 1,
            "amount": 0,
            "customer": row.get("customer"),
            "page_url": "/mysite/cart",
            "occurred_at": row.get("creation"),
            "properties": {"source": "quotation_request", "status": row.get("status")},
            "dedupe_key": f"backfill-qr::{row.get('name')}",
        }
        _insert_payload(payload)


def execute():
    if not _doctype_exists("Analytics Event"):
        return

    from_date = add_days(nowdate(), -365)

    _backfill_from_comment(from_date)
    _backfill_from_sales_orders(from_date)
    _backfill_from_sales_invoices(from_date)
    _backfill_from_quotation_requests(from_date)

    frappe.db.commit()
