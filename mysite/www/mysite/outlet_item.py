from urllib.parse import unquote

import frappe

from mysite.www.mysite.outlet_service import get_outlet_detail_payload


def get_context(context):
    context.page_name = "outlet-item"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "Outlet Detail | دن‌روم"

    raw_name = (frappe.form_dict.get("name") or "").strip()
    if not raw_name:
        path = (frappe.local.request.path or "").strip("/")
        parts = path.split("/")
        if parts:
            raw_name = parts[-1]
    item_code = unquote(raw_name).strip()

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    payload = get_outlet_detail_payload(item_code=item_code, requested_customer=requested_customer)
    detail = payload.get("OutletDetail") or {}
    if not detail:
        frappe.throw("محصول Outlet موردنظر یافت نشد.", frappe.DoesNotExistError)

    context.boot = payload
    context.title = f"{detail.get('title') or 'Outlet'} | دن‌روم"
    return context
