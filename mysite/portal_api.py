import json
from urllib.parse import quote

import frappe
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display
from frappe.utils import add_days, add_months, cint, flt, getdate, nowdate

from erpnext.controllers.website_list_for_contact import get_parents_for_user

DEFAULT_ANALYTICS_MONTHS = 12
MAX_PAGE_SIZE = 50


SECTION_CONFIG = {
    "quotation_requests": {
        "doctype": "Quotation Request",
        "customer_field": "customer",
        "date_field": "creation",
        "status_field": "status",
        "order_by": "creation desc",
        "extra_filters": {"docstatus": ["<", 2]},
        "search_fields": ["name", "customer_name", "phone", "email", "status"],
        "list_fields": [
            "name",
            "customer",
            "customer_name",
            "phone",
            "email",
            "request_note",
            "quotation",
            "status",
            "creation",
            "docstatus",
        ],
        "detail_fields": [
            "name",
            "customer",
            "customer_name",
            "phone",
            "email",
            "request_note",
            "quotation",
            "status",
            "creation",
            "modified",
            "docstatus",
        ],
        "item_doctype": "Quotation Request Item",
        "item_fields": ["idx", "item_code", "item_name", "qty", "price", "configuration"],
    },
    "quotations": {
        "doctype": "Quotation",
        "customer_field": "party_name",
        "date_field": "transaction_date",
        "status_field": "status",
        "order_by": "transaction_date desc, modified desc",
        "extra_filters": {"docstatus": ["<", 2], "quotation_to": "Customer"},
        "search_fields": ["name", "party_name", "status"],
        "list_fields": [
            "name",
            "party_name as customer",
            "transaction_date",
            "valid_till",
            "grand_total",
            "currency",
            "status",
            "docstatus",
        ],
        "detail_fields": [
            "name",
            "party_name as customer",
            "transaction_date",
            "valid_till",
            "grand_total",
            "rounded_total",
            "total_taxes_and_charges",
            "currency",
            "status",
            "docstatus",
            "company",
            "owner",
        ],
        "item_doctype": "Quotation Item",
        "item_fields": ["idx", "item_code", "item_name", "description", "qty", "uom", "rate", "amount"],
    },
    "sales_orders": {
        "doctype": "Sales Order",
        "customer_field": "customer",
        "date_field": "transaction_date",
        "status_field": "status",
        "order_by": "transaction_date desc, modified desc",
        "extra_filters": {"docstatus": ["<", 2]},
        "search_fields": ["name", "customer", "status"],
        "list_fields": [
            "name",
            "customer",
            "transaction_date",
            "delivery_date",
            "grand_total",
            "per_delivered",
            "per_billed",
            "currency",
            "status",
            "docstatus",
        ],
        "detail_fields": [
            "name",
            "customer",
            "transaction_date",
            "delivery_date",
            "grand_total",
            "rounded_total",
            "per_delivered",
            "per_billed",
            "currency",
            "status",
            "docstatus",
            "company",
            "owner",
        ],
        "item_doctype": "Sales Order Item",
        "item_fields": ["idx", "item_code", "item_name", "description", "qty", "uom", "rate", "amount"],
    },
    "sales_invoices": {
        "doctype": "Sales Invoice",
        "customer_field": "customer",
        "date_field": "posting_date",
        "status_field": "status",
        "order_by": "posting_date desc, modified desc",
        "extra_filters": {"docstatus": ["<", 2]},
        "search_fields": ["name", "customer", "status"],
        "list_fields": [
            "name",
            "customer",
            "posting_date",
            "due_date",
            "grand_total",
            "outstanding_amount",
            "currency",
            "status",
            "docstatus",
        ],
        "detail_fields": [
            "name",
            "customer",
            "posting_date",
            "due_date",
            "grand_total",
            "rounded_total",
            "total_taxes_and_charges",
            "outstanding_amount",
            "currency",
            "status",
            "docstatus",
            "company",
            "owner",
        ],
        "item_doctype": "Sales Invoice Item",
        "item_fields": ["idx", "item_code", "item_name", "description", "qty", "uom", "rate", "amount"],
    },
    "deliveries": {
        "doctype": "Delivery Note",
        "customer_field": "customer",
        "date_field": "posting_date",
        "status_field": "status",
        "order_by": "posting_date desc, modified desc",
        "extra_filters": {"docstatus": ["<", 2]},
        "search_fields": ["name", "customer", "status"],
        "list_fields": [
            "name",
            "customer",
            "posting_date",
            "grand_total",
            "currency",
            "status",
            "docstatus",
        ],
        "detail_fields": [
            "name",
            "customer",
            "posting_date",
            "grand_total",
            "rounded_total",
            "total_taxes_and_charges",
            "currency",
            "status",
            "docstatus",
            "company",
            "owner",
        ],
        "item_doctype": "Delivery Note Item",
        "item_fields": ["idx", "item_code", "item_name", "description", "qty", "uom", "rate", "amount"],
    },
}


def _require_authenticated_user():
    if frappe.session.user == "Guest":
        frappe.throw(_("برای دسترسی به داشبورد باید وارد حساب خود شوید."), frappe.PermissionError)
    return frappe.session.user


def _support_guard(include_phase2=False):
    from mysite import support_service

    return support_service.ensure_support_runtime_ready(include_phase2=include_phase2, throw=True)


def _get_allowed_customers_for_session_user():
    _require_authenticated_user()
    customers = get_parents_for_user("Customer") or []
    seen = set()
    unique_customers = []
    for customer in customers:
        if customer and customer not in seen:
            seen.add(customer)
            unique_customers.append(customer)
    return unique_customers


