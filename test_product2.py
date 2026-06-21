import frappe
from frappe.website.utils import can_cache

# Check what frappe.form_dict returns for a URL with ?kind=sofa
# Simulate the URL parsing
from urllib.parse import urlparse, parse_qs

url = "/product/%D8%A8%D8%A7%DA%A9%D8%B3-%D8%A7%D9%88%D8%B1%D8%A7%D9%85%D8%A7%D9%86-%D8%A8%DB%8C%D8%B6%DB%8C-%D8%B7%D9%88%D9%84-%DB%B8%DB%B0-%D8%B9%D8%B1%D8%B6-%DB%B4%DB%B0-%D8%AE%D9%88%D8%AF%D8%B1%D9%86%DA%AF?kind=sofa"
parsed = urlparse(url)
query_params = parse_qs(parsed.query)
print(f"Query params from URL: {query_params}")
print(f"kind value: {query_params.get('kind', [''])[0]}")

# Now check what the actual product.py does
from mysite.www.product import context
import sys

# Try to simulate the request
try:
    # Directly call the context function
    result = context(frappe._dict({
        'name': '',
        'kind': 'sofa',
        'customer': '',
        'bundle': ''
    }))
    print("context() succeeded")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:200]}")
