import frappe

from mysite.www.outlet_service import get_outlet_payload


def get_context(context):
    context.page_name = "outlet"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "Outlet | دن‌روم"

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    context.boot = get_outlet_payload(requested_customer=requested_customer, limit=12)
    return context
