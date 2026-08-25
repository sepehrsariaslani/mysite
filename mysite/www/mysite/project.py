from urllib.parse import unquote

import frappe

from mysite.www.mysite.projects_service import get_project_detail_payload


def get_context(context):
    context.page_name = "project-details"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "جزئیات پروژه | دن‌روم"

    raw_name = (frappe.form_dict.get("name") or "").strip()
    if not raw_name:
        path = (frappe.local.request.path or "").strip("/")
        parts = path.split("/")
        if parts:
            raw_name = parts[-1]
    project_name = unquote(raw_name).strip()

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    payload = get_project_detail_payload(project_name=project_name, requested_customer=requested_customer)

    if not payload.get("ProjectDetails"):
        frappe.throw("پروژه موردنظر یافت نشد.", frappe.DoesNotExistError)

    context.boot = payload
    context.title = f"{payload['ProjectDetails'].get('title') or 'جزئیات پروژه'} | دن‌روم"
    return context
