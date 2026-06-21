import frappe

from mysite.www.faq_service import get_faq_payload


def get_context(context):
    context.page_name = "faq"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "سوالات متداول | دن‌روم"

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    context.boot = get_faq_payload(requested_customer=requested_customer, only_homepage=False, limit=500)
    return context
