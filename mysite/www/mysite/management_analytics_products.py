from mysite.www.mysite.management_context import apply_management_context

no_cache = 1


def get_context(context):
    return apply_management_context(context, required_capability="analytics.view")
