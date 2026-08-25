from __future__ import annotations

from urllib.parse import quote, unquote

import frappe

from mysite.www.mysite.special_edition_service import (
    _build_product_route,
    _extract_model_from_item_name,
    _get_available_fields,
    _get_item_attributes,
    _get_item_gallery,
    _get_item_price,
    _get_model_for_item,
    _guess_kind,
    _normalize_image,
    _normalize_text,
    _resolve_customer_price_context,
    _safe_float,
    _safe_int,
    _to_toman,
)


SAMPLE_OUTLET_ITEMS = [
    {
        "item_code": "OUT-SOFA-ROUZAN-01",
        "title": "روژان کلاسیک",
        "model": "مبلمان Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 142000000,
        "outlet_price_toman": 108000000,
        "discount_percent": 24,
        "stock_count": 3,
        "detail_route": "/mysite/outlet/OUT-SOFA-ROUZAN-01",
        "product_route": "/mysite/sofas",
        "is_fake": 1,
    },
    {
        "item_code": "OUT-CHAIR-MAHOUR-02",
        "title": "ماهور مینیمال",
        "model": "صندلی ناهارخوری Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 36000000,
        "outlet_price_toman": 26200000,
        "discount_percent": 27,
        "stock_count": 6,
        "detail_route": "/mysite/outlet/OUT-CHAIR-MAHOUR-02",
        "product_route": "/mysite/dining-chairs",
        "is_fake": 1,
    },
    {
        "item_code": "OUT-BARSTOOL-NOVA-03",
        "title": "نُوا اپن",
        "model": "صندلی اپن Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 29800000,
        "outlet_price_toman": 22400000,
        "discount_percent": 25,
        "stock_count": 8,
        "detail_route": "/mysite/outlet/OUT-BARSTOOL-NOVA-03",
        "product_route": "/mysite/barstools",
        "is_fake": 1,
    },
    {
        "item_code": "OUT-TABLE-AVA-04",
        "title": "آوا ۶ نفره",
        "model": "میز ناهارخوری Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 88000000,
        "outlet_price_toman": 64200000,
        "discount_percent": 27,
        "stock_count": 2,
        "detail_route": "/mysite/outlet/OUT-TABLE-AVA-04",
        "product_route": "/mysite/tables",
        "is_fake": 1,
    },
    {
        "item_code": "OUT-BENCH-SANA-05",
        "title": "سانا",
        "model": "نیمکت Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 26500000,
        "outlet_price_toman": 19800000,
        "discount_percent": 25,
        "stock_count": 5,
        "detail_route": "/mysite/outlet/OUT-BENCH-SANA-05",
        "product_route": "/mysite/benches",
        "is_fake": 1,
    },
    {
        "item_code": "OUT-COFFEE-LUNA-06",
        "title": "لونا",
        "model": "میز جلو مبلی Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 33200000,
        "outlet_price_toman": 24800000,
        "discount_percent": 25,
        "stock_count": 4,
        "detail_route": "/mysite/outlet/OUT-COFFEE-LUNA-06",
        "product_route": "/mysite/coffee-tables",
        "is_fake": 1,
    },
    {
        "item_code": "OUT-SOFA-ARIA-07",
        "title": "آریا",
        "model": "مبلمان Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 126000000,
        "outlet_price_toman": 98600000,
        "discount_percent": 22,
        "stock_count": 2,
        "detail_route": "/mysite/outlet/OUT-SOFA-ARIA-07",
        "product_route": "/mysite/sofas",
        "is_fake": 1,
    },
    {
        "item_code": "OUT-CHAIR-KAJA-08",
        "title": "کاجا",
        "model": "صندلی ناهارخوری Outlet",
        "image": "/assets/mysite/img/placeholder.png",
        "price_toman": 34200000,
        "outlet_price_toman": 26900000,
        "discount_percent": 21,
        "stock_count": 7,
        "detail_route": "/mysite/outlet/OUT-CHAIR-KAJA-08",
        "product_route": "/mysite/dining-chairs",
        "is_fake": 1,
    },
]


def _build_detail_route(item_code):
    return f"/mysite/outlet/{quote(str(item_code))}"


