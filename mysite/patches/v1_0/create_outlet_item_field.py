import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def _available_fields(doctype):
    if not frappe.db.exists("DocType", doctype):
        return set()
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        return set()
    return {f.fieldname for f in (meta.fields or []) if f.fieldname}


def _pick_insert_after(item_fields):
    for candidate in ("special_edition", "show_on_site", "show_in_website", "is_sales_item", "item_group"):
        if candidate in item_fields:
            return candidate
    return "item_code"


def _default_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _seed_sample_outlet_items():
    item_fields = _available_fields("Item")
    if "outlet_product" not in item_fields:
        return 0

    existing_count = frappe.db.count("Item", {"outlet_product": 1, "disabled": 0})
    if existing_count:
        return 0

    conditions = ["COALESCE(i.disabled, 0) = 0"]
    if "is_sales_item" in item_fields:
        conditions.append("COALESCE(i.is_sales_item, 1) = 1")
    if "show_on_site" in item_fields:
        conditions.append("COALESCE(i.show_on_site, 1) = 1")
    elif "show_in_website" in item_fields:
        conditions.append("COALESCE(i.show_in_website, 1) = 1")

    where_clause = " AND ".join(conditions)
    target_codes = []

    default_pl = _default_price_list()
    if default_pl and frappe.db.exists("DocType", "Item Price"):
        priced_rows = frappe.db.sql(
            f"""
            SELECT
              i.name AS item_code,
              MIN(COALESCE(ip.price_list_rate, 0)) AS price_rate
            FROM `tabItem` i
            LEFT JOIN `tabItem Price` ip
              ON ip.item_code = i.name
             AND ip.price_list = %s
             AND COALESCE(ip.selling, 1) = 1
            WHERE {where_clause}
              AND COALESCE(ip.price_list_rate, 0) > 0
            GROUP BY i.name
            ORDER BY price_rate ASC, i.modified DESC
            LIMIT 14
            """,
            [default_pl],
            as_dict=True,
        )
        target_codes = [row.get("item_code") for row in priced_rows if row.get("item_code")]

    if not target_codes:
        fallback_rows = frappe.db.sql(
            f"""
            SELECT i.name AS item_code
            FROM `tabItem` i
            WHERE {where_clause}
            ORDER BY i.modified DESC
            LIMIT 14
            """,
            as_dict=True,
        )
        target_codes = [row.get("item_code") for row in fallback_rows if row.get("item_code")]

    for index, item_code in enumerate(target_codes):
        frappe.db.set_value("Item", item_code, "outlet_product", 1, update_modified=False)
        if "outlet_discount_percent" in item_fields:
            discount = 10 + (index % 6) * 5
            frappe.db.set_value("Item", item_code, "outlet_discount_percent", discount, update_modified=False)

    if target_codes:
        frappe.db.commit()
    return len(target_codes)


def execute():
    item_fields = _available_fields("Item")
    insert_after = _pick_insert_after(item_fields)

    create_custom_fields(
        {
            "Item": [
                {
                    "fieldname": "outlet_product",
                    "label": "Outlet Product",
                    "fieldtype": "Check",
                    "default": "0",
                    "insert_after": insert_after,
                    "description": "اگر فعال باشد، این محصول در صفحه Outlet نمایش داده می‌شود.",
                },
                {
                    "fieldname": "outlet_discount_percent",
                    "label": "Outlet Discount (%)",
                    "fieldtype": "Percent",
                    "default": "20",
                    "insert_after": "outlet_product",
                    "description": "درصد تخفیف مخصوص Outlet برای نمایش قیمت ویژه.",
                },
            ]
        },
        update=True,
    )

    frappe.clear_cache(doctype="Item")
    _seed_sample_outlet_items()
