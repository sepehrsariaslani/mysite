import frappe


def _add_schema_option(schema_map, attr_name, value):
    if not attr_name or value in (None, ""):
        return
    schema_map.setdefault(attr_name, [])
    if value not in schema_map[attr_name]:
        schema_map[attr_name].append(value)


def get_bench_details(model_name, price_list_param):
    from mysite.www.mysite.benches import get_related_items as get_benches
    all_benches = get_benches(('نیمکت', 'پاف'), price_list_param)
    
    target = next((c for c in all_benches if c.get("name").lower() == model_name.lower()), None)
    if not target: return None

    all_wood_colors = set()
    all_body_colors = set()
    all_variants = []
    schema_map = {}
    source_images = target.get("images") or []
    if not source_images and target.get("image"):
        source_images = [target.get("image")]
    first_image = None
    if source_images:
        img = source_images[0]
        first_image = img.get("file_url", "").replace('/private/files/', '/files/') if isinstance(img, dict) else str(img).replace('/private/files/', '/files/')

    for c in target.get("colors", []):
        variant = c.get("variant", {})
        if c.get("wood_color"): all_wood_colors.add(c.get("wood_color"))
        if c.get("body_color"): all_body_colors.add(c.get("body_color"))

        attributes = {}
        if c.get("wood_color"):
            attributes["رنگ چوب"] = c.get("wood_color")
            _add_schema_option(schema_map, "رنگ چوب", c.get("wood_color"))
        if c.get("body_color"):
            attributes["رنگ بدنه"] = c.get("body_color")
            _add_schema_option(schema_map, "رنگ بدنه", c.get("body_color"))

        all_variants.append({
            "item_code": variant.get("item_code"),
            "wood": c.get("wood_color"),
            "body": c.get("body_color"),
            "body_color": c.get("body_color"),
            "raw_price": variant.get("raw_price", 0) / 10,
            "odd_cloth": target.get("odd_cloth", 0.0),
            "even_cloth": target.get("even_cloth", 0.0),
            "minor_cloth": target.get("minor_cloth", 0.0),
            "image": first_image or "",
            "attributes": attributes
        })

    attribute_schema = [{"name": name, "options": options} for name, options in schema_map.items() if options]
    selectable_attributes = attribute_schema

    c_images = [img.get("file_url", "").replace('/private/files/', '/files/') if isinstance(img, dict) else str(img).replace('/private/files/', '/files/') for img in source_images]
    if not c_images and target.get("image"):
        c_images = [str(target.get("image")).replace('/private/files/', '/files/')]

    return {
        "name": target["name"],
        "display_name": target.get("display_name") or target["name"],
        "category_name": "نیمکت و پاف",
        "description": "طراحی مدرن و راحت.",
        "price": (target.get("colors", [])[0].get("variant", {}).get("raw_price", 0) / 10) if target.get("colors") else 0,
        "images": [i for i in c_images if i],
        "all_wood_colors": list(all_wood_colors),
        "all_body_colors": list(all_body_colors),
        "variants": all_variants,
        "attribute_schema": attribute_schema,
        "selectable_attributes": selectable_attributes,
        "type": "bench",
        "length": target.get("length"),
        "width": target.get("width"),
        "height": target.get("height"),
        "fabric_needed": target.get("odd_cloth", 0.0),
        "odd_cloth": target.get("odd_cloth", 0.0),
        "even_cloth": target.get("even_cloth", 0.0),
        "minor_cloth": target.get("minor_cloth", 0.0),
        "weight": target.get("weight")
    }