def _get_customers_meta(customer_names):
    if not customer_names:
        return []

    rows = frappe.get_all(
        "Customer",
        filters={"name": ["in", customer_names]},
        fields=["name", "customer_name", "email_id", "mobile_no"],
        ignore_permissions=True,
    )
    rows_by_name = {row["name"]: row for row in rows}
    return [rows_by_name[name] for name in customer_names if name in rows_by_name]


def _resolve_customer_scope(customer, allowed_customers):
    allowed_customers = allowed_customers or []
    if customer:
        if customer not in allowed_customers:
            frappe.throw(_("به مشتری انتخاب‌شده دسترسی ندارید."), frappe.PermissionError)
        return [customer]
    return allowed_customers


def _default_date_range(months=DEFAULT_ANALYTICS_MONTHS):
    to_date = getdate(nowdate())
    from_date = add_months(to_date, -months)
    return str(from_date), str(to_date)


def _resolve_date_range(from_date=None, to_date=None, months=DEFAULT_ANALYTICS_MONTHS):
    default_from, default_to = _default_date_range(months)
    resolved_from = getdate(from_date) if from_date else getdate(default_from)
    resolved_to = getdate(to_date) if to_date else getdate(default_to)
    if resolved_from > resolved_to:
        resolved_from, resolved_to = resolved_to, resolved_from
    return str(resolved_from), str(resolved_to)


def _get_customer_contact(customer_name):
    return frappe.db.get_value(
        "Customer",
        customer_name,
        ["customer_name", "email_id", "mobile_no"],
        as_dict=True,
    ) or {}


def _get_user_contact(user):
    return frappe.db.get_value("User", user, ["full_name", "email", "mobile_no"], as_dict=True) or {}


def _safe_contact_for_quotation_request(customer_name, session_user):
    customer_info = _get_customer_contact(customer_name)
    user_info = _get_user_contact(session_user)

    customer_label = (
        customer_info.get("customer_name")
        or frappe.db.get_value("Customer", customer_name, "customer_name")
        or customer_name
    )
    email = customer_info.get("email_id") or user_info.get("email") or ""
    phone = customer_info.get("mobile_no") or user_info.get("mobile_no") or ""
    return {
        "customer_name": customer_label,
        "email": email,
        "phone": phone,
    }


def _normalize_portal_items(items):
    normalized_items = []
    for item in items or []:
        qty = max(flt(item.get("qty") or 1), 1)
        config = item.get("configuration")
        if not config:
            config = item.get("config")
        if isinstance(config, (dict, list)):
            config = json.dumps(config, ensure_ascii=False)

        price = flt(item.get("price"))
        if not price:
            price = flt(item.get("total_price") or item.get("totalPrice"))
        if not price and isinstance(item.get("config"), dict):
            price = flt(item.get("config", {}).get("totalPrice"))

        normalized_items.append(
            {
                "item_name": item.get("item_name") or item.get("name") or item.get("item_code") or _("Item"),
                "item_code": item.get("item_code") or item.get("name"),
                "qty": qty,
                "price": price,
                "configuration": config or "",
            }
        )
    return normalized_items


def _normalize_editable_request_items(items):
    rows = []
    for idx, item in enumerate(items or [], start=1):
        qty = max(flt(item.get("qty") or 1), 1)
        price = flt(item.get("price"))
        if not price:
            price = flt(item.get("rate"))
        if not price:
            price = flt(item.get("amount")) / qty if qty else 0

        config = item.get("configuration") or ""
        if isinstance(config, (dict, list)):
            config = json.dumps(config, ensure_ascii=False)

        rows.append(
            {
                "idx": idx,
                "item_code": item.get("item_code") or "",
                "item_name": item.get("item_name") or item.get("item_code") or _("Item"),
                "qty": qty,
                "price": price,
                "configuration": config,
            }
        )
    return rows


def _get_top_products(customers, from_date, to_date, limit=10):
    if not customers:
        return []

    limit = min(max(cint(limit), 1), 50)
    placeholders = ", ".join(["%s"] * len(customers))
    params = tuple(customers) + (from_date, to_date, limit)
    rows = frappe.db.sql(
        f"""
        SELECT
            COALESCE(sii.item_code, '') AS item_code,
            COALESCE(sii.item_name, sii.item_code, '') AS item_name,
            SUM(IFNULL(sii.qty, 0)) AS total_qty,
            SUM(IFNULL(sii.amount, 0)) AS total_amount,
            COUNT(DISTINCT si.name) AS invoice_count
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si
            ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND IFNULL(si.is_return, 0) = 0
          AND si.customer IN ({placeholders})
          AND si.posting_date BETWEEN %s AND %s
        GROUP BY sii.item_code, sii.item_name
        ORDER BY total_qty DESC, total_amount DESC
        LIMIT %s
        """,
        params,
        as_dict=True,
    )
    return rows


