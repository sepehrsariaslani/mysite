import frappe


def _add_schema_option(schema_map, attr_name, value):
    if not attr_name or value in (None, ""):
        return
    schema_map.setdefault(attr_name, [])
    if value not in schema_map[attr_name]:
        schema_map[attr_name].append(value)


def _normalize_name(value):
    return " ".join((value or "").replace("-", " ").split()).strip().lower()


def _has_any_keyword(text, keywords):
    return any(k in text for k in keywords)


def _find_best_chair_match(all_chairs, model_name):
    target = _normalize_name(model_name)
    if not target:
        return None

    non_chair_keywords = ("مبل", "کاناپه", "نیمکت", "پاف", "میز", "جلومبلی", "عسلی", "باکس", "سرویس خواب")
    if _has_any_keyword(target, non_chair_keywords):
        return None

    exact = next((c for c in all_chairs if _normalize_name(c.get("name")) == target), None)
    if exact:
        return exact

    chair_keywords = ("صندلی", "اپن", "ناهارخوری")
    for c in all_chairs:
        normalized_name = _normalize_name(c.get("name"))
        if not normalized_name:
            continue
        if normalized_name in target or target in normalized_name:
            # Keep fallback fuzzy match only when chair intent is likely.
            if _has_any_keyword(target, chair_keywords) or _has_any_keyword(normalized_name, chair_keywords):
                return c

    tokens = target.split()
    if not _has_any_keyword(target, chair_keywords):
        return None
    while len(tokens) > 2:
        tokens.pop()
        partial = " ".join(tokens)
        candidate = next((c for c in all_chairs if partial in _normalize_name(c.get("name"))), None)
        if candidate:
            return candidate
    return None


def get_chair_details(model_name, price_list_param):
    from mysite.www.dining_chairs import get_chairs_by_type as get_dining_chairs
    all_chairs = get_dining_chairs("صندلی ناهارخوری", price_list_param)
    
    target = _find_best_chair_match(all_chairs, model_name)
    if not target: return None

    all_wood_colors = set()
    all_body_colors = set()
    all_variants = []
    schema_map = {}
    first_image = None
    if target.get("images"):
        img = target.get("images")[0]
        first_image = img.get("file_url", "").replace('/private/files/', '/files/') if isinstance(img, dict) else str(img).replace('/private/files/', '/files/')

    for c in target.get("colors", []):
        variant = c.get("variant", {})
        clr_name = c.get("name")
        is_wood = c.get("is_wood")
        
        if is_wood: all_wood_colors.add(clr_name)
        else: all_body_colors.add(clr_name)
        
        attributes = {}
        if is_wood and clr_name:
            attributes["رنگ چوب"] = clr_name
            _add_schema_option(schema_map, "رنگ چوب", clr_name)
        if (not is_wood) and clr_name:
            attributes["رنگ بدنه"] = clr_name
            _add_schema_option(schema_map, "رنگ بدنه", clr_name)

        all_variants.append({
            "item_code": variant.get("item_code"),
            "wood": clr_name if is_wood else None,
            "body": clr_name if not is_wood else None,
            "body_color": clr_name if not is_wood else None,
            "raw_price": variant.get("raw_price", 0) / 10,
            "odd_cloth": target.get("odd_cloth", 0.0),
            "even_cloth": target.get("even_cloth", 0.0),
            "minor_cloth": target.get("minor_cloth", 0.0),
            "image": first_image or "",
            "attributes": attributes
        })

    attribute_schema = [{"name": name, "options": options} for name, options in schema_map.items() if options]
    selectable_attributes = attribute_schema

    c_images = [img.get("file_url", "").replace('/private/files/', '/files/') if isinstance(img, dict) else str(img).replace('/private/files/', '/files/') for img in target.get("images", [])]

    return {
        "name": target["name"],
        "display_name": target.get("display_name") or target["name"],
        "category_name": "صندلی",
        "description": "صندلی ناهارخوری با طراحی ارگونومیک.",
        "price": (target.get("colors", [])[0].get("variant", {}).get("raw_price", 0) / 10) if target.get("colors") else 0,
        "images": [i for i in c_images if i],
        "all_wood_colors": list(all_wood_colors),
        "all_body_colors": list(all_body_colors),
        "variants": all_variants,
        "attribute_schema": attribute_schema,
        "selectable_attributes": selectable_attributes,
        "type": "chair",
        "length": target.get("length"),
        "width": target.get("width"),
        "height": target.get("height"),
        "fabric_needed": bool(target.get("odd_cloth", 0) or target.get("minor_cloth", 0)),
        "odd_cloth": target.get("odd_cloth", 0.0),
        "even_cloth": target.get("even_cloth", 0.0),
        "minor_cloth": target.get("minor_cloth", 0.0),
        "weight": target.get("weight")
    }
