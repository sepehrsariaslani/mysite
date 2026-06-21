import frappe
from frappe.website.path_resolver import get_home_page, resolve_path
import os

frappe.init(site="denroom.ir")
frappe.connect()

home_page = frappe.db.get_value("Website Settings", None, "home_page")
print(f"home_page setting: {home_page}")

result = get_home_page()
print(f"get_home_page(): {result}")

www_path = "/home/frappe/frappe-bench/apps/mysite/mysite/www"
home_files = [f for f in os.listdir(www_path) if "home" in f.lower()]
print(f"Files with 'home' in www/: {home_files}")

for path in ["/", "/home", "/home-page"]:
    try:
        resolved = resolve_path(path)
        print(f"resolve_path('{path}'): {resolved}")
    except Exception as e:
        print(f"resolve_path('{path}'): ERROR - {e}")
