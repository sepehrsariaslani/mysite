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


def _normalize_name(value):
    return " ".join((value or "").replace("-", " ").split()).strip().lower()


def _normalize_digits(value):
    txt = str(value or "")
    return txt.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))


def _is_meaningful_value(value):
    txt = str(value or "").strip()
    if not txt:
        return False
    if txt.lower() in {"none", "null", "nan"}:
        return False
    normalized = _normalize_digits(txt).replace(",", "")
    try:
        return float(normalized) > 0
    except Exception:
        return True


def get_sofa_unit_details(model_name, price_list_param):
    from mysite.www.mysite.sofas import get_nested_sofa_products
    all_models = get_nested_sofa_products(price_list_param)
    url_clean = _normalize_name(model_name)
    sofa_hints = ("مبل", "کاناپه", "ال", "اکسنت")
    has_sofa_hint = any(h in url_clean for h in sofa_hints)
    
    for model in all_models:
        for mod in model.get("sofa_modules", []):
            module_name_raw = mod.get("sofa_module_name", "")
            mod_clean = _normalize_name(module_name_raw)

            # If the URL matches the module name, we pick the first item of that module as default
            for item in mod.get("sofa_module_items", []):
                item_name_clean = _normalize_name(item.get("item_name", ""))
                is_exact = item_name_clean == url_clean or mod_clean == url_clean
                is_safe_fuzzy = (
                    has_sofa_hint
                    and len(url_clean.split()) >= 3
                    and (
                        (item_name_clean and (item_name_clean in url_clean or url_clean in item_name_clean))
                        or (mod_clean and (mod_clean in url_clean or url_clean in mod_clean))
                    )
                )
                if (
                    is_exact
                    or is_safe_fuzzy
                ):
                    # Found the target module. Build full variant matrix for this module,
                    # including same-name module rows (different feature/dimensions).
                    candidate_modules = [mod]
                    for candidate in model.get("sofa_modules", []):
                        if candidate is mod:
                            continue
                        if _normalize_name(candidate.get("sofa_module_name", "")) == mod_clean:
                            candidate_modules.append(candidate)

                    all_wood_colors = set()
                    all_body_colors = set()
                    all_variants = []
                    schema_map = {}
                    seen_variant_keys = set()
                    collected_images = []

                    for candidate_mod in candidate_modules:
                        for module_item in candidate_mod.get("sofa_module_items", []):
                            wood_options = module_item.get("all_wood_colors") or []
                            if not wood_options:
                                wood_options = [""]

                            feature = module_item.get("module_feature")
                            length_val = module_item.get("module_length")
                            width_val = module_item.get("module_width")
                            height_val = module_item.get("module_height")
                            diameter_val = module_item.get("module_diameter")
                            shape_val = module_item.get("module_shape")
                            body = module_item.get("body_color")
                            item_code = module_item.get("item_code") or module_item.get("item_name")
                            normalized_img = (module_item.get("image") or "").replace('/private/files/', '/files/')
                            if normalized_img and normalized_img not in collected_images:
                                collected_images.append(normalized_img)

                            for wood in wood_options:
                                variant_key = (
                                    item_code or "",
                                    wood or "",
                                    body or "",
                                    str(feature or "").strip(),
                                    str(length_val or "").strip(),
                                    str(width_val or "").strip(),
                                    str(height_val or "").strip(),
                                    str(diameter_val or "").strip(),
                                    str(shape_val or "").strip(),
                                )
                                if variant_key in seen_variant_keys:
                                    continue
                                seen_variant_keys.add(variant_key)

                                attributes = {}
                                if wood:
                                    attributes["رنگ چوب"] = wood
                                    _add_schema_option(schema_map, "رنگ چوب", wood)
                                    all_wood_colors.add(wood)

                                if body:
                                    attributes["رنگ بدنه"] = body
                                    _add_schema_option(schema_map, "رنگ بدنه", body)
                                    all_body_colors.add(body)

                                if feature:
                                    attributes["ویژگی ماژول"] = feature
                                    _add_schema_option(schema_map, "ویژگی ماژول", feature)

                                if _is_meaningful_value(length_val):
                                    attributes["طول"] = str(length_val).strip()
                                    _add_schema_option(schema_map, "طول", str(length_val).strip())

                                if _is_meaningful_value(width_val):
                                    attributes["عرض"] = str(width_val).strip()
                                    _add_schema_option(schema_map, "عرض", str(width_val).strip())

                                if _is_meaningful_value(height_val):
                                    attributes["ارتفاع"] = str(height_val).strip()
                                    _add_schema_option(schema_map, "ارتفاع", str(height_val).strip())

                                if _is_meaningful_value(diameter_val):
                                    attributes["قطر"] = str(diameter_val).strip()
                                    _add_schema_option(schema_map, "قطر", str(diameter_val).strip())

                                if shape_val:
                                    attributes["شکل"] = str(shape_val).strip()
                                    _add_schema_option(schema_map, "شکل", str(shape_val).strip())

                                all_variants.append({
                                    "item_name": module_item.get("item_name") or module_item.get("display_name") or item_code,
                                    "item_code": item_code,
                                    "module_name": candidate_mod.get("sofa_module_name"),
                                    "wood": wood or None,
                                    "body": body or None,
                                    "body_color": body or None,
                                    "module_feature": feature or None,
                                    "module_length": str(length_val).strip() if _is_meaningful_value(length_val) else None,
                                    "module_width": str(width_val).strip() if _is_meaningful_value(width_val) else None,
                                    "module_height": str(height_val).strip() if _is_meaningful_value(height_val) else None,
                                    "module_diameter": str(diameter_val).strip() if _is_meaningful_value(diameter_val) else None,
                                    "module_shape": str(shape_val).strip() if shape_val else None,
                                    "raw_price": module_item.get("Price", 0),
                                    "odd_cloth": candidate_mod.get("sofa_odd_cloth", 0.0),
                                    "even_cloth": candidate_mod.get("sofa_even_cloth", 0.0),
                                    "minor_cloth": candidate_mod.get("sofa_minor_cloth", 0.0),
                                    "image": normalized_img,
                                    "attributes": attributes,
                                })

                    attr_order = {
                        "رنگ چوب": 1,
                        "رنگ بدنه": 2,
                        "ویژگی ماژول": 3,
                        "طول": 4,
                        "عرض": 5,
                        "ارتفاع": 6,
                        "قطر": 7,
                        "شکل": 8,
                    }
                    selectable_attributes = [{"name": name, "options": options} for name, options in schema_map.items() if options]
                    selectable_attributes.sort(key=lambda item_obj: attr_order.get(item_obj.get("name"), 100))
                    attribute_schema = selectable_attributes

                    main_img = (item.get("image") or "").replace('/private/files/', '/files/')
                    images = [main_img] if main_img else []
                    for img_url in collected_images:
                        if img_url and img_url not in images:
                            images.append(img_url)

                    return {
                        "name": item.get("item_name"),
                        "item_code": item.get("item_code") or item.get("item_name"),
                        "display_name": item.get("display_name") or item.get("item_name"),
                        "category_name": "مبل",
                        "description": item.get("description", "یک انتخاب عالی برای دکوراسیون شما."),
                        "price": item.get("Price", 0),
                        "images": images,
                        "all_wood_colors": list(all_wood_colors),
                        "all_body_colors": list(all_body_colors),
                        "variants": all_variants,
                        "attribute_schema": attribute_schema,
                        "selectable_attributes": selectable_attributes,
                        "type": "sofa-unit",
                        "module": mod.get("sofa_module_name"),
                        "parent_model_name": model.get("sofa_model_name"),
                        "parent_model_route": f"product/{model.get('sofa_model_name')}",
                        "parent_sofa_modules": model.get("sofa_modules"),
                        "fabric_needed": mod.get("sofa_odd_cloth", 0.0),
                        "odd_cloth": mod.get("sofa_odd_cloth", 0.0),
                        "even_cloth": mod.get("sofa_even_cloth", 0.0),
                        "minor_cloth": mod.get("sofa_minor_cloth", 0.0),
                        "length": item.get("sofa_length", ""),
                        "width": item.get("sofa_width", ""),
                        "height": item.get("sofa_height", "")
                    }
    return None

