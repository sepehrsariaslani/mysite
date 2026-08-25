import frappe

def get_context(context):
    context.no_cache = 1
    context.safe_render = 0
    return {
        "page_name": "blog",
        "title": "آموزش و بلاگ | دنروم",
        "description": "آخرین مقالات و آموزش‌های دکوراسیون و مبلمان"
    }
