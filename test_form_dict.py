import frappe

# Simulate what frappe.form_dict contains for /product/xxx?kind=sofa
# In Frappe, form_dict is populated from both path and query string

# Let's check what the actual request object provides
print("Testing form_dict simulation...")
print("For URL: /product/xxx?kind=sofa")
print("frappe.form_dict should contain path params AND query params")

# Check if frappe has a way to get query params
from urllib.parse import parse_qs, urlparse

url = "/product/xxx?kind=sofa"
parsed = urlparse(url)
query = parse_qs(parsed.query)
print(f"Query params: {query}")
print(f"kind from query: {query.get('kind', [None])[0]}")