def get_sofa_collection_details(model_name, price_list_param):
    from mysite.www.mysite.sofas import get_nested_sofa_products
    all_models = get_nested_sofa_products(price_list_param)
    target_norm = _normalize_name(model_name)
    target_model = next(
        (m for m in all_models if _normalize_name(m.get("sofa_model_name")) == target_norm),
        None
    )
    if not target_model:
        target_model = next(
            (
                m for m in all_models
                if _normalize_name(m.get("sofa_model_name")) in target_norm
                or target_norm in _normalize_name(m.get("sofa_model_name"))
            ),
            None
        )
    
    if target_model:
        all_woods = set()
        for mod in target_model.get("sofa_modules", []):
            for item in mod.get("sofa_module_items", []):
                for wood in item.get("all_wood_colors", []):
                    all_woods.add(wood)

        main_img = (target_model.get("sofa_main_photo") or "").replace('/private/files/', '/files/')
        other_imgs = [img.get("file_url", "").replace('/private/files/', '/files/') for img in target_model.get("sofa_images", [])]
        images = ([main_img] if main_img else []) + [i for i in other_imgs if i]

        return {
            "name": target_model["sofa_model_name"],
            "category_name": "مجموعه مبلمان",
            "description": target_model.get("sofa_model_description") or "تجربه‌ای نوین از راحتی و زیبایی در دکوراسیون منزل شما.",
            "images": images,
            "modules": target_model.get("sofa_modules", []),
            "bundles": target_model.get("sofa_bundles", []),
            "sofa_modules": target_model.get("sofa_modules", []),
            "sofa_bundles": target_model.get("sofa_bundles", []),
            "all_wood_colors": list(all_woods),
            "type": "sofa-collection"
        }
    return None
