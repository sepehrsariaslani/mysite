import frappe

def get_context(context):
    context.no_cache = 1
    context.safe_render = 0
    return {
        "page_name": "cooperation",
        "title": "همکاری با ما | دنروم",
        "description": "فرصت‌های شغلی و همکاری با برند دنروم"
    }
