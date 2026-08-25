import frappe
from mysite.www.mysite.cloth import get_cloth_groups

no_cache = 1

_PERSIAN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')


def _clean_text(value):
    return " ".join(str(value or "").replace('-', ' ').split()).strip()


def _normalize_for_key(value):
    return _clean_text(value).translate(_PERSIAN_DIGITS).lower()


def _fmt_toman(rial_price):
    if not rial_price:
        return "۰"

    toman = int((rial_price or 0) / 10)
    text = str(toman)
    formatted = ",".join([text[::-1][i:i + 3] for i in range(0, len(text), 3)])[::-1]
    digit_map = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    for en, fa in digit_map.items():
        formatted = formatted.replace(en, fa)
    return formatted


def _normalize_image_url(url):
    return (url or '').replace('/private/files/', '/files/')


def _infer_package(item_name):
    txt = _normalize_for_key(item_name)
    if 'چهار' in txt and 'تايي' in txt:
        return 'چهار تایی'
    if 'سه' in txt and 'تايي' in txt:
        return 'سه تایی'
    if 'دو' in txt and 'تايي' in txt:
        return 'دو تایی'
    if 'تكي' in txt:
        return 'تکی'
    return 'تکی'


def _display_variant_of(value, item_name):
    raw = _clean_text(value)
    if raw:
        return raw
    txt = _clean_text(item_name)
    if txt.startswith('تشکچه'):
        return 'تشکچه'
    return 'کوسن'


def _infer_cushion_type(row, variant_of):
    candidates = [
        row.get('cushion_type'),
        row.get('cushion_model'),
        row.get('model_product'),
    ]
    for c in candidates:
        c = _clean_text(c)
        if c and c.lower() != 'none':
            return c

    item_name = _clean_text(row.get('item_name'))
    base = item_name
    if base.startswith('کوسن'):
        base = base.replace('کوسن', '', 1).strip()
    if base.startswith('تشکچه'):
        base = base.replace('تشکچه', '', 1).strip()

    for marker in ['تکی', 'دو تایی', 'سه تایی', 'چهار تایی']:
        base = base.replace(marker, '').strip()

    return base or variant_of


def _infer_size(row):
    size = _clean_text(row.get('cushion_size'))
    if size and size.lower() != 'none':
        return size

    diameter = _clean_text(row.get('diameter_value'))
    if diameter and diameter.lower() != 'none':
        if diameter.startswith('قطر'):
            return diameter
        return f"قطر {diameter}"

    length = _clean_text(row.get('length_value'))
    width = _clean_text(row.get('width_value'))
    if length and width and length.lower() != 'none' and width.lower() != 'none':
        return f"{length} - {width}"

    return ''


def _package_order_key(label):
    normalized = _normalize_for_key(label)
    if 'تكي' in normalized:
        return 1
    if 'دو' in normalized and 'تايي' in normalized:
        return 2
    if 'سه' in normalized and 'تايي' in normalized:
        return 3
    if 'چهار' in normalized and 'تايي' in normalized:
        return 4
    return 50


def get_context(context):
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""

    context.boot = get_boot_data()
    context.boot["csrf_token"] = csrf_token
    context.safe_render = 0
    return context


def get_boot_data():
    price_list_param = None
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        price_list_param = default_pl or frappe.db.get_single_value("Selling Settings", "selling_price_list")
    except Exception:
        pass

    groups = get_cushion_groups(price_list_param)

    return {
        "CushionGroups": groups,
        "BodyColorChairs": groups,
        "WoodColorChairs": [],
        "AvailableModels": sorted(list(set(item.get("name") for item in groups if item.get("name")))),
        "AvailableBodyColors": [],
        "AvailableWoodColors": [],
        "ClothGroups": get_cloth_groups(price_list_param or "Standard Selling"),
        "site_name": frappe.local.site,
    }