def _insights_kpis(customers, from_date, to_date):
    if not customers:
        return {"products_count": 0, "total_qty": 0, "total_amount": 0}

    placeholders = ", ".join(["%s"] * len(customers))
    base_params = tuple(customers) + (from_date, to_date)
    totals = frappe.db.sql(
        f"""
        SELECT
            SUM(IFNULL(sii.qty, 0)) AS total_qty,
            SUM(IFNULL(sii.amount, 0)) AS total_amount
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si
            ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND IFNULL(si.is_return, 0) = 0
          AND si.customer IN ({placeholders})
          AND si.posting_date BETWEEN %s AND %s
        """,
        base_params,
        as_dict=True,
    )

    grouped = frappe.db.sql(
        f"""
        SELECT COUNT(*) AS products_count
        FROM (
            SELECT 1
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si
                ON si.name = sii.parent
            WHERE si.docstatus = 1
              AND IFNULL(si.is_return, 0) = 0
              AND si.customer IN ({placeholders})
              AND si.posting_date BETWEEN %s AND %s
            GROUP BY sii.item_code, sii.item_name
        ) grouped_items
        """,
        base_params,
        as_dict=True,
    )

    totals_row = (totals or [{}])[0]
    grouped_row = (grouped or [{}])[0]
    return {
        "products_count": cint(grouped_row.get("products_count") or 0),
        "total_qty": flt(totals_row.get("total_qty") or 0),
        "total_amount": flt(totals_row.get("total_amount") or 0),
    }


def _payments_kpis(customers, from_date, to_date):
    if not customers:
        return {"total_received": 0, "payment_count": 0}

    placeholders = ", ".join(["%s"] * len(customers))
    params = tuple(customers) + (from_date, to_date)
    rows = frappe.db.sql(
        f"""
        SELECT
            SUM(
                CASE
                    WHEN payment_type = 'Receive'
                        THEN IFNULL(received_amount, 0)
                    ELSE IFNULL(paid_amount, 0)
                END
            ) AS total_received,
            COUNT(*) AS payment_count
        FROM `tabPayment Entry`
        WHERE docstatus = 1
          AND party_type = 'Customer'
          AND party IN ({placeholders})
          AND posting_date BETWEEN %s AND %s
        """,
        params,
        as_dict=True,
    )
    row = (rows or [{}])[0]
    return {
        "total_received": flt(row.get("total_received") or 0),
        "payment_count": cint(row.get("payment_count") or 0),
    }


def _ledger_kpis(customers, from_date, to_date):
    if not customers:
        return {"total_debit": 0, "total_credit": 0, "net_balance": 0}

    placeholders = ", ".join(["%s"] * len(customers))
    params = tuple(customers) + (from_date, to_date)
    rows = frappe.db.sql(
        f"""
        SELECT
            SUM(IFNULL(debit, 0)) AS total_debit,
            SUM(IFNULL(credit, 0)) AS total_credit
        FROM `tabGL Entry`
        WHERE is_cancelled = 0
          AND party_type = 'Customer'
          AND party IN ({placeholders})
          AND posting_date BETWEEN %s AND %s
        """,
        params,
        as_dict=True,
    )
    row = (rows or [{}])[0]
    total_debit = flt(row.get("total_debit") or 0)
    total_credit = flt(row.get("total_credit") or 0)
    return {
        "total_debit": total_debit,
        "total_credit": total_credit,
        "net_balance": total_debit - total_credit,
    }


def _get_section_config(section):
    config = SECTION_CONFIG.get(section)
    if not config:
        frappe.throw(_("بخش نامعتبر است."), frappe.ValidationError)
    return config


def _build_document_filters(config, customers, status=None, from_date=None, to_date=None):
    filters = {config["customer_field"]: ["in", customers]}
    filters.update(config.get("extra_filters", {}))

    if status:
        status_values = [s.strip() for s in str(status).split(",") if s.strip()]
        if len(status_values) == 1:
            filters[config["status_field"]] = status_values[0]
        elif status_values:
            filters[config["status_field"]] = ["in", status_values]

    if from_date and to_date:
        filters[config["date_field"]] = ["between", [from_date, to_date]]
    elif from_date:
        filters[config["date_field"]] = [">=", from_date]
    elif to_date:
        filters[config["date_field"]] = ["<=", to_date]

    return filters


def _build_or_filters(config, search):
    if not search:
        return None

    search_text = f"%{str(search).strip()}%"
    fields = {"name", config["customer_field"], config["status_field"], *config.get("search_fields", [])}

    return [[config["doctype"], fieldname, "like", search_text] for fieldname in fields]


def _get_document_header(section, name, customers):
    config = _get_section_config(section)
    filters = {config["customer_field"]: ["in", customers], "name": name}
    filters.update(config.get("extra_filters", {}))

    rows = frappe.get_all(
        config["doctype"],
        filters=filters,
        fields=config["detail_fields"],
        limit_page_length=1,
        ignore_permissions=True,
    )
    return rows[0] if rows else None


def _normalize_document_items(section, rows):
    if section != "quotation_requests":
        return rows

    normalized_rows = []
    for row in rows:
        price = flt(row.get("price"))
        qty = flt(row.get("qty"))
        normalized_rows.append(
            {
                **row,
                "rate": price,
                "amount": price * qty,
            }
        )
    return normalized_rows


def _to_bool(value):
    return str(value).lower() in {"1", "true", "yes", "on"}


def _get_address_customer_links(address_name):
    links = frappe.get_all(
        "Dynamic Link",
        filters={
            "parent": address_name,
            "parenttype": "Address",
            "link_doctype": "Customer",
        },
        fields=["link_name"],
        ignore_permissions=True,
    )
    return [link["link_name"] for link in links]


def _clear_address_flag_for_customer(customer_name, fieldname, keep_address):
    if fieldname not in {"is_primary_address", "is_shipping_address"}:
        return

    frappe.db.sql(
        f"""
        UPDATE `tabAddress` a
        INNER JOIN `tabDynamic Link` dl
            ON dl.parent = a.name
            AND dl.parenttype = 'Address'
            AND dl.link_doctype = 'Customer'
        SET a.`{fieldname}` = 0
        WHERE dl.link_name = %s
          AND a.name != %s
        """,
        (customer_name, keep_address),
    )


