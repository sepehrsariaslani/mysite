import re
import frappe


def _add_schema_option(schema_map, attr_name, value):
    if not attr_name or value in (None, ""):
        return
    value = str(value).strip()
    if not value:
        return
    schema_map.setdefault(attr_name, [])
    if value not in schema_map[attr_name]:
        schema_map[attr_name].append(value)


def _normalize_digits(value):
    return str(value or "").translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))


def _to_persian_digits(value):
    txt = str(value or "")
    return txt.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def _normalize_name(value):
    return " ".join((value or "").replace("-", " ").split()).strip().lower()


def _extract_height_from_text(text):
    source = _normalize_digits(text)
    if not source:
        return ""
    match = re.search(r"ارتفاع\s*[:\-]?\s*([0-9]+(?:[./][0-9]+)?)", source)
    if not match:
        match = re.search(r"([0-9]{2,3}(?:[./][0-9]+)?)\s*(?:سانتی\s*متر|سانت|سم)\b", source)
    if not match:
        return ""
    number = match.group(1).replace("/", ".").strip()
    if number.endswith(".0"):
        number = number[:-2]
    if not number:
        return ""
    return f"ارتفاع {_to_persian_digits(number)} سانتی متر"


def _pick_attr(attrs, preferred_names):
    for name in preferred_names:
        value = attrs.get(name)
        if value not in (None, ""):
            return str(value).strip()
    for attr_name, attr_value in attrs.items():
        if any(token in str(attr_name or "") for token in preferred_names):
            txt = str(attr_value or "").strip()
            if txt:
                return txt
    return ""


def _height_sort_key(value):
    normalized = _normalize_digits(value)
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", normalized)
    if match:
        try:
            return (0, float(match.group(1)))
        except Exception:
            pass
    return (1, normalized)


def _normalize_spaces(value):
    return " ".join(str(value or "").replace("\u200c", " ").split()).strip()


def _short_height_label(height_value):
    normalized = _normalize_digits(height_value)
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", normalized)
    if not match:
        return ""
    number = match.group(1)
    if number.endswith(".0"):
        number = number[:-2]
    return f"ارتفاع {_to_persian_digits(number)}"


def _build_barstool_variant_title(model_name, body_color, height_value):
    model = _normalize_spaces(model_name)
    color = _normalize_spaces(body_color)
    height = _short_height_label(height_value)
    parts = ["صندلی اپن", model, color, height]
    return _normalize_spaces(" ".join(p for p in parts if p))


def _lookup_price_by_variant_title(title, price_list_name):
    if not title or not price_list_name:
        return "", 0

    normalized_title = _normalize_spaces(title)
    candidate_code = frappe.db.get_value("Item", {"name": normalized_title}, "name")
    if not candidate_code:
        candidate_code = frappe.db.get_value("Item", {"item_name": normalized_title}, "name")
    if not candidate_code:
        return "", 0

    price_rate = frappe.db.get_value(
        "Item Price",
        {"item_code": candidate_code, "price_list": price_list_name},
        "price_list_rate",
    )
    return candidate_code, float(price_rate or 0)


