import re
from urllib.parse import quote

import frappe
from erpnext.controllers.website_list_for_contact import get_parents_for_user

from mysite.www.mysite.cloth import get_cloth_groups


no_cache = 1


_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def _safe_float(value, default=0.0):
    try:
        return float(value or 0)
    except Exception:
        return float(default)


def _to_toman(rial_price):
    amount = _safe_float(rial_price)
    if amount <= 0:
        return 0
    return int(amount / 10)


def _normalize_image(url):
    return str(url or "").strip().replace("/private/files/", "/files/")


def _normalize_key(value):
    return " ".join(str(value or "").split()).strip().lower()


def _extract_code(text):
    value = str(text or "").strip()
    if not value:
        return ""
    matches = re.findall(r"([0-9\u06F0-\u06F9]+)", value)
    if not matches:
        return ""
    return matches[-1]


def _append_customer(route, customer):
    if not route:
        return route
    if not customer:
        return route
    if "customer=" in route:
        return route
    joiner = "&" if "?" in route else "?"
    return f"{route}{joiner}customer={quote(customer)}"


def _get_default_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _resolve_customer_price_context(requested_customer):
    selected_customer = ""
    selected_price_list = _get_default_price_list() or ""
    price_source = "default"

    requested_customer = (requested_customer or "").strip()
    if not requested_customer or frappe.session.user == "Guest":
        return selected_customer, selected_price_list, price_source

    try:
        allowed_customers = get_parents_for_user("Customer") or []
    except Exception:
        allowed_customers = []

    if requested_customer in allowed_customers:
        selected_customer = requested_customer
        customer_price_list = frappe.db.get_value("Customer", requested_customer, "default_price_list")
        if customer_price_list:
            selected_price_list = customer_price_list
            price_source = "customer"

    return selected_customer, selected_price_list, price_source


def _guess_item_kind(item_row):
    raw = " ".join(
        [
            str(item_row.get("variant_of") or ""),
            str(item_row.get("item_name") or ""),
            str(item_row.get("item_code") or ""),
        ]
    ).lower()

    if "صندلی ناهارخوری" in raw and "اپن" not in raw and "بار" not in raw:
        return "chair"
    if "صندلی اپن" in raw or "بار" in raw or "اپن" in raw:
        return "barstool"
    if "نیمکت" in raw or "پاف" in raw:
        return "bench"
    if "میز" in raw or "جلومبلی" in raw or "عسلی" in raw or "باکس" in raw:
        return "table"
    return "sofa"


def _table_has_column(table_name, column_name):
    try:
        rows = frappe.db.sql(
            f"SHOW COLUMNS FROM `{table_name}` LIKE %s",
            (column_name,),
            as_dict=True,
        )
        return bool(rows)
    except Exception:
        return False


def _flatten_fabrics(cloth_groups):
    fabrics = []
    quality_set = set()
    code_set = set()

    for group in cloth_groups or []:
        quality = str(group.get("name") or "").strip()
        if not quality:
            continue
        quality_set.add(quality)

        for variant in group.get("clothvariants") or []:
            item_code = str(variant.get("item_code") or variant.get("name") or "").strip()
            item_name = str(variant.get("item_name") or variant.get("name") or "").strip()
            display_name = str(variant.get("name") or item_name or item_code).strip()
            code = str(variant.get("code") or "").strip() or _extract_code(display_name)
            bucket = str(variant.get("bucket") or "").strip()

            if code:
                code_set.add(code)

            fabrics.append(
                {
                    "id": f"{quality}::{item_code or display_name}",
                    "quality": quality,
                    "quality_name": quality,
                    "name": display_name,
                    "item_name": item_name,
                    "item_code": item_code,
                    "code": code,
                    "bucket": bucket,
                    "image": _normalize_image(variant.get("image") or group.get("sample_image")),
                    "price_per_meter": int(variant.get("Price") or 0),
                    "formatted_price": variant.get("formatted_Price") or "۰",
                    "formatted_group_price": group.get("average_purchase_price") or "۰",
                    "sample_image": _normalize_image(group.get("sample_image")),
                }
            )

    fabrics.sort(key=lambda x: (x.get("quality") or "", x.get("code") or "", x.get("name") or ""))

    return fabrics, {
        "qualities": sorted(quality_set),
        "codes": sorted(code_set),
    }


