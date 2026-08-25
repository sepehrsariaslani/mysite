import frappe

def get_context(context):
    context.no_cache = 1
    context.safe_render = 0
    return {
        "page_name": "dealers",
        "title": "نمایندگی‌ها | دنروم",
        "description": "لیست نمایندگی‌های فعال دنروم در سراسر ایران"
    }