def _fetch_addresses(customers):
    if not customers:
        return []

    addresses = frappe.get_all(
        "Address",
        filters=[
            ["Dynamic Link", "link_doctype", "=", "Customer"],
            ["Dynamic Link", "link_name", "in", customers],
            ["Dynamic Link", "parenttype", "=", "Address"],
            ["disabled", "=", 0],
        ],
        fields=[
            "name",
            "address_title",
            "address_type",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "country",
            "pincode",
            "phone",
            "email_id",
            "is_primary_address",
            "is_shipping_address",
            "modified",
        ],
        order_by="is_primary_address desc, modified desc",
        ignore_permissions=True,
    )

    unique_addresses = {}
    for address in addresses:
        unique_addresses[address["name"]] = address

    normalized = []
    for address in unique_addresses.values():
        address["display"] = get_address_display(address)
        address["customers"] = _get_address_customer_links(address["name"])
        normalized.append(address)

    return normalized


def _get_quotation_request_doc(name, customers):
    doc = frappe.get_doc("Quotation Request", name)
    if doc.docstatus >= 2:
        frappe.throw(_("این درخواست دیگر قابل ویرایش نیست."), frappe.ValidationError)
    if doc.customer not in (customers or []):
        frappe.throw(_("به این درخواست دسترسی ندارید."), frappe.PermissionError)
    return doc


@frappe.whitelist(allow_guest=True)
def portal_session(customer=None):
    csrf_token = ""
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""

    if frappe.session.user == "Guest":
        return {
            "authenticated": False,
            "user": "Guest",
            "full_name": _("Guest"),
            "customers": [],
            "default_customer": None,
            "selected_customer": None,
            "can_switch_customer": False,
            "scope_mode": "customer_portal",
            "csrf_token": csrf_token,
        }

    user = frappe.session.user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    allowed_customers = _get_allowed_customers_for_session_user()
    customer_meta = _get_customers_meta(allowed_customers)
    default_customer = customer_meta[0]["name"] if customer_meta else None
    selected_customer = default_customer
    if customer and customer in allowed_customers:
        selected_customer = customer

    return {
        "authenticated": True,
        "user": user,
        "full_name": full_name,
        "customers": customer_meta,
        "default_customer": default_customer,
        "selected_customer": selected_customer,
        "can_switch_customer": len(customer_meta) > 1,
        "scope_mode": "customer_portal",
        "csrf_token": csrf_token,
    }