def _fetch_project_pairs():
    if not _table_has_column("tabCustomer Project Product", "cloth_item"):
        return []

    conditions = [
        "COALESCE(item_code, '') <> ''",
        "COALESCE(cloth_item, '') <> ''",
    ]
    if _table_has_column("tabCustomer Project Product", "is_active"):
        conditions.append("COALESCE(is_active, 1) = 1")

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT item_code, cloth_item
        FROM `tabCustomer Project Product`
        WHERE {where_clause}
    """

    try:
        return frappe.db.sql(query, as_dict=True)
    except Exception:
        return []


def _fetch_products(price_list, selected_customer, required_codes=None):
    required_codes = [str(code or "").strip() for code in (required_codes or []) if str(code or "").strip()]

    base_where = (
        "i.show_on_site = 1 "
        "AND COALESCE(i.disabled, 0) = 0 "
        "AND ("
        "COALESCE(i.odd_cloth, 0) > 0 OR "
        "COALESCE(i.even_cloth, 0) > 0 OR "
        "COALESCE(i.minor_cloth, 0) > 0"
        ")"
    )

    params = [price_list or ""]
    code_clause = ""
    if required_codes:
        placeholders = ",".join(["%s"] * len(required_codes))
        code_clause = f" OR i.name IN ({placeholders}) OR i.item_code IN ({placeholders})"
        params.extend(required_codes)
        params.extend(required_codes)

    query = f"""
        SELECT
            i.name,
            i.item_code,
            i.item_name,
            i.variant_of,
            i.image,
            i.modified,
            COALESCE(i.odd_cloth, 0) AS odd_cloth,
            COALESCE(i.even_cloth, 0) AS even_cloth,
            COALESCE(i.minor_cloth, 0) AS minor_cloth,
            COALESCE(ip.price_list_rate, 0) AS price_list_rate
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` ip
            ON i.name = ip.item_code
           AND ip.price_list = %s
        WHERE i.is_stock_item = 1
          AND ({base_where}{code_clause})
        ORDER BY i.modified DESC
        LIMIT 500
    """

    rows = frappe.db.sql(query, tuple(params), as_dict=True)
    if not rows:
        return [], {}

    parents = [row.name for row in rows if row.get("name")]
    colors_by_parent = {name: [] for name in parents}

    if parents:
        placeholders = ",".join(["%s"] * len(parents))
        attr_rows = frappe.db.sql(
            f"""
                SELECT parent, attribute, attribute_value
                FROM `tabItem Variant Attribute`
                WHERE parent IN ({placeholders})
                  AND attribute IN ('رنگ بدنه', 'رنگ چوب')
                ORDER BY parent ASC, idx ASC
            """,
            tuple(parents),
            as_dict=True,
        )
        for attr in attr_rows:
            value = str(attr.get("attribute_value") or "").strip()
            if not value:
                continue
            arr = colors_by_parent.setdefault(attr.get("parent"), [])
            if value not in arr:
                arr.append(value)

    products = []
    alias_map = {}

    for row in rows:
        item_code = str(row.get("item_code") or row.get("name") or "").strip()
        item_name = str(row.get("item_name") or item_code).strip()
        kind = _guess_item_kind(row)
        model_name = row.get("variant_of") or row.get("item_name") or row.get("name")
        route = _append_customer(
            f"/mysite/product?name={quote(str(model_name or ''))}&kind={quote(kind)}",
            selected_customer,
        )

        payload = {
            "id": row.get("name"),
            "item_code": item_code,
            "item_name": item_name,
            "image": _normalize_image(row.get("image")),
            "kind": kind,
            "route": route,
            "colors": colors_by_parent.get(row.get("name"), []),
            "base_price": _to_toman(row.get("price_list_rate")),
            "odd_cloth": _safe_float(row.get("odd_cloth")),
            "even_cloth": _safe_float(row.get("even_cloth")),
            "minor_cloth": _safe_float(row.get("minor_cloth")),
        }
        products.append(payload)

        for alias in [row.get("name"), row.get("item_code"), item_code]:
            key = _normalize_key(alias)
            if key and key not in alias_map:
                alias_map[key] = payload

    return products, alias_map


def _build_project_links(fabrics, project_pairs, product_alias_map):
    if not project_pairs:
        return {}

    cloth_alias_map = {}
    for fabric in fabrics:
        canonical = str(fabric.get("item_code") or "").strip()
        if not canonical:
            continue
        for alias in [fabric.get("item_code"), fabric.get("item_name"), fabric.get("name")]:
            key = _normalize_key(alias)
            if not key:
                continue
            cloth_alias_map.setdefault(key, set()).add(canonical)

    links = {}
    seen = {}

    for pair in project_pairs:
        product = product_alias_map.get(_normalize_key(pair.get("item_code")))
        if not product:
            continue

        cloth_value = str(pair.get("cloth_item") or "").strip()
        if not cloth_value:
            continue

        target_codes = cloth_alias_map.get(_normalize_key(cloth_value), set())
        if not target_codes:
            continue

        for cloth_code in target_codes:
            links.setdefault(cloth_code, [])
            seen.setdefault(cloth_code, set())
            pid = product.get("item_code")
            if pid in seen[cloth_code]:
                continue
            seen[cloth_code].add(pid)
            links[cloth_code].append(product)

    return links


def get_boot_data():
    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)

    cloth_groups = get_cloth_groups(selected_price_list or "Standard Selling")
    fabrics, filter_meta = _flatten_fabrics(cloth_groups)

    project_pairs = _fetch_project_pairs()
    required_item_codes = [row.get("item_code") for row in project_pairs]

    related_products, product_alias_map = _fetch_products(
        price_list=selected_price_list,
        selected_customer=selected_customer,
        required_codes=required_item_codes,
    )

    project_links = _build_project_links(fabrics, project_pairs, product_alias_map)

    return {
        "ClothGroups": cloth_groups,
        "Fabrics": fabrics,
        "FabricFilterMeta": filter_meta,
        "FabricRelatedProducts": related_products,
        "FabricProjectLinks": project_links,
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
        "site_name": frappe.local.site,
    }


def get_context(context):
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""

    context.boot = get_boot_data()
    context.boot["csrf_token"] = csrf_token
    context.safe_render = 0
    return context
