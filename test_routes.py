from frappe.website.router import get_router_rules
rules = get_router_rules()
for r in rules:
    if 'product' in str(r) or 'sofa' in str(r):
        print(r)
