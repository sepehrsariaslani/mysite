import frappe

from mysite.www.mysite.shop_by_look_service import get_shop_by_look_payload


def get_context(context):
    context.page_name = "shop-by-look"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "Shop by Look | دن‌روم"

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    context.boot = get_shop_by_look_payload(requested_customer=requested_customer, only_homepage=False, limit=400)
    return context
