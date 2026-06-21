import frappe

from mysite.zarinpal_api import verify_payment_status


def get_context(context):
    context.no_cache = 1
    context.safe_render = 0
    context.show_sidebar = False
    context.title = "نتیجه پرداخت زرین‌پال"

    authority = (frappe.form_dict.get("Authority") or frappe.form_dict.get("authority") or "").strip()
    status = (frappe.form_dict.get("Status") or frappe.form_dict.get("status") or "").strip()

    try:
        context.result = verify_payment_status(authority=authority, status=status)
    except Exception:
        context.result = {
            "ok": False,
            "message": "خطا در بررسی وضعیت پرداخت. لطفاً با پشتیبانی تماس بگیرید.",
            "authority": authority,
        }
        frappe.log_error(frappe.get_traceback(), "Zarinpal Callback Error")
    context.authority = authority
    context.gateway_status = status
    return context
