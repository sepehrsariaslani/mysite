import frappe

no_cache = 1


def get_context(context):
    context.safe_render = 0
    try:
        context.csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        context.csrf_token = ""
    return context
