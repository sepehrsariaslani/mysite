import frappe

def get_context(context):
    context.no_cache = 1
    context.safe_render = 0
    return {
        "page_name": "custom-products",
        "title": "محصولات سفارشی | دنروم",
        "description": "سفارش مبلمان اختصاصی با طرح و ابعاد دلخواه"
    }