@frappe.whitelist()
def portal_dashboard_summary(customer=None, from_date=None, to_date=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)
    resolved_from_date, resolved_to_date = _resolve_date_range(from_date, to_date)

    if not scoped_customers:
        return {
            "counts": {
                "quotation_requests": 0,
                "quotations": 0,
                "sales_orders": 0,
                "sales_invoices": 0,
                "deliveries": 0,
            },
            "total_invoiced": 0,
            "total_outstanding": 0,
            "unpaid_count": 0,
            "overdue_count": 0,
            "open_invoices": [],
            "recent_activity": [],
            "insights_preview": [],
            "payments_summary": {"total_received": 0, "payment_count": 0},
            "ledger_summary": {"total_debit": 0, "total_credit": 0, "net_balance": 0},
            "range": {"from_date": resolved_from_date, "to_date": resolved_to_date},
        }

    def section_count(section):
        config = _get_section_config(section)
        filters = {config["customer_field"]: ["in", scoped_customers]}
        filters.update(config.get("extra_filters", {}))
        return frappe.db.count(config["doctype"], filters=filters)

    counts = {
        "quotation_requests": section_count("quotation_requests"),
        "quotations": section_count("quotations"),
        "sales_orders": section_count("sales_orders"),
        "sales_invoices": section_count("sales_invoices"),
        "deliveries": section_count("deliveries"),
    }

    invoice_rows = frappe.get_all(
        "Sales Invoice",
        filters={
            "customer": ["in", scoped_customers],
            "docstatus": ["<", 2],
        },
        fields=["name", "customer", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"],
        ignore_permissions=True,
    )

    total_invoiced = sum(flt(row.get("grand_total")) for row in invoice_rows)
    total_outstanding = sum(flt(row.get("outstanding_amount")) for row in invoice_rows)
    unpaid_count = sum(1 for row in invoice_rows if flt(row.get("outstanding_amount")) > 0)
    overdue_count = sum(1 for row in invoice_rows if str(row.get("status") or "").lower() == "overdue")

    open_invoices = sorted(
        [row for row in invoice_rows if flt(row.get("outstanding_amount")) > 0],
        key=lambda d: (str(d.get("posting_date") or ""), str(d.get("name") or "")),
        reverse=True,
    )[:10]

    recent_activity = []
    for section in SECTION_CONFIG:
        config = _get_section_config(section)
        section_rows = frappe.get_all(
            config["doctype"],
            filters={**{config["customer_field"]: ["in", scoped_customers]}, **config.get("extra_filters", {})},
            fields=["name", config["date_field"], config["status_field"]],
            order_by=config["order_by"],
            limit_page_length=3,
            ignore_permissions=True,
        )
        for row in section_rows:
            recent_activity.append(
                {
                    "section": section,
                    "name": row.get("name"),
                    "date": row.get(config["date_field"]),
                    "status": row.get(config["status_field"]),
                }
            )

    recent_activity = sorted(
        recent_activity,
        key=lambda d: (str(d.get("date") or ""), str(d.get("name") or "")),
        reverse=True,
    )[:12]

    insights_preview = _get_top_products(scoped_customers, resolved_from_date, resolved_to_date, limit=3)
    payments_summary = _payments_kpis(scoped_customers, resolved_from_date, resolved_to_date)
    ledger_summary = _ledger_kpis(scoped_customers, resolved_from_date, resolved_to_date)

    return {
        "counts": counts,
        "total_invoiced": total_invoiced,
        "total_outstanding": total_outstanding,
        "unpaid_count": unpaid_count,
        "overdue_count": overdue_count,
        "open_invoices": open_invoices,
        "recent_activity": recent_activity,
        "insights_preview": insights_preview,
        "payments_summary": payments_summary,
        "ledger_summary": ledger_summary,
        "range": {"from_date": resolved_from_date, "to_date": resolved_to_date},
    }


@frappe.whitelist()
def portal_submit_quotation_request(customer=None, items=None, note=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)
    if not scoped_customers:
        frappe.throw(_("برای این کاربر مشتری مجاز تعریف نشده است."), frappe.PermissionError)

    if isinstance(items, str):
        items = json.loads(items)

    normalized_items = _normalize_portal_items(items)
    if not normalized_items:
        frappe.throw(_("سبد خرید خالی است."), frappe.ValidationError)

    customer_name = scoped_customers[0]
    contact = _safe_contact_for_quotation_request(customer_name, frappe.session.user)

    doc = frappe.get_doc(
        {
            "doctype": "Quotation Request",
            "customer": customer_name,
            "customer_name": contact.get("customer_name") or customer_name,
            "phone": contact.get("phone"),
            "email": contact.get("email"),
            "request_note": note or "",
            "status": "Submitted",
            "items": [],
        }
    )

    for item in normalized_items:
        doc.append(
            "items",
            {
                "item_code": item.get("item_code"),
                "item_name": item.get("item_name"),
                "qty": item.get("qty"),
                "price": item.get("price"),
                "configuration": item.get("configuration"),
            },
        )

    doc.insert(ignore_permissions=True)

    try:
        from mysite.www.product import (
            FUNNEL_STEP_ORDER_SUBMIT,
            _log_funnel_event_safely,
            _resolve_model_name_for_item,
        )

        total_qty = 0
        total_amount = 0
        model_names = []
        for item in normalized_items:
            code = (item.get("item_code") or "").strip()
            name = item.get("item_name") or code
            model_name = _resolve_model_name_for_item(item_code=code, fallback_name=name)
            if model_name and model_name not in model_names:
                model_names.append(model_name)
            total_qty += cint(item.get("qty") or 0)
            total_amount += flt(item.get("price") or 0)

        _log_funnel_event_safely(
            step=FUNNEL_STEP_ORDER_SUBMIT,
            model_name=model_names[0] if model_names else "",
            qty=total_qty or len(normalized_items),
            amount=total_amount,
            customer=customer_name,
            quotation_name=doc.name,
            extra={
                "models": model_names,
                "items_count": len(normalized_items),
                "source": "portal",
            },
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Portal Funnel Tracking Error")

    frappe.db.commit()
    return {
        "status": "success",
        "name": doc.name,
        "customer": customer_name,
        "customer_name": contact.get("customer_name") or customer_name,
    }


@frappe.whitelist()
def portal_quotation_request_editor(name, customer=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers) if customer else allowed_customers
    if not scoped_customers:
        frappe.throw(_("برای این کاربر مشتری مجاز تعریف نشده است."), frappe.PermissionError)

    doc = _get_quotation_request_doc(name, scoped_customers)
    items = []
    for row in doc.items:
        items.append(
            {
                "idx": row.idx,
                "item_code": row.item_code,
                "item_name": row.item_name,
                "qty": flt(row.qty or 0),
                "price": flt(row.price or 0),
                "configuration": row.configuration or "",
            }
        )

    return {
        "name": doc.name,
        "customer": doc.customer,
        "customer_name": doc.customer_name,
        "phone": doc.phone,
        "email": doc.email,
        "status": doc.status,
        "request_note": doc.get("request_note") or "",
        "quotation": doc.get("quotation"),
        "docstatus": doc.docstatus,
        "creation": doc.creation,
        "modified": doc.modified,
        "items": items,
    }


@frappe.whitelist()
def portal_save_quotation_request(name, customer=None, payload=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers) if customer else allowed_customers
    if not scoped_customers:
        frappe.throw(_("برای این کاربر مشتری مجاز تعریف نشده است."), frappe.PermissionError)

    if isinstance(payload, str):
        payload = json.loads(payload)
    payload = payload or {}

    doc = _get_quotation_request_doc(name, scoped_customers)
    if doc.docstatus != 0:
        frappe.throw(_("فقط درخواست‌های Draft قابل ویرایش هستند."), frappe.ValidationError)

    incoming_customer = payload.get("customer")
    if incoming_customer and incoming_customer != doc.customer:
        if incoming_customer not in allowed_customers:
            frappe.throw(_("به مشتری انتخاب‌شده دسترسی ندارید."), frappe.PermissionError)
        doc.customer = incoming_customer

    if payload.get("customer_name") is not None:
        doc.customer_name = (payload.get("customer_name") or "").strip()
    if payload.get("phone") is not None:
        doc.phone = (payload.get("phone") or "").strip()
    if payload.get("email") is not None:
        doc.email = (payload.get("email") or "").strip()
    if payload.get("status"):
        doc.status = payload.get("status")
    if payload.get("request_note") is not None:
        doc.request_note = payload.get("request_note") or ""

    if "items" in payload:
        rows = _normalize_editable_request_items(payload.get("items"))
        if not rows:
            frappe.throw(_("حداقل یک آیتم برای درخواست لازم است."), frappe.ValidationError)
        doc.set("items", [])
        for row in rows:
            doc.append("items", row)

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "name": doc.name}


@frappe.whitelist()
def portal_make_quotation_from_request(name, customer=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers) if customer else allowed_customers
    if not scoped_customers:
        frappe.throw(_("برای این کاربر مشتری مجاز تعریف نشده است."), frappe.PermissionError)

    request_doc = _get_quotation_request_doc(name, scoped_customers)
    if request_doc.get("quotation") and frappe.db.exists("Quotation", request_doc.quotation):
        return {"status": "success", "quotation": request_doc.quotation, "request": request_doc.name}

    quotation_doc = frappe.new_doc("Quotation")
    quotation_doc.quotation_to = "Customer"
    quotation_doc.party_name = request_doc.customer
    quotation_doc.transaction_date = nowdate()
    quotation_doc.valid_till = add_days(nowdate(), 14)
    quotation_doc.order_type = "Sales"

    company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
        "Global Defaults", "default_company"
    )
    if not company:
        company = frappe.db.get_value("Company", {"is_group": 0}, "name")
    if company:
        quotation_doc.company = company

    selling_price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
    if selling_price_list:
        quotation_doc.selling_price_list = selling_price_list

    if quotation_doc.company and not quotation_doc.currency:
        company_currency = frappe.db.get_value("Company", quotation_doc.company, "default_currency")
        if company_currency and frappe.db.exists("Currency", company_currency):
            quotation_doc.currency = company_currency

    if not request_doc.items:
        frappe.throw(_("این درخواست آیتمی برای تبدیل به پیش‌فاکتور ندارد."), frappe.ValidationError)

    for row in request_doc.items:
        item_code = (row.item_code or "").strip()
        if not item_code or not frappe.db.exists("Item", item_code):
            frappe.throw(
                _("کد کالا برای تبدیل به پیش‌فاکتور معتبر نیست: {0}").format(row.item_name or row.item_code or "-"),
                frappe.ValidationError,
            )

        description = row.item_name or item_code
        if row.configuration:
            description = f"{description}\n{row.configuration}"

        quotation_doc.append(
            "items",
            {
                "item_code": item_code,
                "item_name": row.item_name or item_code,
                "description": description,
                "qty": flt(row.qty or 1),
                "rate": flt(row.price or 0),
            },
        )

    quotation_doc.insert(ignore_permissions=True)
    request_doc.db_set("quotation", quotation_doc.name)
    request_doc.db_set("status", "Quoted")
    frappe.db.commit()
    return {"status": "success", "quotation": quotation_doc.name, "request": request_doc.name}


@frappe.whitelist()
def portal_customer_insights(customer=None, from_date=None, to_date=None, limit=10):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)
    resolved_from_date, resolved_to_date = _resolve_date_range(from_date, to_date)

    if not scoped_customers:
        return {
            "top_products": [],
            "kpis": {"products_count": 0, "total_qty": 0, "total_amount": 0},
            "range": {"from_date": resolved_from_date, "to_date": resolved_to_date},
        }

    top_products = _get_top_products(scoped_customers, resolved_from_date, resolved_to_date, limit=limit)
    kpis = _insights_kpis(scoped_customers, resolved_from_date, resolved_to_date)
    return {
        "top_products": top_products,
        "kpis": kpis,
        "range": {"from_date": resolved_from_date, "to_date": resolved_to_date},
    }


def _match_financial_search(row, search_text, fields):
    if not search_text:
        return True
    lowered = str(search_text).strip().lower()
    if not lowered:
        return True
    haystack = " ".join(str(row.get(field) or "") for field in fields).lower()
    return lowered in haystack


@frappe.whitelist()
def portal_financial_entries(
    entry_type,
    customer=None,
    from_date=None,
    to_date=None,
    search=None,
    page=1,
    page_size=10,
):
    if entry_type not in {"payments", "ledger"}:
        frappe.throw(_("نوع گزارش مالی نامعتبر است."), frappe.ValidationError)

    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)
    resolved_from_date, resolved_to_date = _resolve_date_range(from_date, to_date)

    page = max(cint(page), 1)
    page_size = min(max(cint(page_size), 1), MAX_PAGE_SIZE)
    start = (page - 1) * page_size

    if not scoped_customers:
        zero_kpis = (
            {"total_received": 0, "payment_count": 0}
            if entry_type == "payments"
            else {"total_debit": 0, "total_credit": 0, "net_balance": 0}
        )
        return {
            "entry_type": entry_type,
            "items": [],
            "kpis": zero_kpis,
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_pages": 1,
            "has_next": False,
            "has_prev": page > 1,
            "range": {"from_date": resolved_from_date, "to_date": resolved_to_date},
        }

    if entry_type == "payments":
        filters = {
            "docstatus": 1,
            "party_type": "Customer",
            "party": ["in", scoped_customers],
            "posting_date": ["between", [resolved_from_date, resolved_to_date]],
        }
        or_filters = None
        if search:
            search_text = f"%{str(search).strip()}%"
            or_filters = [
                ["Payment Entry", "name", "like", search_text],
                ["Payment Entry", "party_name", "like", search_text],
                ["Payment Entry", "mode_of_payment", "like", search_text],
                ["Payment Entry", "reference_no", "like", search_text],
                ["Payment Entry", "remarks", "like", search_text],
            ]

        total = len(
            frappe.get_all(
                "Payment Entry",
                filters=filters,
                or_filters=or_filters,
                fields=["name"],
                ignore_permissions=True,
            )
        )
        items = frappe.get_all(
            "Payment Entry",
            filters=filters,
            or_filters=or_filters,
            fields=[
                "name",
                "posting_date",
                "party as customer",
                "party_name",
                "payment_type",
                "mode_of_payment",
                "paid_amount",
                "received_amount",
                "reference_no",
                "reference_date",
                "status",
                "remarks",
            ],
            order_by="posting_date desc, modified desc",
            start=start,
            page_length=page_size,
            ignore_permissions=True,
        )
        kpis = _payments_kpis(scoped_customers, resolved_from_date, resolved_to_date)
    else:
        filters = {
            "is_cancelled": 0,
            "party_type": "Customer",
            "party": ["in", scoped_customers],
            "posting_date": ["between", [resolved_from_date, resolved_to_date]],
        }
        all_rows = frappe.get_all(
            "GL Entry",
            filters=filters,
            fields=[
                "name",
                "posting_date",
                "account",
                "voucher_type",
                "voucher_no",
                "against_voucher_type",
                "against_voucher",
                "debit",
                "credit",
                "remarks",
                "party as customer",
                "company",
                "creation",
            ],
            order_by="posting_date asc, creation asc, name asc",
            ignore_permissions=True,
        )
        all_rows = [
            row
            for row in all_rows
            if _match_financial_search(
                row,
                search,
                ["name", "voucher_no", "account", "remarks", "against_voucher"],
            )
        ]

        running_balance = 0
        for row in all_rows:
            running_balance += flt(row.get("debit")) - flt(row.get("credit"))
            row["running_balance"] = running_balance

        total = len(all_rows)
        items = all_rows[start : start + page_size]
        kpis = _ledger_kpis(scoped_customers, resolved_from_date, resolved_to_date)

    total_pages = max(int((total + page_size - 1) / page_size), 1) if page_size else 1
    return {
        "entry_type": entry_type,
        "items": items,
        "kpis": kpis,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "range": {"from_date": resolved_from_date, "to_date": resolved_to_date},
    }