def _clamp_discount(value, default=20):
    discount = _safe_int(value, default=default)
    return max(5, min(discount, 55))


def _estimate_discount(item_code, default=20):
    code = str(item_code or "")
    if not code:
        return default
    seed = sum(ord(ch) for ch in code) % 24
    return 12 + seed


def _stock_count_for_item(item_code):
    code = str(item_code or "")
    seed = sum(ord(ch) for ch in code) % 9
    return 1 + seed


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

    for sample in SAMPLE_OUTLET_ITEMS:
        code = _normalize_text(sample.get("item_code"))
        if not code or code in seen_codes:
            continue
        merged.append(dict(sample))
        seen_codes.add(code)
        if len(merged) >= safe_limit:
            break

    return merged


def _fetch_outlet_items(selected_price_list, limit):
    item_fields = _get_available_fields("Item")
    if "outlet_product" not in item_fields:
        return []

    filters = {"outlet_product": 1}
    if "disabled" in item_fields:
        filters["disabled"] = 0
    if "show_on_site" in item_fields:
        filters["show_on_site"] = 1
    elif "show_in_website" in item_fields:
        filters["show_in_website"] = 1
    if "is_sales_item" in item_fields:
        filters["is_sales_item"] = 1

    requested_fields = ["name", "item_name", "variant_of", "item_group", "image", "modified"]
    if "outlet_discount_percent" in item_fields:
        requested_fields.append("outlet_discount_percent")
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
        price_filters = {"item_code": ["in", item_codes], "price_list": selected_price_list}
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

        base_price = _to_toman(price_map.get(item_code))
        if base_price <= 0:
            continue

        discount_percent = _clamp_discount(
            row.get("outlet_discount_percent"),
            default=_estimate_discount(item_code, default=20),
        )
        outlet_price = int(round(base_price * (100 - discount_percent) / 100.0))
        if outlet_price <= 0:
            continue

        payload.append(
            {
                "item_code": item_code,
                "title": model_title,
                "model": _normalize_text(variant_of or row.get("item_group") or item_name),
                "image": _normalize_image(row.get("image")),
                "price_toman": base_price,
                "outlet_price_toman": outlet_price,
                "discount_percent": discount_percent,
                "stock_count": _stock_count_for_item(item_code),
                "detail_route": _build_detail_route(item_code),
                "product_route": _build_product_route(route_name=route_name, kind=kind),
                "is_fake": 0,
            }
        )

    payload.sort(
        key=lambda item: (
            -_safe_int(item.get("discount_percent"), default=0),
            _safe_int(item.get("outlet_price_toman"), default=10**10),
            item.get("title") or "",
        )
    )
    return payload[: max(1, _safe_int(limit, default=12))]


def get_outlet_payload(requested_customer="", limit=12):
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)
    safe_limit = max(1, min(_safe_int(limit, default=12), 24))

    items = _fetch_outlet_items(selected_price_list=selected_price_list, limit=safe_limit)
    items = _merge_with_sample_items(items, safe_limit)
    if not items:
        items = [dict(item) for item in SAMPLE_OUTLET_ITEMS[:safe_limit]]

    total_stock = sum(_safe_int(item.get("stock_count"), default=0) for item in items)
    best_discount = max((_safe_int(item.get("discount_percent"), default=0) for item in items), default=0)

    return {
        "OutletHero": {
            "eyebrow": "DENROOM OUTLET SELECTION",
            "title": "Outlet",
            "subtitle": "محصولات منتخب دن‌روم با قیمت ویژه و موجودی محدود",
            "note": "محصولات Outlet تا زمان تکمیل موجودی قابل سفارش هستند و با قیمت نهایی ویژه عرضه می‌شوند.",
        },
        "OutletItems": items,
        "OutletStats": {
            "items_count": len(items),
            "total_stock": total_stock,
            "best_discount": best_discount,
        },
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }


def _pick_sample_item(item_code):
    code = _normalize_text(unquote(item_code or ""))
    if code:
        for item in SAMPLE_OUTLET_ITEMS:
            if _normalize_text(item.get("item_code")) == code:
                return dict(item)
    return dict(SAMPLE_OUTLET_ITEMS[0]) if SAMPLE_OUTLET_ITEMS else {}


