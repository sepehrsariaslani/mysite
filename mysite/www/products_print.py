import frappe
from erpnext.controllers.website_list_for_contact import get_parents_for_user

from mysite.www.barstools import get_chairs_by_type as get_barstools
from mysite.www.beds import get_nested_bed_products
from mysite.www.benches import get_related_items as get_benches
from mysite.www.cloth import get_cloth_groups
from mysite.www.coffee_tables import get_related_items as get_coffee_tables
from mysite.www.cushions import get_cushion_groups
from mysite.www.dining_chairs import get_chairs_by_type as get_dining_chairs
from mysite.www.sofas import get_nested_sofa_products
from mysite.www.tables import get_chairs_by_type as get_dining_tables

no_cache = 1


def _to_float(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def _to_toman_from_rial(value):
    rial = _to_float(value)
    if rial <= 0:
        return 0
    return int(rial / 10)


def _resolve_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _is_valid_selling_price_list(price_list_name):
    if not price_list_name:
        return False
    try:
        row = frappe.db.get_value(
            "Price List",
            price_list_name,
            ["name", "enabled", "selling"],
            as_dict=True,
        )
    except Exception:
        row = None
    if not row:
        return False
    if not row.get("enabled"):
        return False
    # keep strict to selling lists for website pricing
    if "selling" in row and not row.get("selling"):
        return False
    return True


def _get_available_price_lists():
    try:
        rows = frappe.get_all(
            "Price List",
            filters={"enabled": 1, "selling": 1},
            fields=["name"],
            order_by="name asc",
        )
    except Exception:
        rows = []
    return [r.get("name") for r in rows if r.get("name")]


def _resolve_customer_price_context(requested_customer, requested_price_list):
    selected_customer = None
    selected_price_list = _resolve_price_list()
    price_source = "default"

    if requested_price_list and _is_valid_selling_price_list(requested_price_list):
        selected_price_list = requested_price_list
        price_source = "manual"

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

    # manual selection should win even for authenticated customer
    if requested_price_list and _is_valid_selling_price_list(requested_price_list):
        selected_price_list = requested_price_list
        price_source = "manual"

    return selected_customer, selected_price_list, price_source


def _compute_cloth_meters(odd, even, minor):
    odd_val = max(0.0, _to_float(odd))
    even_val = max(0.0, _to_float(even))
    minor_val = max(0.0, _to_float(minor))
    main_val = odd_val if odd_val > 0 else even_val
    return round(main_val + minor_val, 2)


def _build_price_row(label, base_price_toman, odd=0, even=0, minor=0, cloth_meters=None):
    meters = _to_float(cloth_meters) if cloth_meters is not None else _compute_cloth_meters(odd, even, minor)
    base = int(max(0, _to_float(base_price_toman)))
    return {
        "label": label or "گزینه",
        "basePriceToman": base,
        "clothMeters": round(max(0.0, meters), 2),
        "finalPriceToman": base,
    }


def _build_dimensions(data):
    return {
        "length": str(data.get("length") or data.get("sofa_length") or "").strip(),
        "width": str(data.get("width") or data.get("sofa_width") or "").strip(),
        "height": str(data.get("height") or data.get("sofa_height") or "").strip(),
        "shape": str(data.get("shape") or data.get("sofa_shape") or "").strip(),
        "size": str(data.get("size") or "").strip(),
        "diameter": str(data.get("diameter") or data.get("sofa_diameter") or "").strip(),
    }


def _model_image(model):
    if model.get("image"):
        return model.get("image")
    images = model.get("images") or []
    if images:
        first = images[0]
        if isinstance(first, dict):
            return first.get("file_url") or ""
        return first
    return ""


def _module_image(module):
    images = module.get("sofa_module_images") or []
    if images:
        cover = next((img for img in images if img.get("cover")), None)
        target = cover or images[0]
        return target.get("file_url") or ""
    items = module.get("sofa_module_items") or []
    if items:
        first = items[0]
        if first.get("image"):
            return first.get("image")
        i_images = first.get("images") or []
        if i_images:
            cover = next((img for img in i_images if img.get("cover")), None)
            target = cover or i_images[0]
            return target.get("file_url") or ""
    return ""


def _transform_standard_models(models, section_id):
    items = []
    for idx, model in enumerate(models or []):
        rows = []
        model_odd = _to_float(model.get("odd_cloth"))
        model_even = _to_float(model.get("even_cloth"))
        model_minor = _to_float(model.get("minor_cloth"))

        for color in model.get("colors") or []:
            variant = color.get("variant") or {}
            base_toman = _to_toman_from_rial(variant.get("raw_price"))
            row_odd = _to_float(variant.get("odd_cloth")) or model_odd
            row_even = _to_float(variant.get("even_cloth")) or model_even
            row_minor = _to_float(variant.get("minor_cloth")) or model_minor
            row_label = color.get("name") or color.get("full_name") or "گزینه"
            rows.append(_build_price_row(row_label, base_toman, row_odd, row_even, row_minor))

        items.append(
            {
                "key": f"{section_id}-{idx}-{model.get('name') or 'item'}",
                "name": model.get("name") or model.get("display_name") or "محصول",
                "image": _model_image(model),
                "kind": "standard",
                "dimensions": _build_dimensions(model),
                "clothNeeds": {
                    "odd": model_odd,
                    "even": model_even,
                    "minor": model_minor,
                },
                "priceRows": rows,
            }
        )
    return items


def _transform_cushion_models(groups):
    items = []
    for idx, group in enumerate(groups or []):
        rows = []
        for opt in group.get("options") or []:
            base_toman = int(max(0, _to_float(opt.get("price_toman"))))
            rows.append(
                _build_price_row(
                    opt.get("name") or opt.get("package") or "گزینه",
                    base_toman,
                    opt.get("odd_cloth"),
                    opt.get("even_cloth"),
                    opt.get("minor_cloth"),
                )
            )

        items.append(
            {
                "key": f"cushion-{idx}-{group.get('name') or 'item'}",
                "name": group.get("display_name") or group.get("name") or "کوسن",
                "image": group.get("image") or "",
                "kind": "standard",
                "dimensions": _build_dimensions(group),
                "clothNeeds": {
                    "odd": _to_float(group.get("odd_cloth")),
                    "even": _to_float(group.get("even_cloth")),
                    "minor": _to_float(group.get("minor_cloth")),
                },
                "priceRows": rows,
            }
        )
    return items


def _transform_sofa_models(nested_models):
    items = []
    for m_idx, model in enumerate(nested_models or []):
        model_name = model.get("sofa_model_name") or f"sofa-{m_idx}"

        for mod_idx, module in enumerate(model.get("sofa_modules") or []):
            rows = []
            mod_odd = _to_float(module.get("sofa_odd_cloth"))
            mod_even = _to_float(module.get("sofa_even_cloth"))
            mod_minor = _to_float(module.get("sofa_minor_cloth"))

            for variant in module.get("sofa_module_items") or []:
                base_toman = int(max(0, _to_float(variant.get("Price"))))
                if not base_toman:
                    base_toman = _to_toman_from_rial(variant.get("raw_price"))
                row_odd = _to_float(variant.get("odd_cloth")) or mod_odd
                row_even = _to_float(variant.get("even_cloth")) or mod_even
                row_minor = _to_float(variant.get("minor_cloth")) or mod_minor
                rows.append(
                    _build_price_row(
                        variant.get("display_name_without_wood_color")
                        or variant.get("display_name")
                        or variant.get("item_name")
                        or variant.get("item_code")
                        or "مدل",
                        base_toman,
                        row_odd,
                        row_even,
                        row_minor,
                    )
                )

            items.append(
                {
                    "key": f"sofa-module-{m_idx}-{mod_idx}-{model_name}",
                    "name": module.get("sofa_module_name") or model_name,
                    "image": _module_image(module) or model.get("sofa_main_photo") or "",
                    "kind": "module",
                    "dimensions": _build_dimensions(module),
                    "clothNeeds": {"odd": mod_odd, "even": mod_even, "minor": mod_minor},
                    "priceRows": rows,
                }
            )

        for b_idx, bundle in enumerate(model.get("sofa_bundles") or []):
            odd = _to_float(bundle.get("odd_fabric"))
            even = _to_float(bundle.get("even_fabric"))
            minor = _to_float(bundle.get("minor_fabric"))
            total_fabric = _to_float(bundle.get("total_fabric"))
            rows = [
                _build_price_row(
                    "بسته کامل",
                    int(max(0, _to_float(bundle.get("bundle_price")))),
                    odd,
                    even,
                    minor,
                    cloth_meters=total_fabric if total_fabric > 0 else None,
                )
            ]

            items.append(
                {
                    "key": f"sofa-bundle-{m_idx}-{b_idx}-{model_name}",
                    "name": bundle.get("sofa_bundle_display_name") or bundle.get("name") or "بسته مبلمان",
                    "image": bundle.get("bundle_cover_photo") or model.get("sofa_main_photo") or "",
                    "kind": "bundle",
                    "dimensions": _build_dimensions({}),
                    "clothNeeds": {"odd": odd, "even": even, "minor": minor},
                    "priceRows": rows,
                }
            )
    return items


def _transform_bed_models(nested_models):
    items = []
    for idx, model in enumerate(nested_models or []):
        modules = model.get("sofa_modules") or []
        if modules:
            for m_idx, module in enumerate(modules):
                rows = []
                for variant in module.get("sofa_module_items") or []:
                    base_toman = int(max(0, _to_float(variant.get("Price"))))
                    if not base_toman:
                        base_toman = _to_toman_from_rial(variant.get("raw_price"))
                    rows.append(_build_price_row(variant.get("display_name") or variant.get("item_name") or "مدل", base_toman))

                items.append(
                    {
                        "key": f"bed-module-{idx}-{m_idx}",
                        "name": module.get("sofa_module_name") or model.get("sofa_model_name") or "سرویس خواب",
                        "image": _module_image(module) or model.get("sofa_main_photo") or "",
                        "kind": "module",
                        "dimensions": _build_dimensions(module),
                        "clothNeeds": {"odd": 0, "even": 0, "minor": 0},
                        "priceRows": rows,
                    }
                )
        else:
            items.append(
                {
                    "key": f"bed-{idx}",
                    "name": model.get("sofa_model_name") or "سرویس خواب",
                    "image": model.get("sofa_main_photo") or "",
                    "kind": "standard",
                    "dimensions": _build_dimensions(model),
                    "clothNeeds": {"odd": 0, "even": 0, "minor": 0},
                    "priceRows": [],
                }
            )
    return items


def _safe_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        return []


def _build_sections(price_list):
    sofa_items = _transform_sofa_models(_safe_call(get_nested_sofa_products, price_list))
    coffee_items = _transform_standard_models(
        _safe_call(get_coffee_tables, ("میز جلومبلی", "میز عسلی", "باکس"), price_list), "coffee-tables"
    )
    dining_chair_items = _transform_standard_models(_safe_call(get_dining_chairs, "صندلی ناهارخوری", price_list), "dining-chairs")
    dining_table_items = _transform_standard_models(_safe_call(get_dining_tables, "میز ناهارخوری", price_list), "tables")
    barstool_items = _transform_standard_models(_safe_call(get_barstools, "صندلی اپن", price_list), "barstools")
    bench_items = _transform_standard_models(_safe_call(get_benches, ("نیمکت", "پاف"), price_list), "benches")
    cushion_items = _transform_cushion_models(_safe_call(get_cushion_groups, price_list))
    bed_items = _transform_bed_models(_safe_call(get_nested_bed_products, price_list))

    ordered = [
        {"id": "sofas", "title": "مبلمان", "items": sofa_items},
        {"id": "coffee-tables", "title": "میزهای جلومبلی و عسلی", "items": coffee_items},
        {"id": "dining-chairs", "title": "صندلی‌های ناهارخوری", "items": dining_chair_items},
        {"id": "tables", "title": "میزهای ناهارخوری", "items": dining_table_items},
        {"id": "barstools", "title": "صندلی‌های اپن", "items": barstool_items},
        {"id": "benches", "title": "نیمکت و پاف", "items": bench_items},
        {"id": "cushions", "title": "کوسن و تشکچه", "items": cushion_items},
        {"id": "beds", "title": "سرویس خواب", "items": bed_items},
    ]
    return [section for section in ordered if section.get("items")]


def get_context(context):
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    requested_price_list = (frappe.form_dict.get("price_list") or "").strip()
    selected_customer, price_list_param, price_source = _resolve_customer_price_context(
        requested_customer, requested_price_list
    )
    available_price_lists = _get_available_price_lists()
    if price_list_param and price_list_param not in available_price_lists:
        available_price_lists.append(price_list_param)

    context.boot = {
        "PrintCatalogSections": _build_sections(price_list_param),
        "ClothGroups": get_cloth_groups(price_list_param),
        "SelectedPriceList": price_list_param or "",
        "AvailablePriceLists": available_price_lists,
        "SelectedCustomer": selected_customer or "",
        "PriceSource": price_source,
        "csrf_token": csrf_token,
    }
    context.safe_render = 0
    return context
