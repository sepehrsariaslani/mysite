from urllib.parse import quote, unquote

import frappe
from erpnext.controllers.website_list_for_contact import get_parents_for_user


FIXED_PROJECT_TYPES = [
    ("home", "خانه"),
    ("restaurant", "رستوران"),
    ("cafe", "کافه"),
    ("office", "اداری"),
    ("retail", "فروشگاهی"),
    ("villa", "ویلا"),
]
FIXED_TYPE_ID_BY_LABEL = {label: type_id for type_id, label in FIXED_PROJECT_TYPES}


def _normalize_text(value):
    return " ".join(str(value or "").split()).strip().lower()


def _normalize_image(url):
    raw = str(url or "").strip()
    if not raw:
        return ""
    return raw.replace("/private/files/", "/files/")


def _safe_int(value, default=0):
    try:
        return int(value or 0)
    except Exception:
        return int(default)


def _safe_float(value, default=0.0):
    try:
        return float(value or 0)
    except Exception:
        return float(default)


def _to_toman(rial_price):
    amount = _safe_float(rial_price, default=0.0)
    if amount <= 0:
        return 0
    return int(amount / 10)


def _get_available_fields(doctype):
    if not frappe.db.exists("DocType", doctype):
        return set()
    try:
        meta = frappe.get_meta(doctype)
        return {f.fieldname for f in (meta.fields or []) if f.fieldname}
    except Exception:
        return set()


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


def _guess_kind(variant_of, item_name, item_code, attributes):
    raw = _normalize_text(" ".join([variant_of or "", item_name or "", item_code or ""]))

    if "صندلی ناهارخوری" in raw and "اپن" not in raw and "بار" not in raw:
        return "chair"
    if "صندلی اپن" in raw or "بار" in raw or "اپن" in raw:
        return "barstool"
    if "نیمکت" in raw or "پاف" in raw:
        return "bench"
    if "میز" in raw or "جلومبلی" in raw or "عسلی" in raw or "باکس" in raw:
        return "table"
    if attributes and (attributes.get("ماژول") or attributes.get("مدل محصول")):
        return "sofa"
    return "sofa"


def _build_target_route(item_name, kind, selected_customer):
    target_name = str(item_name or "").strip()
    if not target_name:
        return ""
    route = f"/product?name={quote(target_name)}&kind={quote(kind)}"
    if selected_customer:
        route = f"{route}&customer={quote(selected_customer)}"
    return route


def _project_filter_id(project_type_label, fallback_index=0):
    normalized_label = (project_type_label or "").strip()
    if normalized_label in FIXED_TYPE_ID_BY_LABEL:
        return FIXED_TYPE_ID_BY_LABEL[normalized_label]

    slug = frappe.scrub(normalized_label)
    if not slug:
        slug = f"type-{fallback_index}"
    return f"custom-{slug}"


def _resolve_project_type_label(project_row):
    project_type = (project_row.get("project_type") or "").strip()
    if project_type == "سایر":
        custom = (project_row.get("project_type_custom") or "").strip()
        if custom:
            return custom
    return project_type or "سایر"


def _query_project_rows(only_homepage=False, limit=200):
    if not frappe.db.exists("DocType", "Customer Project"):
        return []

    available_fields = _get_available_fields("Customer Project")
    if not available_fields:
        return []

    filters = {}
    if "is_published" in available_fields:
        filters["is_published"] = 1
    if only_homepage and "show_on_homepage" in available_fields:
        filters["show_on_homepage"] = 1

    requested_fields = [
        "name",
        "title",
        "project_type",
        "project_type_custom",
        "customer_name",
        "location",
        "project_date",
        "project_area_sqm",
        "cover_image",
        "short_description",
        "client_request",
        "extended_notes",
        "full_description",
        "sort_order",
        "modified",
    ]
    fields = [f for f in requested_fields if f == "name" or f in available_fields]
    order_by = "sort_order asc, modified desc" if "sort_order" in available_fields else "modified desc"

    try:
        return frappe.get_all(
            "Customer Project",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=max(1, _safe_int(limit, default=200)),
        )
    except Exception:
        return []


def _query_project_products(project_names):
    if not project_names:
        return {}
    if not frappe.db.exists("DocType", "Customer Project Product"):
        return {}

    available_fields = _get_available_fields("Customer Project Product")
    if not available_fields:
        return {}

    filters = {"parent": ["in", project_names]}
    if "is_active" in available_fields:
        filters["is_active"] = 1
    requested_fields = [
        "name",
        "parent",
        "idx",
        "item_code",
        "cloth_item",
        "project_image",
        "qty",
        "note",
        "sort_order",
    ]
    core_fields = {"name", "parent", "idx"}
    fields = [f for f in requested_fields if f in core_fields or f in available_fields]
    order_parts = ["parent asc"]
    if "sort_order" in available_fields:
        order_parts.append("sort_order asc")
    if "idx" in available_fields:
        order_parts.append("idx asc")
    order_by = ", ".join(order_parts)

    try:
        rows = frappe.get_all(
            "Customer Project Product",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=10000,
        )
    except Exception:
        return {}

    grouped = {}
    for row in rows:
        grouped.setdefault(row.parent, []).append(row)
    return grouped


def _query_project_images(project_names):
    if not project_names:
        return {}
    if not frappe.db.exists("DocType", "Customer Project Image"):
        return {}

    available_fields = _get_available_fields("Customer Project Image")
    if not available_fields:
        return {}

    filters = {"parent": ["in", project_names]}
    if "is_active" in available_fields:
        filters["is_active"] = 1
    requested_fields = ["name", "parent", "idx", "image", "caption", "sort_order"]
    core_fields = {"name", "parent", "idx"}
    fields = [f for f in requested_fields if f in core_fields or f in available_fields]
    order_parts = ["parent asc"]
    if "sort_order" in available_fields:
        order_parts.append("sort_order asc")
    if "idx" in available_fields:
        order_parts.append("idx asc")
    order_by = ", ".join(order_parts)

    try:
        rows = frappe.get_all(
            "Customer Project Image",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=10000,
        )
    except Exception:
        return {}

    grouped = {}
    for row in rows:
        grouped.setdefault(row.parent, []).append(row)
    return grouped


def _fetch_item_payload(item_codes, price_list):
    item_codes = [str(code or "").strip() for code in (item_codes or []) if str(code or "").strip()]
    if not item_codes:
        return {}

    placeholders = ",".join(["%s"] * len(item_codes))
    try:
        items = frappe.db.sql(
            f"""
            SELECT
                i.name,
                i.item_code,
                i.item_name,
                i.image,
                i.variant_of,
                COALESCE(i.show_on_site, 0) as show_on_site,
                COALESCE(i.disabled, 0) as disabled,
                COALESCE(i.odd_cloth, 0) as odd_cloth,
                COALESCE(i.even_cloth, 0) as even_cloth,
                COALESCE(i.minor_cloth, 0) as minor_cloth,
                COALESCE(ip.price_list_rate, 0) as price_list_rate
            FROM `tabItem` i
            LEFT JOIN `tabItem Price` ip
              ON i.name = ip.item_code
             AND ip.price_list = %s
            WHERE i.name IN ({placeholders}) OR i.item_code IN ({placeholders})
            """,
            tuple([price_list or ""] + item_codes + item_codes),
            as_dict=True,
        )
        item_names = [row.name for row in items]
        if item_names:
            attr_placeholders = ",".join(["%s"] * len(item_names))
            attrs = frappe.db.sql(
                f"""
                SELECT parent, attribute, attribute_value
                FROM `tabItem Variant Attribute`
                WHERE parent IN ({attr_placeholders})
                """,
                tuple(item_names),
                as_dict=True,
            )
        else:
            attrs = []
    except Exception:
        return {}

    attrs_map = {}
    for row in attrs:
        attrs_map.setdefault(row.parent, {})[row.attribute] = row.attribute_value

    payload = {}
    for row in items:
        normalized = {
            "item_code": row.item_code or row.name,
            "item_name": row.item_name or row.item_code or row.name,
            "image": _normalize_image(row.image),
            "variant_of": row.variant_of,
            "show_on_site": _safe_int(row.show_on_site),
            "disabled": _safe_int(row.disabled),
            "odd_cloth": _safe_float(row.odd_cloth),
            "even_cloth": _safe_float(row.even_cloth),
            "minor_cloth": _safe_float(row.minor_cloth),
            "base_price": _to_toman(row.price_list_rate),
            "attributes": attrs_map.get(row.name, {}),
        }
        payload[row.name] = normalized
        payload[row.item_code] = normalized
    return payload


def _serialize_project_product(row, item_data, cloth_data, selected_customer):
    if not item_data:
        return None
    if not item_data.get("show_on_site") or item_data.get("disabled"):
        return None

    kind = _guess_kind(
        item_data.get("variant_of"),
        item_data.get("item_name"),
        item_data.get("item_code"),
        item_data.get("attributes"),
    )
    target_route = _build_target_route(item_data.get("item_name"), kind, selected_customer)
    qty = _safe_int(row.qty, default=1)
    if qty <= 0:
        qty = 1

    return {
        "id": row.name,
        "item_code": item_data.get("item_code"),
        "item_name": item_data.get("item_name"),
        "image": _normalize_image(row.project_image) or item_data.get("image") or "",
        "base_price": _safe_int(item_data.get("base_price")),
        "odd_cloth": _safe_float(item_data.get("odd_cloth")),
        "even_cloth": _safe_float(item_data.get("even_cloth")),
        "minor_cloth": _safe_float(item_data.get("minor_cloth")),
        "note": (row.note or "").strip(),
        "qty": qty,
        "cloth_item_code": cloth_data.get("item_code") if cloth_data else (row.cloth_item or ""),
        "cloth_name": cloth_data.get("item_name") if cloth_data else "",
        "cloth_base_price": _safe_int(cloth_data.get("base_price")) if cloth_data else 0,
        "kind": kind,
        "target_route": target_route,
    }


def _build_filters(projects):
    filters = [{"id": "all", "label": "همه"}]
    for type_id, type_label in FIXED_PROJECT_TYPES:
        filters.append({"id": type_id, "label": type_label})

    seen_custom = set()
    for index, project in enumerate(projects):
        type_label = project.get("project_type_label")
        if not type_label:
            continue
        if type_label in FIXED_TYPE_ID_BY_LABEL:
            continue
        custom_id = _project_filter_id(type_label, fallback_index=index)
        if custom_id in seen_custom:
            continue
        seen_custom.add(custom_id)
        filters.append({"id": custom_id, "label": type_label})

    return filters


def _serialize_project_images(rows):
    result = []
    for row in rows or []:
        image_url = _normalize_image(row.image)
        if not image_url:
            continue
        result.append(
            {
                "id": row.name,
                "image": image_url,
                "caption": (row.caption or "").strip(),
            }
        )
    return result


def _build_project_entry(
    project_row,
    project_products,
    project_image_rows,
    item_map,
    selected_customer,
    fallback_index=0,
):
    serialized_products = []
    for row in project_products:
        item_code = str(row.get("item_code") or "").strip()
        cloth_code = str(row.get("cloth_item") or "").strip()
        item_data = item_map.get(item_code)
        cloth_data = item_map.get(cloth_code) if cloth_code else None
        serialized = _serialize_project_product(row, item_data, cloth_data, selected_customer)
        if serialized:
            serialized_products.append(serialized)

    project_images = _serialize_project_images(project_image_rows)

    project_type_label = _resolve_project_type_label(project_row)
    filter_id = _project_filter_id(project_type_label, fallback_index=fallback_index)
    project_name = project_row.get("name") or ""
    project_route = f"/project?name={quote(project_name)}"
    if selected_customer:
        project_route = f"{project_route}&customer={quote(selected_customer)}"

    cover_image = _normalize_image(project_row.cover_image)
    if not cover_image and project_images:
        cover_image = project_images[0].get("image") or ""
    if not cover_image and serialized_products:
        cover_image = serialized_products[0].get("image") or ""

    return {
        "id": project_name,
        "name": project_name,
        "title": project_row.get("title") or project_name,
        "project_type": project_row.get("project_type"),
        "project_type_label": project_type_label,
        "filter_id": filter_id,
        "customer_name": str(project_row.get("customer_name") or "").strip(),
        "location": str(project_row.get("location") or "").strip(),
        "project_date": str(project_row.get("project_date") or ""),
        "project_area_sqm": _safe_float(project_row.get("project_area_sqm")),
        "cover_image": cover_image,
        "short_description": str(project_row.get("short_description") or "").strip(),
        "client_request": str(project_row.get("client_request") or "").strip(),
        "extended_notes": project_row.get("extended_notes") or "",
        "full_description": project_row.get("full_description") or "",
        "route": project_route,
        "project_images": project_images,
        "products": serialized_products,
        "preview_products": serialized_products[:5],
        "product_count": len(serialized_products),
    }


def get_projects_payload(requested_customer=None, only_homepage=False, limit=200):
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)

    project_rows = _query_project_rows(only_homepage=only_homepage, limit=limit)

    project_names = [row.name for row in project_rows]
    products_by_project = _query_project_products(project_names)
    images_by_project = _query_project_images(project_names)

    item_codes = []
    for project_name in project_names:
        for row in products_by_project.get(project_name, []):
            code = (row.item_code or "").strip()
            if code:
                item_codes.append(code)
            cloth_code = (row.cloth_item or "").strip()
            if cloth_code:
                item_codes.append(cloth_code)

    item_map = _fetch_item_payload(sorted(set(item_codes)), selected_price_list)

    projects = []
    for index, row in enumerate(project_rows):
        project = _build_project_entry(
            project_row=row,
            project_products=products_by_project.get(row.name, []),
            project_image_rows=images_by_project.get(row.name, []),
            item_map=item_map,
            selected_customer=selected_customer,
            fallback_index=index,
        )
        projects.append(project)

    return {
        "Projects": projects,
        "ProjectFilters": _build_filters(projects),
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }


def _find_project_name(requested_name):
    requested_name = unquote(str(requested_name or "")).strip()
    if not requested_name:
        return ""
    if not frappe.db.exists("DocType", "Customer Project"):
        return ""

    if frappe.db.exists("Customer Project", requested_name):
        return requested_name

    matched = frappe.get_all(
        "Customer Project",
        filters={"title": requested_name, "is_published": 1},
        fields=["name"],
        order_by="sort_order asc, modified desc",
        limit_page_length=1,
    )
    if matched:
        return matched[0].name
    return ""


def get_project_detail_payload(project_name, requested_customer=None):
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)

    if not frappe.db.exists("DocType", "Customer Project"):
        return {
            "ProjectDetails": None,
            "SelectedCustomer": selected_customer or "",
            "SelectedPriceList": selected_price_list or "",
            "PriceSource": price_source,
        }

    resolved_name = _find_project_name(project_name)
    if not resolved_name:
        return {
            "ProjectDetails": None,
            "SelectedCustomer": selected_customer or "",
            "SelectedPriceList": selected_price_list or "",
            "PriceSource": price_source,
        }

    available_fields = _get_available_fields("Customer Project")
    filters = {"name": resolved_name}
    if "is_published" in available_fields:
        filters["is_published"] = 1
    requested_fields = [
        "name",
        "title",
        "project_type",
        "project_type_custom",
        "customer_name",
        "location",
        "project_date",
        "project_area_sqm",
        "cover_image",
        "short_description",
        "client_request",
        "extended_notes",
        "full_description",
        "sort_order",
        "modified",
    ]
    fields = [f for f in requested_fields if f == "name" or f in available_fields]
    project_rows = frappe.get_all(
        "Customer Project",
        filters=filters,
        fields=fields,
        limit_page_length=1,
    )
    if not project_rows:
        return {
            "ProjectDetails": None,
            "SelectedCustomer": selected_customer or "",
            "SelectedPriceList": selected_price_list or "",
            "PriceSource": price_source,
        }

    project_row = project_rows[0]
    products_by_project = _query_project_products([project_row.name])
    images_by_project = _query_project_images([project_row.name])
    project_products = products_by_project.get(project_row.name, [])
    item_codes = []
    for row in project_products:
        code = str(row.item_code or "").strip()
        cloth_code = str(row.cloth_item or "").strip()
        if code:
            item_codes.append(code)
        if cloth_code:
            item_codes.append(cloth_code)
    item_map = _fetch_item_payload(sorted(set(item_codes)), selected_price_list)

    project_details = _build_project_entry(
        project_row=project_row,
        project_products=project_products,
        project_image_rows=images_by_project.get(project_row.name, []),
        item_map=item_map,
        selected_customer=selected_customer,
        fallback_index=0,
    )

    return {
        "ProjectDetails": project_details,
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }
