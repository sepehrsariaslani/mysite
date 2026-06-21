from __future__ import annotations

from urllib.parse import quote, unquote

import frappe
from erpnext.controllers.website_list_for_contact import get_parents_for_user


SAMPLE_SPECIAL_ITEMS = [
    {
        "item_code": "SE-SOFA-HERMES-NOIR",
        "title": "هرمس نُوار",
        "model": "کالکشن Signature Sofa",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 289000000,
        "edition_count": 7,
        "detail_route": "/special-edition/SE-SOFA-HERMES-NOIR",
        "product_route": "/sofas",
        "is_fake": 1,
    },
    {
        "item_code": "SE-CHAIR-MAHOUR-ATELIER",
        "title": "ماهور Atelier",
        "model": "Dining Chair Couture",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 126000000,
        "edition_count": 12,
        "detail_route": "/special-edition/SE-CHAIR-MAHOUR-ATELIER",
        "product_route": "/dining-chairs",
        "is_fake": 1,
    },
    {
        "item_code": "SE-TABLE-LUMEN-8P",
        "title": "لومن ۸ نفره",
        "model": "Grand Dining Table",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 314000000,
        "edition_count": 5,
        "detail_route": "/special-edition/SE-TABLE-LUMEN-8P",
        "product_route": "/tables",
        "is_fake": 1,
    },
    {
        "item_code": "SE-BENCH-ROUZAN-ARC",
        "title": "روزان Arc",
        "model": "Bench Collection",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 98000000,
        "edition_count": 9,
        "detail_route": "/special-edition/SE-BENCH-ROUZAN-ARC",
        "product_route": "/benches",
        "is_fake": 1,
    },
    {
        "item_code": "SE-BARSTOOL-SANTIA-LTD",
        "title": "سانتیا Limited",
        "model": "Barstool Edition",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 86500000,
        "edition_count": 14,
        "detail_route": "/special-edition/SE-BARSTOOL-SANTIA-LTD",
        "product_route": "/barstools",
        "is_fake": 1,
    },
    {
        "item_code": "SE-COFFEE-ATRIUM-SET",
        "title": "Atrium Set",
        "model": "Coffee Table Premium",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 109000000,
        "edition_count": 11,
        "detail_route": "/special-edition/SE-COFFEE-ATRIUM-SET",
        "product_route": "/coffee-tables",
        "is_fake": 1,
    },
    {
        "item_code": "SE-SOFA-ROUZAN-RESERVE",
        "title": "روژان Reserve",
        "model": "Sofa Collector Edition",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 276000000,
        "edition_count": 8,
        "detail_route": "/special-edition/SE-SOFA-ROUZAN-RESERVE",
        "product_route": "/sofas",
        "is_fake": 1,
    },
    {
        "item_code": "SE-CHAIR-NOURA-PRIME",
        "title": "نورا Prime",
        "model": "Dining Chair Limited",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 118000000,
        "edition_count": 10,
        "detail_route": "/special-edition/SE-CHAIR-NOURA-PRIME",
        "product_route": "/dining-chairs",
        "is_fake": 1,
    },
    {
        "item_code": "SE-TABLE-ASTRA-10P",
        "title": "Astra 10P",
        "model": "Dining Table Signature",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 332000000,
        "edition_count": 4,
        "detail_route": "/special-edition/SE-TABLE-ASTRA-10P",
        "product_route": "/tables",
        "is_fake": 1,
    },
    {
        "item_code": "SE-BENCH-KIYAN-ARC",
        "title": "کیان Arc",
        "model": "Bench Signature",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 102000000,
        "edition_count": 9,
        "detail_route": "/special-edition/SE-BENCH-KIYAN-ARC",
        "product_route": "/benches",
        "is_fake": 1,
    },
    {
        "item_code": "SE-BARSTOOL-VERA-NERO",
        "title": "Vera Nero",
        "model": "Barstool Atelier",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 93500000,
        "edition_count": 13,
        "detail_route": "/special-edition/SE-BARSTOOL-VERA-NERO",
        "product_route": "/barstools",
        "is_fake": 1,
    },
    {
        "item_code": "SE-COFFEE-ONYX-DUO",
        "title": "Onyx Duo",
        "model": "Coffee Table Ultra",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 124000000,
        "edition_count": 6,
        "detail_route": "/special-edition/SE-COFFEE-ONYX-DUO",
        "product_route": "/coffee-tables",
        "is_fake": 1,
    },
]


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


def _normalize_text(value):
    return " ".join(str(value or "").split()).strip()


def _normalize_image(raw):
    image = str(raw or "").strip()
    if not image:
        return "/assets/mysite/img/placeholder.png"
    return image.replace("/private/files/", "/files/")


def _to_toman(value):
    amount = _safe_float(value, default=0.0)
    if amount <= 0:
        return 0
    return int(amount / 10)


def _default_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _resolve_customer_price_context(requested_customer):
    selected_customer = ""
    selected_price_list = _default_price_list() or ""
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


def _get_available_fields(doctype):
    if not frappe.db.exists("DocType", doctype):
        return set()
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        return set()
    return {f.fieldname for f in (meta.fields or []) if f.fieldname}


def _guess_kind(variant_of, item_name, item_code):
    raw = " ".join([str(variant_of or ""), str(item_name or ""), str(item_code or "")]).lower()
    if "صندلی ناهارخوری" in raw and "اپن" not in raw and "بار" not in raw:
        return "chair"
    if "صندلی اپن" in raw or "بار" in raw or "اپن" in raw:
        return "barstool"
    if "نیمکت" in raw or "پاف" in raw:
        return "bench"
    if "میز ناهارخوری" in raw or ("ناهارخوری" in raw and "میز" in raw):
        return "dining_table"
    if (
        "میز جلومبلی" in raw
        or "جلومبلی" in raw
        or "میز عسلی" in raw
        or "باکس" in raw
        or "میز" in raw
    ):
        return "coffee_table"
    return "sofa"


def _route_kind_value(kind):
    if kind in {"dining_table", "coffee_table"}:
        return "table"
    return str(kind or "").strip().lower()


def _build_product_route(route_name, kind):
    return f"/product?name={quote(str(route_name))}&kind={quote(_route_kind_value(kind))}"


def _build_detail_route(item_code):
    return f"/special-edition/{quote(str(item_code))}"


def _merge_with_sample_items(items, limit, exclude_codes=None):
    safe_limit = max(1, _safe_int(limit, default=12))
    blocked = {
        _normalize_text(code)
        for code in (exclude_codes or [])
        if _normalize_text(code)
    }

    merged = []
    seen_codes = set(blocked)

    for row in items or []:
        code = _normalize_text((row or {}).get("item_code"))
        if not code or code in seen_codes:
            continue
        merged.append(dict(row))
        seen_codes.add(code)
        if len(merged) >= safe_limit:
            return merged

    for sample in SAMPLE_SPECIAL_ITEMS:
        code = _normalize_text(sample.get("item_code"))
        if not code or code in seen_codes:
            continue
        merged.append(dict(sample))
        seen_codes.add(code)
        if len(merged) >= safe_limit:
            break

    return merged


def _extract_model_from_item_name(item_name):
    label = str(item_name or "").strip()
    if not label:
        return ""

    if "مدل " in label:
        label = label.split("مدل ", 1)[1].strip()
    else:
        for prefix in (
            "صندلی اپن ",
            "صندلی ناهارخوری ",
            "میز ناهارخوری ",
            "میز جلومبلی ",
            "میز عسلی ",
            "مبل ",
            "کاناپه ",
            "نیمکت ",
        ):
            if label.startswith(prefix):
                label = label[len(prefix):].strip()
                break

    for separator in (" همراه ", " بدون ", " با ", " رنگ ", " - ", " | ", " / ", "("):
        if separator in label:
            label = label.split(separator, 1)[0].strip()

    return " ".join(label.split()).strip()


def _edition_count_for_item(item_code):
    code = str(item_code or "")
    seed = sum(ord(ch) for ch in code) % 11
    return 5 + seed


def _fetch_special_items(selected_price_list, limit):
    item_fields = _get_available_fields("Item")
    if "special_edition" not in item_fields:
        return []

    filters = {"special_edition": 1}
    if "disabled" in item_fields:
        filters["disabled"] = 0
    if "show_on_site" in item_fields:
        filters["show_on_site"] = 1
    elif "show_in_website" in item_fields:
        filters["show_in_website"] = 1
    if "is_sales_item" in item_fields:
        filters["is_sales_item"] = 1

    requested_fields = [
        "name",
        "item_name",
        "variant_of",
        "item_group",
        "image",
        "modified",
    ]
    fields = [f for f in requested_fields if f == "name" or f in item_fields]

    rows = frappe.get_all(
        "Item",
        filters=filters,
        fields=fields,
        order_by="modified desc",
        limit_page_length=max(24, _safe_int(limit, default=12) * 3),
    )
    if not rows:
        return []

    item_codes = [row.get("name") for row in rows if row.get("name")]
    if not item_codes:
        return []

    price_map = {}
    if selected_price_list and frappe.db.exists("DocType", "Item Price"):
        price_fields = _get_available_fields("Item Price")
        price_filters = {
            "item_code": ["in", item_codes],
            "price_list": selected_price_list,
        }
        if "selling" in price_fields:
            price_filters["selling"] = 1

        price_rows = frappe.get_all(
            "Item Price",
            filters=price_filters,
            fields=["item_code", "price_list_rate", "modified"],
            order_by="modified desc",
            limit_page_length=0,
        )
        for row in price_rows:
            code = row.get("item_code")
            if code and code not in price_map:
                price_map[code] = _safe_float(row.get("price_list_rate"), default=0.0)

    model_map = {}
    if frappe.db.exists("DocType", "Item Variant Attribute"):
        model_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={"parent": ["in", item_codes], "attribute": "مدل محصول"},
            fields=["parent", "attribute_value"],
            limit_page_length=0,
        )
        for row in model_rows:
            code = row.get("parent")
            model = _normalize_text(row.get("attribute_value"))
            if code and model and code not in model_map:
                model_map[code] = model

    payload = []
    for row in rows:
        item_code = row.get("name")
        if not item_code:
            continue

        item_name = row.get("item_name") or item_code
        variant_of = row.get("variant_of") or ""
        model_title = model_map.get(item_code) or _extract_model_from_item_name(item_name) or _normalize_text(item_name)
        kind = _guess_kind(variant_of, item_name, item_code)
        route_name = variant_of or item_code
        price_toman = _to_toman(price_map.get(item_code))

        if price_toman <= 0:
            continue

        product_route = _build_product_route(route_name=route_name, kind=kind)
        payload.append(
            {
                "item_code": item_code,
                "title": model_title,
                "model": _normalize_text(variant_of or row.get("item_group") or item_name),
                "image": _normalize_image(row.get("image")),
                "price_toman": price_toman,
                "edition_count": _edition_count_for_item(item_code),
                "detail_route": _build_detail_route(item_code),
                "product_route": product_route,
                "is_fake": 0,
            }
        )

    payload.sort(key=lambda item: (-_safe_int(item.get("price_toman"), default=0), item.get("title") or ""))
    return payload[: max(1, _safe_int(limit, default=12))]