@frappe.whitelist()
def portal_documents(section, customer=None, page=1, page_size=10, status=None, from_date=None, to_date=None, search=None):
    config = _get_section_config(section)
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)

    page = max(cint(page), 1)
    page_size = min(max(cint(page_size), 1), MAX_PAGE_SIZE)
    start = (page - 1) * page_size

    if not scoped_customers:
        return {
            "section": section,
            "items": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_pages": 1,
            "has_next": False,
            "has_prev": page > 1,
        }

    filters = _build_document_filters(config, scoped_customers, status=status, from_date=from_date, to_date=to_date)
    or_filters = _build_or_filters(config, search)

    total = len(
        frappe.get_all(
            config["doctype"],
            filters=filters,
            or_filters=or_filters,
            fields=["name"],
            ignore_permissions=True,
        )
    )

    items = frappe.get_all(
        config["doctype"],
        filters=filters,
        or_filters=or_filters,
        fields=config["list_fields"],
        order_by=config["order_by"],
        start=start,
        page_length=page_size,
        ignore_permissions=True,
    )

    total_pages = max(int((total + page_size - 1) / page_size), 1) if page_size else 1

    return {
        "section": section,
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@frappe.whitelist()
def portal_document_detail(section, name, customer=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)

    document = _get_document_header(section, name, scoped_customers)
    if not document:
        frappe.throw(_("سند مورد نظر پیدا نشد یا دسترسی ندارید."), frappe.PermissionError)

    config = _get_section_config(section)
    item_rows = frappe.get_all(
        config["item_doctype"],
        filters={"parent": name, "parenttype": config["doctype"], "parentfield": "items"},
        fields=config["item_fields"],
        order_by="idx asc",
        ignore_permissions=True,
    )

    return {
        "section": section,
        "document": document,
        "items": _normalize_document_items(section, item_rows),
    }


@frappe.whitelist()
def portal_document_pdf_url(section, name, customer=None, format=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)

    document = _get_document_header(section, name, scoped_customers)
    if not document:
        frappe.throw(_("سند مورد نظر پیدا نشد یا دسترسی ندارید."), frappe.PermissionError)

    url = f"/api/method/mysite.portal_api.portal_download_pdf?section={quote(section)}&name={quote(name)}"
    if format:
        url += f"&format={quote(format)}"
    return {"url": url}


@frappe.whitelist()
def portal_download_pdf(section, name, format=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    document = _get_document_header(section, name, allowed_customers)
    if not document:
        frappe.throw(_("سند مورد نظر پیدا نشد یا دسترسی ندارید."), frappe.PermissionError)

    config = _get_section_config(section)
    from frappe.utils.print_format import download_pdf

    return download_pdf(config["doctype"], name, format)


@frappe.whitelist()
def portal_addresses(customer=None):
    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)
    return {"items": _fetch_addresses(scoped_customers)}


@frappe.whitelist()
def portal_save_address(customer=None, payload=None):
    allowed_customers = _get_allowed_customers_for_session_user()

    if isinstance(payload, str):
        payload = json.loads(payload)
    payload = payload or {}

    customer_name = customer or payload.get("customer")
    if not customer_name:
        frappe.throw(_("مشتری انتخاب نشده است."), frappe.ValidationError)

    scoped_customers = _resolve_customer_scope(customer_name, allowed_customers)
    if not scoped_customers:
        frappe.throw(_("برای این کاربر مشتری مجاز تعریف نشده است."), frappe.PermissionError)
    customer_name = scoped_customers[0]

    address_name = payload.get("name")
    address_type = payload.get("address_type") or "Shipping"
    is_primary_address = _to_bool(payload.get("is_primary_address"))
    is_shipping_address = _to_bool(payload.get("is_shipping_address"))

    address_fields = {
        "address_title": payload.get("address_title"),
        "address_type": address_type,
        "address_line1": payload.get("address_line1"),
        "address_line2": payload.get("address_line2"),
        "city": payload.get("city"),
        "state": payload.get("state"),
        "country": payload.get("country"),
        "pincode": payload.get("pincode"),
        "phone": payload.get("phone"),
        "email_id": payload.get("email_id"),
        "is_primary_address": 1 if is_primary_address else 0,
        "is_shipping_address": 1 if is_shipping_address else 0,
        "disabled": 0,
    }

    if address_name:
        linked_customers = _get_address_customer_links(address_name)
        if not set(linked_customers) & set(allowed_customers):
            frappe.throw(_("به این آدرس دسترسی ندارید."), frappe.PermissionError)

        address_doc = frappe.get_doc("Address", address_name)
        for fieldname, value in address_fields.items():
            address_doc.set(fieldname, value)

        if customer_name not in linked_customers:
            address_doc.append(
                "links",
                {
                    "link_doctype": "Customer",
                    "link_name": customer_name,
                },
            )
        address_doc.save(ignore_permissions=True)
    else:
        address_doc = frappe.get_doc(
            {
                "doctype": "Address",
                **address_fields,
                "links": [{"link_doctype": "Customer", "link_name": customer_name}],
            }
        )
        address_doc.insert(ignore_permissions=True)

    if is_primary_address:
        _clear_address_flag_for_customer(customer_name, "is_primary_address", address_doc.name)
        frappe.db.set_value("Address", address_doc.name, "is_primary_address", 1, update_modified=False)

    if is_shipping_address:
        _clear_address_flag_for_customer(customer_name, "is_shipping_address", address_doc.name)
        frappe.db.set_value("Address", address_doc.name, "is_shipping_address", 1, update_modified=False)

    frappe.db.commit()
    return {"success": True, "address_name": address_doc.name}


@frappe.whitelist()
def portal_delete_address(address_name):
    allowed_customers = _get_allowed_customers_for_session_user()
    linked_customers = _get_address_customer_links(address_name)
    if not set(linked_customers) & set(allowed_customers):
        frappe.throw(_("به این آدرس دسترسی ندارید."), frappe.PermissionError)

    frappe.delete_doc("Address", address_name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def portal_create_support_ticket(customer=None, payload=None, subject=None, description=None, item_code=None, source_page=None):
    from mysite import support_service

    _support_guard()

    if isinstance(payload, str):
        payload = json.loads(payload)
    payload = payload or {}

    customer_name = customer or payload.get("customer")
    ticket_subject = payload.get("subject", subject)
    ticket_description = payload.get("description", description)
    related_item = payload.get("item_code", item_code)
    source_route = payload.get("source_page", source_page)

    return support_service.create_portal_ticket(
        subject=ticket_subject,
        description=ticket_description,
        customer=customer_name,
        item_code=related_item,
        source_page=source_route,
    )


@frappe.whitelist()
def portal_list_support_tickets(customer=None, page=1, page_size=10, status=None):
    from mysite import support_service

    _support_guard()

    return support_service.list_tickets_for_customer(
        customer=customer,
        page=page,
        page_size=page_size,
        status=status,
    )


@frappe.whitelist()
def portal_get_support_ticket(name=None):
    from mysite import support_service

    _support_guard()

    ticket_name = str(name or "").strip()
    if not ticket_name:
        frappe.throw(_("نام تیکت الزامی است."), frappe.ValidationError)
    return support_service.get_ticket_detail(ticket_name, for_management=False)


@frappe.whitelist()
def portal_reply_support_ticket(name=None, message=None, payload=None):
    from mysite import support_service

    _support_guard()

    if isinstance(payload, str):
        payload = json.loads(payload)
    payload = payload or {}

    ticket_name = str(name or payload.get("name") or "").strip()
    reply_message = payload.get("message", message)

    if not ticket_name:
        frappe.throw(_("نام تیکت الزامی است."), frappe.ValidationError)

    return support_service.add_customer_reply(ticket_name, reply_message)


@frappe.whitelist()
def portal_open_support_chat(customer=None, ticket_name=None, subject=None, initial_message=None, source_page=None, payload=None):
    from mysite import support_service

    _support_guard(include_phase2=True)

    if isinstance(payload, str):
        payload = json.loads(payload)
    payload = payload or {}

    return support_service.open_portal_support_chat(
        customer=customer or payload.get("customer"),
        ticket_name=str(ticket_name or payload.get("ticket_name") or payload.get("ticket") or "").strip() or None,
        subject=payload.get("subject", subject),
        initial_message=payload.get("initial_message", initial_message),
        source_page=payload.get("source_page", source_page),
    )


@frappe.whitelist()
def portal_send_support_chat_message(channel_id=None, ticket_name=None, message=None, payload=None):
    from mysite import support_service

    _support_guard(include_phase2=True)

    if isinstance(payload, str):
        payload = json.loads(payload)
    payload = payload or {}

    return support_service.portal_send_support_chat_message(
        channel_id=str(channel_id or payload.get("channel_id") or "").strip() or None,
        ticket_name=str(ticket_name or payload.get("ticket_name") or payload.get("ticket") or "").strip() or None,
        message=payload.get("message", message),
    )


@frappe.whitelist()
def portal_list_support_chats(page=1, page_size=20):
    from mysite import support_service

    _support_guard(include_phase2=True)

    return support_service.portal_list_support_chats(page=page, page_size=page_size)
