import frappe
from email.utils import parseaddr


def doctype_exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def to_int(value, default=0):
    try:
        return int(float(value or 0))
    except Exception:
        return default


def normalize_status_category(value):
    raw = str(value or "").strip().lower()
    if raw in {"open", "new", "pending", "replied"}:
        return "Open"
    if raw in {"paused", "hold", "on hold"}:
        return "Paused"
    if raw in {"resolved", "done"}:
        return "Resolved"
    if raw in {"closed"}:
        return "Closed"
    return "Open"


def map_user(value, fallback="Administrator"):
    candidate = str(value or "").strip()
    if candidate and frappe.db.exists("User", candidate):
        return candidate

    email = parseaddr(candidate)[1] if candidate else ""
    if email:
        user = frappe.db.get_value("User", {"email": email}, "name")
        if user:
            return user

    if fallback and frappe.db.exists("User", fallback):
        return fallback
    return "Administrator"


def map_customer(hd_customer_name):
    customer = str(hd_customer_name or "").strip()
    if not customer:
        return ""

    if frappe.db.exists("Customer", customer):
        return customer

    if doctype_exists("HD Customer") and frappe.db.exists("HD Customer", customer):
        hd_customer_title = frappe.db.get_value("HD Customer", customer, "customer_name")
        if hd_customer_title:
            by_name = frappe.db.get_value("Customer", {"customer_name": hd_customer_title}, "name")
            if by_name:
                return by_name

    by_name = frappe.db.get_value("Customer", {"customer_name": customer}, "name")
    return by_name or ""


def first_ms_open_status():
    value = frappe.db.get_value(
        "MS Support Ticket Status",
        {"enabled": 1, "category": "Open"},
        "name",
        order_by="modified asc",
    )
    if value:
        return value
    return frappe.db.get_value("MS Support Ticket Status", {"enabled": 1}, "name")


def first_ms_priority():
    return frappe.db.get_value(
        "MS Support Ticket Priority",
        {"enabled": 1},
        "name",
        order_by="weight asc, modified asc",
    )


def first_ms_ticket_type():
    return frappe.db.get_value(
        "MS Support Ticket Type",
        {"enabled": 1},
        "name",
        order_by="modified asc",
    )


def map_existing_name(doctype, value, fallback=""):
    candidate = str(value or "").strip()
    if candidate and frappe.db.exists(doctype, candidate):
        return candidate
    return fallback


def migration_logger():
    return frappe.logger("mysite_support_migration")