def get_special_edition_payload(requested_customer="", limit=12):
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)
    safe_limit = max(1, min(_safe_int(limit, default=12), 24))

    items = _fetch_special_items(selected_price_list=selected_price_list, limit=safe_limit)
    items = _merge_with_sample_items(items, safe_limit)
    if not items:
        items = [dict(item) for item in SAMPLE_SPECIAL_ITEMS[:safe_limit]]

    total_units = sum(_safe_int(item.get("edition_count"), default=0) for item in items)
    min_price = min((_safe_int(item.get("price_toman"), default=0) for item in items), default=0)
    max_price = max((_safe_int(item.get("price_toman"), default=0) for item in items), default=0)

    return {
        "SpecialEditionHero": {
            "eyebrow": "DENROOM SIGNATURE SERIES",
            "title": "Special Edition",
            "subtitle": "کالکشن نسخه محدود دن‌روم برای فضاهای شاخص و پروژه‌های خاص",
            "note": "هر مدل با تیراژ محدود تولید می‌شود و پس از اتمام ظرفیت، از چرخه سفارش خارج خواهد شد.",
        },
        "SpecialEditionItems": items,
        "SpecialEditionStats": {
            "items_count": len(items),
            "total_units": total_units,
            "price_range": {
                "min": min_price,
                "max": max_price,
            },
        },
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }


def _pick_sample_item(item_code):
    code = _normalize_text(unquote(item_code or ""))
    if code:
        for item in SAMPLE_SPECIAL_ITEMS:
            if _normalize_text(item.get("item_code")) == code:
                return dict(item)
    return dict(SAMPLE_SPECIAL_ITEMS[0]) if SAMPLE_SPECIAL_ITEMS else {}


def _get_item_price(item_code, selected_price_list):
    if not item_code or not selected_price_list or not frappe.db.exists("DocType", "Item Price"):
        return 0
    price_fields = _get_available_fields("Item Price")
    filters = {"item_code": item_code, "price_list": selected_price_list}
    if "selling" in price_fields:
        filters["selling"] = 1
    price_rows = frappe.get_all(
        "Item Price",
        filters=filters,
        fields=["price_list_rate", "modified"],
        order_by="modified desc",
        limit_page_length=1,
    )
    if not price_rows:
        return 0
    return _to_toman(price_rows[0].get("price_list_rate"))


def _get_model_for_item(item_code, item_name):
    model = ""
    if frappe.db.exists("DocType", "Item Variant Attribute"):
        model_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={"parent": item_code, "attribute": "مدل محصول"},
            fields=["attribute_value"],
            limit_page_length=1,
        )
        if model_rows:
            model = _normalize_text(model_rows[0].get("attribute_value"))
    if not model:
        model = _extract_model_from_item_name(item_name)
    return model or _normalize_text(item_name)


def _get_item_attributes(item_code):
    if not item_code or not frappe.db.exists("DocType", "Item Variant Attribute"):
        return []
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": item_code},
        fields=["attribute", "attribute_value"],
        limit_page_length=60,
    )
    black_list = {"رنگ بدنه", "رنگ چوب", "کد پارچه", "کد"}
    attributes = []
    for row in rows:
        label = _normalize_text(row.get("attribute"))
        value = _normalize_text(row.get("attribute_value"))
        if not label or not value:
            continue
        if label in black_list:
            continue
        attributes.append({"label": label, "value": value})
    return attributes[:8]


def _get_item_gallery(item_code, main_image):
    gallery = []
    if main_image:
        gallery.append(_normalize_image(main_image))

    if not item_code:
        return gallery

    try:
        rows = frappe.db.sql(
            """
            SELECT file_url
            FROM `tabFile`
            WHERE
              attached_to_doctype = 'Item'
              AND attached_to_name = %s
              AND is_folder = 0
            ORDER BY modified DESC
            LIMIT 8
            """,
            [item_code],
            as_dict=True,
        )
    except Exception:
        rows = []

    for row in rows:
        image = _normalize_image(row.get("file_url"))
        if image and image not in gallery:
            gallery.append(image)
    return gallery[:6]


