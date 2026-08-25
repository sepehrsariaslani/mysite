import frappe


def _add_schema_option(schema_map, attr_name, value):
    if not attr_name or value in (None, ""):
        return
    schema_map.setdefault(attr_name, [])
    if value not in schema_map[attr_name]:
        schema_map[attr_name].append(value)


def _normalize_name(value):
    return " ".join(str(value or "").replace("-", " ").split()).strip().lower()


def _find_matching_family(all_models, model_name):
    target = _normalize_name(model_name)
    if not target:
        return []

    family = []
    for row in all_models or []:
        row_name = _normalize_name(row.get("name"))
        if not row_name:
            continue
        if (
            row_name == target
            or row_name.startswith(target)
            or target.startswith(row_name)
            or target in row_name
            or row_name in target
        ):
            family.append(row)
    return family


def get_table_details(model_name, price_list_param):
    from mysite.www.mysite.tables import get_chairs_by_type as get_tables
    all_tables = get_tables("میز ناهارخوری", price_list_param)
    
    # Tables with matching parent model
    family = _find_matching_family(all_tables, model_name)
    if not family:
        from mysite.www.mysite.coffee_tables import get_related_items as get_coffee
        all_coffee = get_coffee(('میز جلومبلی', 'میز عسلی', 'باکس'), price_list_param)
        family = _find_matching_family(all_coffee, model_name)
        if not family:
            return None

    target_name = _normalize_name(model_name)
    target_table = next((t for t in family if _normalize_name(t.get("name")) == target_name), family[0])

    all_wood_colors = set()
    all_body_colors = set()
    all_variants = []
    schema_map = {}

    for t in family:
        for c in t.get("colors", []):
            variant = c.get("variant", {})
            color_name = c.get("name") or c.get("wood_color") or c.get("body_color")
            is_wood = c.get("is_wood")
            dimension = ""
            if variant.get("length") and variant.get("width"):
                dimension = f"{variant.get('length')}x{variant.get('width')}"
            elif variant.get("length"):
                dimension = str(variant.get("length"))

            attributes = {}
            if color_name and is_wood:
                attributes["رنگ چوب"] = color_name
                _add_schema_option(schema_map, "رنگ چوب", color_name)
            if color_name and not is_wood:
                attributes["رنگ بدنه"] = color_name
                _add_schema_option(schema_map, "رنگ بدنه", color_name)
            if dimension:
                attributes["ابعاد"] = dimension
                _add_schema_option(schema_map, "ابعاد", dimension)

            vObj = {
                "item_code": variant.get("item_code"),
                "wood": color_name if is_wood else None,
                "body": color_name if not is_wood else None,
                "body_color": color_name if not is_wood else None,
                "length": variant.get("length", ""),
                "width": variant.get("width", ""),
                "raw_price": variant.get("raw_price", 0) / 10,
                "odd_cloth": t.get("odd_cloth", 0.0),
                "even_cloth": t.get("even_cloth", 0.0),
                "minor_cloth": t.get("minor_cloth", 0.0),
                "image": t.get("image") or "",
                "attributes": attributes
            }
            all_variants.append(vObj)
            if color_name and is_wood:
                all_wood_colors.add(color_name)
            elif color_name:
                all_body_colors.add(color_name)

    item_codes = [v.get("item_code") for v in all_variants if v.get("item_code")]
    if item_codes:
        attr_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={"parent": ["in", item_codes]},
            fields=["parent", "attribute", "attribute_value"],
            ignore_permissions=True,
        )
        ignored_attrs = {"مدل محصول", "رنگ"}
        attrs_by_item = {}
        for row in attr_rows:
            if row.attribute in ignored_attrs or not row.attribute_value:
                continue
            attrs_by_item.setdefault(row.parent, {})[row.attribute] = row.attribute_value
            _add_schema_option(schema_map, row.attribute, row.attribute_value)

        for variant in all_variants:
            code = variant.get("item_code")
            item_attrs = attrs_by_item.get(code, {})
            if item_attrs:
                merged = dict(variant.get("attributes") or {})
                merged.update(item_attrs)
                variant["attributes"] = merged

    selectable_attributes = [{"name": name, "options": options} for name, options in schema_map.items() if options]
    attribute_schema = selectable_attributes

    c_images = [img.get("file_url", "").replace('/private/files/', '/files/') if isinstance(img, dict) else str(img).replace('/private/files/', '/files/') for img in target_table.get("images", [])]

    return {
        "name": target_table["name"],
        "display_name": target_table.get("display_name") or target_table["name"],
        "category_name": "میز",
        "description": target_table.get("description", "محصول مدرن با طراحی ارگونومیک."),
        "price": (target_table.get("colors", [])[0].get("variant", {}).get("raw_price", 0) / 10) if target_table.get("colors") else 0,
        "images": [i for i in c_images if i],
        "all_wood_colors": list(all_wood_colors),
        "all_body_colors": list(all_body_colors),
        "variants": all_variants,
        "attribute_schema": attribute_schema,
        "selectable_attributes": selectable_attributes,
        "type": "table",
        "length": target_table.get("length"),
        "width": target_table.get("width"),
        "height": target_table.get("height"),
        "fabric_needed": target_table.get("odd_cloth", 0.0),
        "odd_cloth": target_table.get("odd_cloth", 0.0),
        "even_cloth": target_table.get("even_cloth", 0.0),
        "minor_cloth": target_table.get("minor_cloth", 0.0),
        "weight": target_table.get("weight")
    }
