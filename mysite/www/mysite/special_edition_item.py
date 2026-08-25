from urllib.parse import unquote

import frappe

from mysite.www.mysite.special_edition_service import get_special_edition_detail_payload


def get_context(context):
    context.page_name = "special-edition-item"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "Special Edition Detail | دن‌روم"

    raw_name = (frappe.form_dict.get("name") or "").strip()
    if not raw_name:
        path = (frappe.local.request.path or "").strip("/")
        parts = path.split("/")
        if parts:
            raw_name = parts[-1]
    item_code = unquote(raw_name).strip()

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    payload = get_special_edition_detail_payload(item_code=item_code, requested_customer=requested_customer)
    detail = payload.get("SpecialEditionDetail") or {}
    if not detail:
        frappe.throw("Special Edition موردنظر یافت نشد.", frappe.DoesNotExistError)

    context.boot = payload
    context.title = f"{detail.get('title') or 'Special Edition'} | دن‌روم"
    return context
