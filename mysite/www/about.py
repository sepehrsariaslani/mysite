from mysite.www.about_service import get_about_payload


def get_context(context):
    context.page_name = "about"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "درباره ما | دن‌روم"
    context.boot = {
        "AboutPageData": get_about_payload(),
    }
    return context