def _outlet_item_detail_from_row(row, selected_price_list):
    item_code = row.get("name")
    item_name = row.get("item_name") or item_code
    variant_of = row.get("variant_of") or ""
    model_title = _get_model_for_item(item_code=item_code, item_name=item_name)
    kind = _guess_kind(variant_of, item_name, item_code)
    route_name = variant_of or item_code
    base_price = _get_item_price(item_code=item_code, selected_price_list=selected_price_list)
    if base_price <= 0:
        return None

    discount_percent = _clamp_discount(
        row.get("outlet_discount_percent"),
        default=_estimate_discount(item_code, default=20),
    )
    outlet_price = int(round(base_price * (100 - discount_percent) / 100.0))
    if outlet_price <= 0:
        return None

    image = _normalize_image(row.get("image"))
    return {
        "item_code": item_code,
        "title": model_title,
        "model": _normalize_text(variant_of or row.get("item_group") or item_name),
        "display_name": _normalize_text(item_name),
        "image": image,
        "gallery": _get_item_gallery(item_code=item_code, main_image=image),
        "price_toman": base_price,
        "outlet_price_toman": outlet_price,
        "discount_percent": discount_percent,
        "stock_count": _stock_count_for_item(item_code),
        "detail_route": _build_detail_route(item_code),
        "product_route": _build_product_route(route_name=route_name, kind=kind),
        "kind": kind,
        "is_fake": 0,
        "attributes": _get_item_attributes(item_code=item_code),
    }


def _build_outlet_detail_payload(detail_item, selected_customer="", selected_price_list="", price_source="default"):
    title = detail_item.get("title") or "Outlet"
    model = detail_item.get("model") or ""
    stock_count = _safe_int(detail_item.get("stock_count"), default=0)
    discount_percent = _safe_int(detail_item.get("discount_percent"), default=0)

    detail_code = detail_item.get("item_code")
    related = _fetch_outlet_items(selected_price_list=selected_price_list, limit=8)
    related = _merge_with_sample_items(related, limit=8, exclude_codes=[detail_code])
    related = [item for item in related if item.get("item_code") != detail_code][:4]

    return {
        "OutletDetail": {
            **detail_item,
            "story": f"مدل «{title}» در بخش Outlet دن‌روم با شرایط قیمت ویژه ارائه می‌شود.",
            "craft_note": f"این آیتم با تخفیف {discount_percent}٪ و موجودی فعلی {stock_count} عدد قابل سفارش است.",
            "luxury_note": "همه محصولات Outlet از نظر سلامت فنی بررسی شده‌اند و آماده ارسال هستند.",
            "subtitle": model,
        },
        "OutletRelated": related,
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }


def get_outlet_detail_payload(item_code="", requested_customer=""):
    requested_code = _normalize_text(unquote(item_code or ""))
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)

    if requested_code and frappe.db.exists("Item", requested_code):
        item_fields = _get_available_fields("Item")
        fields = [
            f
            for f in ["name", "item_name", "variant_of", "item_group", "image", "outlet_product", "outlet_discount_percent"]
            if f in item_fields or f == "name"
        ]
        item_row = frappe.get_all(
            "Item",
            filters={"name": requested_code, "disabled": 0},
            fields=fields,
            limit_page_length=1,
        )
        if item_row and _safe_int(item_row[0].get("outlet_product"), default=0) == 1:
            detail_item = _outlet_item_detail_from_row(item_row[0], selected_price_list=selected_price_list)
            if detail_item:
                return _build_outlet_detail_payload(
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
            "story": f"مدل «{sample.get('title')}» نمونه نمایشی از کالکشن Outlet دن‌روم است.",
            "craft_note": f"این آیتم در Outlet با تخفیف {sample.get('discount_percent')}٪ عرضه می‌شود.",
            "luxury_note": "پس از فعال‌سازی محصولات واقعی، اطلاعات دقیق هر محصول از ERPNext نمایش داده می‌شود.",
        }
        return _build_outlet_detail_payload(
            detail_item,
            selected_customer=selected_customer,
            selected_price_list=selected_price_list,
            price_source=price_source,
        )

    return {
        "OutletDetail": {},
        "OutletRelated": [],
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }
