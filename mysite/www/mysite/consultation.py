import frappe

def get_context(context):
    context.no_cache = 1
    context.safe_render = 0
    return {
        "page_name": "consultation",
        "title": "مشاوره و فروش | دنروم",
        "description": "دریافت مشاوره رایگان برای خرید مبلمان"
    }
