import frappe


def get_context(context):
    context.page_name = "cart"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "سبد خرید | دن‌روم"
    context.safe_render = 0

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""
    context.boot = {
        "SelectedCustomer": requested_customer,
        "csrf_token": csrf_token,
    }
    return context
