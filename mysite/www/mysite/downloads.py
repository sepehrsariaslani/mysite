import frappe

def get_context(context):
    context.no_cache = 1
    context.safe_render = 0
    return {
        "page_name": "downloads",
        "title": "دانلود ها | دنروم",
        "description": "کاتالوگ‌ها و فایل‌های مورد نیاز محصولات دنروم"
    }