def get_cushion_groups(price_list):
    query = """
        SELECT
            i.name as item_name,
            i.item_code,
            i.image,
            i.variant_of,
            COALESCE(ip.price_list_rate, 0) as price_list_rate,
            COALESCE(i.odd_cloth, 0) as odd_cloth,
            COALESCE(i.even_cloth, 0) as even_cloth,
            COALESCE(i.minor_cloth, 0) as minor_cloth,
            cushion_model_attr.attribute_value as cushion_model,
            cushion_type_attr.attribute_value as cushion_type,
            cushion_size_attr.attribute_value as cushion_size,
            cushion_pack_attr.attribute_value as cushion_pack,
            model_attr.attribute_value as model_product,
            length_attr.attribute_value as length_value,
            width_attr.attribute_value as width_value,
            height_attr.attribute_value as height_value,
            diameter_attr.attribute_value as diameter_value,
            shape_attr.attribute_value as shape_value
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
        LEFT JOIN `tabItem Variant Attribute` cushion_model_attr ON i.name = cushion_model_attr.parent AND cushion_model_attr.attribute = 'مدل کوسن'
        LEFT JOIN `tabItem Variant Attribute` cushion_type_attr ON i.name = cushion_type_attr.parent AND cushion_type_attr.attribute = 'نوع کوسن'
        LEFT JOIN `tabItem Variant Attribute` cushion_size_attr ON i.name = cushion_size_attr.parent AND cushion_size_attr.attribute = 'سایز کوسن'
        LEFT JOIN `tabItem Variant Attribute` cushion_pack_attr ON i.name = cushion_pack_attr.parent AND cushion_pack_attr.attribute = 'بسته کوسن'
        LEFT JOIN `tabItem Variant Attribute` model_attr ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
        LEFT JOIN `tabItem Variant Attribute` length_attr ON i.name = length_attr.parent AND length_attr.attribute = 'طول'
        LEFT JOIN `tabItem Variant Attribute` width_attr ON i.name = width_attr.parent AND width_attr.attribute = 'عرض'
        LEFT JOIN `tabItem Variant Attribute` height_attr ON i.name = height_attr.parent AND height_attr.attribute = 'ارتفاع'
        LEFT JOIN `tabItem Variant Attribute` diameter_attr ON i.name = diameter_attr.parent AND diameter_attr.attribute = 'قطر'
        LEFT JOIN `tabItem Variant Attribute` shape_attr ON i.name = shape_attr.parent AND shape_attr.attribute = 'شکل'
        WHERE i.item_group = 'محصولات'
            AND i.show_on_site = 1
            AND COALESCE(i.has_variants, 0) = 0
            AND (
                COALESCE(i.variant_of, '') LIKE 'کوسن%%'
                OR COALESCE(i.variant_of, '') LIKE 'تشکچه%%'
                OR i.item_name LIKE 'کوسن%%'
                OR i.item_name LIKE 'تشکچه%%'
            )
        ORDER BY i.creation DESC
    """
    rows = frappe.db.sql(query, (price_list or '',), as_dict=True)

    item_names = list(set(row.item_name for row in rows if row.item_name))
    image_lookup = {}
    if item_names:
        ph = ','.join(['%s'] * len(item_names))
        files = frappe.db.sql(
            f"""
            SELECT attached_to_name, file_url, custom_tag
            FROM `tabFile`
            WHERE attached_to_doctype = 'Item'
              AND attached_to_name IN ({ph})
              AND (
                file_url LIKE '%%.jpg' OR file_url LIKE '%%.jpeg' OR file_url LIKE '%%.png'
                OR file_url LIKE '%%.webp' OR file_url LIKE '%%.svg'
              )
            ORDER BY CASE WHEN custom_tag = 'کاور' THEN 0 ELSE 1 END, creation ASC
            """,
            tuple(item_names),
            as_dict=True,
        )
        for f in files:
            image_lookup.setdefault(f.attached_to_name, []).append({
                "file_url": _normalize_image_url(f.file_url),
                "custom_tag": f.custom_tag or '',
            })

    grouped = {}

    for row in rows:
        item_name = _clean_text(row.get('item_name'))
        if not item_name:
            continue

        variant_of = _display_variant_of(row.get('variant_of'), item_name)
        cushion_type = _infer_cushion_type(row, variant_of)
        size_label = _infer_size(row)
        package_label = _clean_text(row.get('cushion_pack')) or _infer_package(item_name)

        group_key = '|'.join([
            _normalize_for_key(variant_of),
            _normalize_for_key(cushion_type),
            _normalize_for_key(size_label),
        ])

        imgs = image_lookup.get(item_name, [])
        cover = next((img.get('file_url') for img in imgs if img.get('custom_tag') == 'کاور'), None)
        main_image = cover or (imgs[0].get('file_url') if imgs else _normalize_image_url(row.get('image')))

        display_name = f"{variant_of} {cushion_type}".strip()
        if display_name.startswith(f"{variant_of} {variant_of}"):
            display_name = display_name.replace(f"{variant_of} {variant_of}", variant_of, 1).strip()

        if group_key not in grouped:
            grouped[group_key] = {
                "name": display_name,
                "display_name": display_name,
                "variant_of": variant_of,
                "cushion_type": cushion_type,
                "size": size_label,
                "image": main_image,
                "images": imgs,
                "options": {},
                "odd_cloth": 0.0,
                "even_cloth": 0.0,
                "minor_cloth": 0.0,
                "length": _clean_text(row.get('length_value')),
                "width": _clean_text(row.get('width_value')),
                "height": _clean_text(row.get('height_value')),
                "shape": _clean_text(row.get('shape_value')),
            }

        option_obj = {
            "name": package_label,
            "package": package_label,
            "item_name": item_name,
            "item_code": row.get('item_code') or item_name,
            "raw_price": float(row.get('price_list_rate') or 0),
            "price_toman": int((row.get('price_list_rate') or 0) / 10) if row.get('price_list_rate') else 0,
            "formatted_price": _fmt_toman(row.get('price_list_rate')),
            "odd_cloth": float(row.get('odd_cloth') or 0),
            "even_cloth": float(row.get('even_cloth') or 0),
            "minor_cloth": float(row.get('minor_cloth') or 0),
            "image": main_image,
        }

        existing = grouped[group_key]["options"].get(package_label)
        if (not existing) or (option_obj["raw_price"] > (existing.get("raw_price") or 0)):
            grouped[group_key]["options"][package_label] = option_obj

        grouped[group_key]["odd_cloth"] = max(grouped[group_key]["odd_cloth"], option_obj["odd_cloth"])
        grouped[group_key]["even_cloth"] = max(grouped[group_key]["even_cloth"], option_obj["even_cloth"])
        grouped[group_key]["minor_cloth"] = max(grouped[group_key]["minor_cloth"], option_obj["minor_cloth"])

        if (not grouped[group_key].get("image")) and main_image:
            grouped[group_key]["image"] = main_image

    results = []
    for item in grouped.values():
        options = list(item["options"].values())
        options.sort(key=lambda opt: (_package_order_key(opt.get('name')), _normalize_for_key(opt.get('name'))))
        item["options"] = options

        # Temporary compatibility with existing components expecting `colors`.
        item["colors"] = [
            {
                "name": opt.get("name"),
                "is_wood": False,
                "variant": {
                    "item_code": opt.get("item_code"),
                    "raw_price": opt.get("raw_price"),
                    "odd_cloth": opt.get("odd_cloth"),
                    "even_cloth": opt.get("even_cloth"),
                    "minor_cloth": opt.get("minor_cloth"),
                },
            }
            for opt in options
        ]

        results.append(item)

    results.sort(key=lambda it: (_normalize_for_key(it.get('variant_of')), _normalize_for_key(it.get('cushion_type')), _normalize_for_key(it.get('size'))))
    return results