def get_barstool_details(model_name, price_list_param):
    from mysite.www.mysite.barstools import get_chairs_by_type as get_barstools
    all_barstools = get_barstools("صندلی اپن", price_list_param)
    
    # We want to gather all heights for the same base model (e.g. Model A 60cm vs Model A 70cm)
    base_model = model_name
    # Strip dimensions out if present in URL
    if "سانتی متر" in model_name:
        base_model = model_name.split("سانتی متر")[0].strip()
    elif "سم" in model_name:
        base_model = model_name.split("سم")[0].strip()

    base_model_norm = _normalize_name(base_model)
    family = [
        b for b in all_barstools
        if base_model_norm in _normalize_name(b.get("name")) or _normalize_name(b.get("name")) in base_model_norm
    ]
    if not family: return None
    
    target_norm = _normalize_name(model_name)
    target = next((b for b in family if _normalize_name(b.get("name")) == target_norm), family[0])

    all_wood_colors = set()
    all_body_colors = set()
    all_heights = set()
    all_variants = []
    schema_map = {}
    color_hint_by_item = {}

    # Keep family colors as a fallback for cases where variant attributes are incomplete.
    for f in family:
        for c in f.get("colors", []):
            variant = c.get("variant", {}) or {}
            item_code = variant.get("item_code")
            if not item_code:
                continue
            color_hint_by_item[item_code] = {
                "name": c.get("name"),
                "is_wood": bool(c.get("is_wood")),
                "odd_cloth": f.get("odd_cloth", 0.0),
                "even_cloth": f.get("even_cloth", 0.0),
                "minor_cloth": f.get("minor_cloth", 0.0),
                "image": f.get("image") or "",
            }

    family_model_names = [f.get("name") for f in family if f.get("name")]
    item_codes = []
    if family_model_names:
        model_variant_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={
                "attribute": "مدل محصول",
                "attribute_value": ["in", family_model_names],
            },
            fields=["parent"],
            ignore_permissions=True,
        )
        item_codes.extend(row.parent for row in model_variant_rows if row.parent)

    item_codes.extend(color_hint_by_item.keys())
    item_codes = list(dict.fromkeys(item_codes))

    attrs_by_item = {}
    if item_codes:
        attr_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={"parent": ["in", item_codes]},
            fields=["parent", "attribute", "attribute_value"],
            ignore_permissions=True,
        )
        for row in attr_rows:
            if row.attribute_value in (None, ""):
                continue
            attrs_by_item.setdefault(row.parent, {})[row.attribute] = str(row.attribute_value).strip()

    item_details_map = {}
    if item_codes:
        item_rows = frappe.get_all(
            "Item",
            filters={"name": ["in", item_codes], "show_on_site": 1},
            fields=["name", "item_code", "item_name", "image", "odd_cloth", "even_cloth", "minor_cloth"],
            ignore_permissions=True,
        )
        for row in item_rows:
            item_details_map[row.name] = row

    prices_by_item = {}
    if item_codes and price_list_param:
        price_rows = frappe.get_all(
            "Item Price",
            filters={"item_code": ["in", item_codes], "price_list": price_list_param},
            fields=["item_code", "price_list_rate"],
            ignore_permissions=True,
        )
        for row in price_rows:
            prices_by_item[row.item_code] = float(row.price_list_rate or 0)

    seen_variants = set()
    title_price_cache = {}
    for item_code in item_codes:
        item_doc = item_details_map.get(item_code)
        if not item_doc:
            continue

        attrs = dict(attrs_by_item.get(item_code) or {})
        fallback = color_hint_by_item.get(item_code, {})
        item_name_blob = f"{item_doc.item_name or ''} {item_doc.item_code or ''}"
        category_attr = _pick_attr(attrs, ("دسته محصول",))
        if "خدمات" in item_name_blob or "کلاف" in item_name_blob:
            continue
        if "صندلی اپن" not in item_name_blob and category_attr != "صندلی اپن":
            continue

        wood_color = _pick_attr(attrs, ("رنگ چوب",)) or (fallback.get("name") if fallback.get("is_wood") else "")
        body_color = _pick_attr(attrs, ("رنگ بدنه", "رنگ")) or (fallback.get("name") if not fallback.get("is_wood") else "")
        height_str = _pick_attr(attrs, ("ارتفاع",))
        if not height_str:
            height_str = _extract_height_from_text((item_doc.item_name if item_doc else "") or item_code)

        if not wood_color and not body_color:
            continue

        attributes = {}
        if wood_color:
            attributes["رنگ چوب"] = wood_color
            all_wood_colors.add(wood_color)
            _add_schema_option(schema_map, "رنگ چوب", wood_color)
        if body_color:
            attributes["رنگ بدنه"] = body_color
            all_body_colors.add(body_color)
            _add_schema_option(schema_map, "رنگ بدنه", body_color)
        if height_str:
            attributes["ارتفاع"] = height_str
            all_heights.add(height_str)
            _add_schema_option(schema_map, "ارتفاع", height_str)

        key = tuple(sorted(attributes.items()))
        if key in seen_variants:
            continue
        seen_variants.add(key)

        raw_price_rial = prices_by_item.get(item_code, 0)
        resolved_item_code = item_code
        variant_title = ""

        if body_color and height_str:
            variant_title = _build_barstool_variant_title(target.get("name"), body_color, height_str)
            if variant_title in title_price_cache:
                cached_code, cached_price = title_price_cache[variant_title]
            else:
                cached_code, cached_price = _lookup_price_by_variant_title(variant_title, price_list_param)
                title_price_cache[variant_title] = (cached_code, cached_price)

            if cached_code:
                resolved_item_code = cached_code
            if not raw_price_rial and cached_price:
                raw_price_rial = cached_price

        all_variants.append({
            "item_code": resolved_item_code,
            "wood": wood_color or None,
            "body": body_color or None,
            "body_color": body_color or None,
            "height": height_str,
            "variant_title": variant_title,
            "raw_price": raw_price_rial / 10,
            "odd_cloth": float((item_doc.odd_cloth if item_doc else 0) or fallback.get("odd_cloth", 0.0) or 0.0),
            "even_cloth": float((item_doc.even_cloth if item_doc else 0) or fallback.get("even_cloth", 0.0) or 0.0),
            "minor_cloth": float((item_doc.minor_cloth if item_doc else 0) or fallback.get("minor_cloth", 0.0) or 0.0),
            "image": (item_doc.image if item_doc and item_doc.image else fallback.get("image") or "").replace('/private/files/', '/files/'),
            "attributes": attributes
        })

    attr_order = {
        "رنگ چوب": 1,
        "رنگ بدنه": 2,
        "ارتفاع": 3,
    }
    attribute_schema = [{"name": name, "options": options} for name, options in schema_map.items() if options]
    attribute_schema.sort(key=lambda item_obj: attr_order.get(item_obj.get("name"), 50))
    selectable_attributes = attribute_schema

    c_images = [img.get("file_url", "").replace('/private/files/', '/files/') if isinstance(img, dict) else str(img).replace('/private/files/', '/files/') for img in target.get("images", [])]
    if not c_images and target.get("image"):
        c_images = [str(target.get("image")).replace('/private/files/', '/files/')]

    sorted_heights = sorted([h for h in all_heights if h], key=_height_sort_key)
    main_height = sorted_heights[0] if sorted_heights else (target.get("height") or "")
    default_price = next((v.get("raw_price") for v in all_variants if v.get("raw_price")), 0)

    return {
        "name": target["name"],
        "display_name": target.get("display_name") or target["name"],
        "category_name": "صندلی اپن",
        "description": "صندلی اپن با ارتفاع مختلف.",
        "price": default_price,
        "images": [i for i in c_images if i],
        "all_wood_colors": sorted(all_wood_colors),
        "all_body_colors": sorted(all_body_colors),
        "all_heights": sorted_heights,
        "variants": all_variants,
        "attribute_schema": attribute_schema,
        "selectable_attributes": selectable_attributes,
        "type": "barstool",
        "length": target.get("length"),
        "width": target.get("width"),
        "height": main_height,
        "fabric_needed": bool(target.get("odd_cloth", 0) or target.get("minor_cloth", 0)),
        "odd_cloth": target.get("odd_cloth", 0.0),
        "even_cloth": target.get("even_cloth", 0.0),
        "minor_cloth": target.get("minor_cloth", 0.0),
        "weight": target.get("weight")
    }
