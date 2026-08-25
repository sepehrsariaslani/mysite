import json
from urllib.parse import quote, urlparse

import frappe
from erpnext.controllers.website_list_for_contact import get_parents_for_user


FIXED_ROOM_FILTERS = [
    ("bedroom", "اتاق خواب"),
    ("kitchen", "آشپزخانه"),
    ("dining", "ناهارخوری"),
    ("living", "نشیمن"),
    ("office", "دفتر کار"),
    ("outdoor", "فضای باز"),
]
FIXED_ROOM_ID_BY_LABEL = {label: room_id for room_id, label in FIXED_ROOM_FILTERS}


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _normalize_text(value):
    return " ".join(str(value or "").split()).strip().lower()


def _normalize_image(url):
    raw = str(url or "").strip()
    if not raw:
        return ""

    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        raw = parsed.path or raw

    return raw.replace("/private/files/", "/files/")


def _to_toman(rial_price):
    try:
        price = float(rial_price or 0)
    except Exception:
        return 0
    if price <= 0:
        return 0
    return int(price / 10)


def _get_default_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _resolve_customer_price_context(requested_customer):
    selected_customer = None
    selected_price_list = _get_default_price_list()
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


def _room_filter_id(room_label, fallback_index=0):
    if room_label in FIXED_ROOM_ID_BY_LABEL:
        return FIXED_ROOM_ID_BY_LABEL[room_label]
    slug = frappe.scrub(room_label or "")
    if not slug:
        slug = f"room-{fallback_index}"
    return f"custom-{slug}"


def _guess_kind(variant_of, item_name, item_code, attributes):
    raw = _normalize_text(" ".join([variant_of or "", item_name or "", item_code or ""]))

    if "صندلی ناهارخوری" in raw and "اپن" not in raw and "بار" not in raw:
        return "chair"

    if "صندلی اپن" in raw or "بار" in raw or "اپن" in raw:
        return "barstool"

    if "نیمکت" in raw or "پاف" in raw:
        return "bench"

    if (
        "میز ناهارخوری" in raw
        or "میز جلومبلی" in raw
        or "میز عسلی" in raw
        or "باکس" in raw
        or "میز" in raw
    ):
        return "table"

    if attributes and (attributes.get("ماژول") or attributes.get("مدل محصول")):
        return "sofa"

    return "sofa"


def _build_target_route(item_name, kind, selected_customer):
    target_name = str(item_name or "").strip()
    if not target_name:
        return ""
    route = f"/mysite/product?name={quote(target_name)}&kind={quote(kind)}"
    if selected_customer:
        route = f"{route}&customer={quote(selected_customer)}"
    return route


def _query_scene_rows(only_homepage=False, limit=200):
    filters = {"is_published": 1}
    if only_homepage:
        filters["show_on_homepage"] = 1

    try:
        return frappe.get_all(
            "Shop By Look Scene",
            filters=filters,
            fields=[
                "name",
                "title",
                "room_type",
                "room_custom",
                "cover_image",
                "caption",
                "sort_order",
                "modified",
                "show_on_homepage",
            ],
            order_by="sort_order asc, modified desc",
            limit_page_length=max(1, int(limit or 200)),
        )
    except Exception:
        return []


def _query_hotspots_by_scene(scene_names):
    if not scene_names:
        return {}

    try:
        rows = frappe.get_all(
            "Shop By Look Hotspot",
            filters={"parent": ["in", scene_names], "is_active": 1},
            fields=["name", "parent", "idx", "item_code", "x_percent", "y_percent", "label"],
            order_by="parent asc, idx asc",
            limit_page_length=10000,
        )
    except Exception:
        return {}

    result = {}
    for row in rows:
        result.setdefault(row.parent, []).append(row)
    return result


def _fetch_item_payload(item_names, price_list):
    if not item_names:
        return {}

    placeholders = ",".join(["%s"] * len(item_names))
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
            WHERE i.name IN ({placeholders})
            """,
            tuple([price_list or ""] + item_names),
            as_dict=True,
        )

        attrs = frappe.db.sql(
            f"""
            SELECT parent, attribute, attribute_value
            FROM `tabItem Variant Attribute`
            WHERE parent IN ({placeholders})
            """,
            tuple(item_names),
            as_dict=True,
        )
    except Exception:
        return {}

    attrs_map = {}
    for row in attrs:
        attrs_map.setdefault(row.parent, {})[row.attribute] = row.attribute_value

    by_name = {}
    for item in items:
        by_name[item.name] = {
            "name": item.name,
            "item_code": item.item_code or item.name,
            "item_name": item.item_name or item.item_code or item.name,
            "image": _normalize_image(item.image),
            "variant_of": item.variant_of,
            "show_on_site": int(item.show_on_site or 0),
            "disabled": int(item.disabled or 0),
            "odd_cloth": _safe_float(item.odd_cloth),
            "even_cloth": _safe_float(item.even_cloth),
            "minor_cloth": _safe_float(item.minor_cloth),
            "base_price": _to_toman(item.price_list_rate),
            "attributes": attrs_map.get(item.name, {}),
        }

    return by_name


def _build_filters(scenes):
    filters = [{"id": "all", "label": "همه"}]
    for room_id, room_label in FIXED_ROOM_FILTERS:
        filters.append({"id": room_id, "label": room_label})

    seen_custom = set()
    for index, scene in enumerate(scenes):
        room_label = scene.get("room_label")
        if not room_label:
            continue
        if room_label in FIXED_ROOM_ID_BY_LABEL:
            continue
        custom_id = _room_filter_id(room_label, fallback_index=index)
        if custom_id in seen_custom:
            continue
        seen_custom.add(custom_id)
        filters.append({"id": custom_id, "label": room_label})

    return filters


def get_shop_by_look_payload(requested_customer=None, only_homepage=False, limit=200):
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)

    raw_scenes = _query_scene_rows(only_homepage=only_homepage, limit=limit)
    if only_homepage and not raw_scenes:
        raw_scenes = _query_scene_rows(only_homepage=False, limit=limit)
    scene_names = [scene.name for scene in raw_scenes]
    hotspots_by_scene = _query_hotspots_by_scene(scene_names)

    all_item_names = []
    for scene_name in scene_names:
        for hotspot in hotspots_by_scene.get(scene_name, []):
            item_ref = (hotspot.item_code or "").strip()
            if item_ref:
                all_item_names.append(item_ref)

    item_map = _fetch_item_payload(sorted(set(all_item_names)), selected_price_list)

    scenes = []
    for scene_index, scene in enumerate(raw_scenes):
        room_label = (scene.room_custom or "").strip() or (scene.room_type or "").strip() or "سایر"
        filter_id = _room_filter_id(room_label, fallback_index=scene_index)

        hotspots = []
        for hotspot in hotspots_by_scene.get(scene.name, []):
            item_ref = (hotspot.item_code or "").strip()
            item_data = item_map.get(item_ref)
            if not item_data:
                continue
            if not item_data.get("show_on_site") or item_data.get("disabled"):
                continue

            kind = _guess_kind(
                item_data.get("variant_of"),
                item_data.get("item_name"),
                item_data.get("item_code"),
                item_data.get("attributes"),
            )
            target_route = _build_target_route(item_data.get("item_name"), kind, selected_customer)

            hotspots.append(
                {
                    "id": hotspot.name,
                    "x_percent": max(0.0, min(100.0, _safe_float(hotspot.x_percent))),
                    "y_percent": max(0.0, min(100.0, _safe_float(hotspot.y_percent))),
                    "item_code": item_data.get("item_code"),
                    "item_name": item_data.get("item_name"),
                    "item_image": item_data.get("image"),
                    "base_price": item_data.get("base_price", 0),
                    "odd_cloth": item_data.get("odd_cloth", 0),
                    "even_cloth": item_data.get("even_cloth", 0),
                    "minor_cloth": item_data.get("minor_cloth", 0),
                    "kind": kind,
                    "target_route": target_route,
                    "room_label": room_label,
                    "label": (hotspot.label or "").strip() or item_data.get("item_name"),
                }
            )

        scene_cover = _normalize_image(scene.cover_image)
        if not scene_cover and hotspots:
            scene_cover = hotspots[0].get("item_image") or ""

        scenes.append(
            {
                "id": scene.name,
                "title": scene.title,
                "room_type": scene.room_type,
                "room_label": room_label,
                "filter_id": filter_id,
                "cover_image": scene_cover,
                "caption": scene.caption or "",
                "sort_order": scene.sort_order or 0,
                "hotspots": hotspots,
            }
        )

    filters = _build_filters(scenes)

    return {
        "ShopByLookScenes": scenes,
        "ShopByLookFilters": filters,
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }


@frappe.whitelist()
def get_editor_item_previews(item_codes=None, price_list=None):
    if isinstance(item_codes, str):
        item_codes = item_codes.strip()
        if not item_codes:
            item_codes = []
        else:
            try:
                item_codes = json.loads(item_codes)
            except Exception:
                item_codes = [code.strip() for code in item_codes.split(",") if code.strip()]

    if not isinstance(item_codes, (list, tuple, set)):
        item_codes = []

    item_codes = [str(code).strip() for code in item_codes if str(code).strip()]
    if not item_codes:
        return {}

    selected_price_list = (price_list or "").strip() or _get_default_price_list()
    item_map = _fetch_item_payload(sorted(set(item_codes)), selected_price_list)

    previews = {}
    for item_name, data in item_map.items():
        previews[item_name] = {
            "item_code": data.get("item_code"),
            "item_name": data.get("item_name"),
            "image": data.get("image"),
            "base_price": data.get("base_price", 0),
            "show_on_site": data.get("show_on_site", 0),
            "disabled": data.get("disabled", 0),
        }
    return previews
