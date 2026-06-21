import frappe

from mysite.www.special_edition_service import get_special_edition_payload


def get_context(context):
    context.page_name = "special-edition"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "Special Edition | دن‌روم"

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    context.boot = get_special_edition_payload(requested_customer=requested_customer, limit=12)
    return context