def _special_item_detail_from_row(row, selected_price_list):
    item_code = row.get("name")
    item_name = row.get("item_name") or item_code
    variant_of = row.get("variant_of") or ""
    model_title = _get_model_for_item(item_code=item_code, item_name=item_name)
    kind = _guess_kind(variant_of, item_name, item_code)
    route_name = variant_of or item_code
    price_toman = _get_item_price(item_code=item_code, selected_price_list=selected_price_list)
    if price_toman <= 0:
        return None

    edition_count = _edition_count_for_item(item_code)
    image = _normalize_image(row.get("image"))
    return {
        "item_code": item_code,
        "title": model_title,
        "model": _normalize_text(variant_of or row.get("item_group") or item_name),
        "display_name": _normalize_text(item_name),
        "image": image,
        "gallery": _get_item_gallery(item_code=item_code, main_image=image),
        "price_toman": price_toman,
        "edition_count": edition_count,
        "detail_route": _build_detail_route(item_code),
        "product_route": _build_product_route(route_name=route_name, kind=kind),
        "kind": kind,
        "is_fake": 0,
        "attributes": _get_item_attributes(item_code=item_code),
    }


def _build_special_detail_payload(detail_item, selected_customer="", selected_price_list="", price_source="default"):
    title = detail_item.get("title") or "Special Edition"
    model = detail_item.get("model") or ""
    edition_count = _safe_int(detail_item.get("edition_count"), default=0)

    detail_code = detail_item.get("item_code")
    related = _fetch_special_items(selected_price_list=selected_price_list, limit=8)
    related = _merge_with_sample_items(related, limit=8, exclude_codes=[detail_code])
    related = [item for item in related if item.get("item_code") != detail_code][:4]

    return {
        "SpecialEditionDetail": {
            **detail_item,
            "story": f"مدل «{title}» از سری نسخه محدود دن‌روم است که با تمرکز بر جزئیات ساخت، کیفیت متریال و هویت بصری شاخص طراحی شده است.",
            "craft_note": f"این مدل فقط در تیراژ {edition_count} عدد تولید می‌شود و هر سفارش آن با کنترل کیفی اختصاصی آماده‌سازی می‌گردد.",
            "luxury_note": "ساختار این کالکشن برای مشتریانی طراحی شده که به‌دنبال محصول متمایز، کمیاب و سطح‌بالا هستند.",
            "subtitle": model,
        },
        "SpecialEditionRelated": related,
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }


def get_special_edition_detail_payload(item_code="", requested_customer=""):
    requested_code = _normalize_text(unquote(item_code or ""))
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)

    if requested_code and frappe.db.exists("Item", requested_code):
        item_fields = _get_available_fields("Item")
        fields = [f for f in ["name", "item_name", "variant_of", "item_group", "image", "special_edition"] if f in item_fields or f == "name"]
        item_row = frappe.get_all(
            "Item",
            filters={"name": requested_code, "disabled": 0},
            fields=fields,
            limit_page_length=1,
        )
        if item_row and _safe_int(item_row[0].get("special_edition"), default=0) == 1:
            detail_item = _special_item_detail_from_row(item_row[0], selected_price_list=selected_price_list)
            if detail_item:
                return _build_special_detail_payload(
                    detail_item,
                    selected_customer=selected_customer,
                    selected_price_list=selected_price_list,
                    price_source=price_source,
                )

    sample = _pick_sample_item(requested_code)
    if sample:
        detail_item = {
            **sample,
            "display_name": sample.get("title"),
            "gallery": [sample.get("image")],
            "attributes": [],
            "subtitle": sample.get("model"),
            "story": f"مدل «{sample.get('title')}» نمونه نمایشی از کالکشن Special Edition دن‌روم است.",
            "craft_note": f"این نسخه با تیراژ محدود {sample.get('edition_count')} عدد تعریف شده است.",
            "luxury_note": "پس از فعال‌سازی محصولات واقعی، اطلاعات دقیق هر مدل از ERPNext نمایش داده می‌شود.",
        }
        return _build_special_detail_payload(
            detail_item,
            selected_customer=selected_customer,
            selected_price_list=selected_price_list,
            price_source=price_source,
        )

    return {
        "SpecialEditionDetail": {},
        "SpecialEditionRelated": [],
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }
