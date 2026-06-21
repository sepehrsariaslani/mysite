import frappe

from mysite.www.projects_service import get_projects_payload


def get_context(context):
    context.page_name = "projects"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "پروژه‌های انجام‌شده | دن‌روم"

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    context.boot = get_projects_payload(
        requested_customer=requested_customer,
        only_homepage=False,
        limit=400,
    )
    return context
