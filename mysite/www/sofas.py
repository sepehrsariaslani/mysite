"""
Sofas Page Controller - مبلمان
Rewritten to match the exact data structure required by the Vue frontend.
Uses cloth.py for ClothGroups data.
"""

import frappe
import json
from mysite.www.cloth import get_cloth_groups

no_cache = 1


def get_context(context):
    """Frappe www controller for the sofas page"""
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""

    context.boot = get_boot_data()
    context.boot["csrf_token"] = csrf_token
    context.safe_render = 0
    return context


def get_boot_data():
    """Main data gathering function"""
    
    # ── Price list ─────────────────────────────────────────────────
    price_list_param = None
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        price_list_param = default_pl or frappe.db.get_single_value("Selling Settings", "selling_price_list")
    except Exception:
        pass

    nested_products = get_nested_sofa_products(price_list_param)
    cloth_groups = get_cloth_groups("Standard Selling")

    return frappe._dict({
        "NestedSofaProducts": nested_products,
        "ClothGroups": cloth_groups,
        "SelectedPriceList": price_list_param or "",
        "site_name": frappe.local.site,
    })


# ─────────────────────────────────────────────────────────────────
# Sofas
# ─────────────────────────────────────────────────────────────────

WOOD_COLORS = [
    "خودرنگ", "رنگ فندقی روشن", "رنگ گردویی روشن",
    "رنگ فندوقی تیره", "رنگ گردویی تیره", "چوب مشکی",
    "رنگ عسلی روشن", "رنگ عسلی تیره", "چوب سفید"
]


def to_persian_digits(number):
    """Convert digits to Persian"""
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    text = str(number)
    for en, fa in persian_digits.items():
        text = text.replace(en, fa)
    return text


def fmt_toman(rial_price):
    """Format rial price to Persian Toman string"""
    if not rial_price or rial_price <= 0:
        return "تماس بگیرید"
    toman = int(rial_price / 10)
    s = str(toman)
    formatted = ",".join([s[::-1][i:i+3] for i in range(0, len(s), 3)])[::-1]
    return to_persian_digits(formatted)


def clean_wood_color(name):
    """Remove wood color substring from end of name"""
    n = (name or '').strip()
    for color in WOOD_COLORS:
        if n.endswith(color):
            n = n[:-len(color)].strip()
    return n


def get_nested_sofa_products(price_list_param):
    """Build the NestedSofaProducts data structure"""
    
    # 1. Main sofa items query
    sofa_query = """
        SELECT 
            i.name as item_name,
            i.item_code,
            i.item_name as display_name,
            i.description,
            i.image,
            i.creation,
            ip.price_list_rate,
            COALESCE(bin.projected_qty, 0) as projected_qty,
            COALESCE(i.odd_cloth, 0) as odd_cloth,
            COALESCE(i.even_cloth, 0) as even_cloth,
            COALESCE(i.minor_cloth, 0) as minor_cloth,
            COALESCE(i.cushion_cloth, 0) as cushion_cloth,
            model_attr.attribute_value as model,
            module_attr.attribute_value as module,
            feature_attr.attribute_value as module_feature,
            length_attr.attribute_value as length_value,
            width_attr.attribute_value as width_value,
            height_attr.attribute_value as height_value,
            body_color_attr.attribute_value as body_color,
            wood_color_attr.attribute_value as wood_color,
            body_color_jav.abbr as body_color_abbr,
            wood_color_jav.abbr as wood_color_abbr,
            i.yindex as yindex
        FROM `tabItem` i
        LEFT JOIN `tabBin` bin ON i.name = bin.item_code
        LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
        LEFT JOIN `tabItem Variant Attribute` model_attr ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
        LEFT JOIN `tabItem Variant Attribute` module_attr ON i.name = module_attr.parent AND module_attr.attribute = 'ماژول'
        LEFT JOIN `tabItem Variant Attribute` feature_attr ON i.name = feature_attr.parent AND feature_attr.attribute = 'ویژگی ماژول'
        LEFT JOIN `tabItem Variant Attribute` length_attr ON i.name = length_attr.parent AND length_attr.attribute = 'طول'
        LEFT JOIN `tabItem Variant Attribute` width_attr ON i.name = width_attr.parent AND width_attr.attribute = 'عرض'
        LEFT JOIN `tabItem Variant Attribute` height_attr ON i.name = height_attr.parent AND height_attr.attribute = 'ارتفاع'
        LEFT JOIN `tabItem Variant Attribute` wood_color_attr ON i.name = wood_color_attr.parent AND wood_color_attr.attribute = 'رنگ چوب'
        LEFT JOIN `tabItem Attribute Value` wood_color_jav ON wood_color_attr.attribute_value = wood_color_jav.attribute_value AND wood_color_attr.attribute = wood_color_jav.parent
        LEFT JOIN `tabItem Variant Attribute` body_color_attr ON i.name = body_color_attr.parent AND body_color_attr.attribute = 'رنگ بدنه'
        LEFT JOIN `tabItem Attribute Value` body_color_jav ON body_color_attr.attribute_value = body_color_jav.attribute_value AND body_color_attr.attribute = body_color_jav.parent
        WHERE i.item_group = 'محصولات'
          AND i.show_on_site = 1
          AND COALESCE(i.variant_of, '') NOT IN (
              'میز جلومبلی', 'میز عسلی', 'میز ناهارخوری',
              'نیمکت', 'پاف', 'باکس', 'کوسن',
              'صندلی ناهارخوری', 'صندلی اپن', 'سرویس خواب'
          )
          AND EXISTS (
              SELECT 1 FROM `tabItem Variant Attribute` iva_model
              WHERE iva_model.parent = i.name
                AND iva_model.attribute = 'مدل محصول'
                AND COALESCE(iva_model.attribute_value, '') != ''
          )
          AND EXISTS (
              SELECT 1 FROM `tabItem Variant Attribute` iva_module
              WHERE iva_module.parent = i.name
                AND iva_module.attribute = 'ماژول'
                AND COALESCE(iva_module.attribute_value, '') != ''
          )
        ORDER BY i.creation DESC
    """
    
    try:
        sofas_raw = frappe.db.sql(sofa_query, (price_list_param or '',), as_dict=True)
    except Exception as e:
        frappe.log_error(f"sofas.py main query error: {e}")
        sofas_raw = []

    if not sofas_raw:
        return []

    # 2. Fetch item images in bulk
    item_names = list(set(s.item_name for s in sofas_raw if s.item_name))
    image_lookup = {}
    if item_names:
        try:
            ph = ','.join(['%s'] * len(item_names))
            files = frappe.db.sql(
                f"""SELECT name, file_name, file_url, file_size, file_type,
                           attached_to_name, custom_yindex, custom_alt_text, custom_tag
                    FROM `tabFile`
                    WHERE attached_to_doctype = 'Item'
                      AND attached_to_name IN ({ph})
                      AND (file_url LIKE '%%.jpg' OR file_url LIKE '%%.jpeg'
                           OR file_url LIKE '%%.png' OR file_url LIKE '%%.webp'
                           OR file_url LIKE '%%.svg')
                    ORDER BY CASE WHEN custom_tag = 'کاور' THEN 0 ELSE 1 END, CAST(COALESCE(custom_yindex, 0) AS SIGNED) ASC""",
                tuple(item_names), as_dict=True
            )
            for img in files:
                tag = img.custom_tag or ''
                image_lookup.setdefault(img.attached_to_name, []).append({
                    "name": img.name or "",
                    "file_name": img.file_name or "",
                    "file_url": img.file_url or "",
                    "file_size": img.file_size or 0,
                    "file_type": img.file_type or "",
                    "attached_to_name": img.attached_to_name or "",
                    "custom_yindex": img.custom_yindex or "",
                    "custom_alt_text": img.custom_alt_text or "",
                    "custom_tag": tag,
                    "cover": tag == "کاور",
                    "dimentions": tag == "اندازه",
                    "gallary": tag == "گالری",
                    "icon": tag == "آیکون",
                })
        except Exception as e:
            frappe.log_error(f"sofas.py image query error: {e}")

    # 3. Process each raw item
    sofas = []
    for sofa in sofas_raw:
        price = int(sofa.price_list_rate / 10) if sofa.price_list_rate and sofa.price_list_rate > 0 else 0
        item_imgs = image_lookup.get(sofa.item_name, [])
        sofas.append({
            "item_name": sofa.item_name or "",
            "item_code": sofa.item_code or sofa.item_name or "",
            "display_name": sofa.display_name or sofa.item_name or "",
            "display_name_without_wood_color": clean_wood_color(sofa.item_name),
            "description": sofa.description or "",
            "image": (item_imgs[0]["file_url"] if item_imgs else sofa.image) or "",
            "creation": str(sofa.creation) if sofa.creation else "",
            "projected_qty": sofa.projected_qty or 0,
            "price_list_rate": sofa.price_list_rate or 0,
            "model": sofa.model or "",
            "module": sofa.module or "",
            "module_feature": sofa.module_feature or "",
            "module_length": sofa.length_value or "0",
            "module_width": sofa.width_value or "0",
            "module_height": sofa.height_value or "0",
            "module_diameter": "",
            "module_shape": "",
            "module_color": "",
            "wood_color": sofa.wood_color_abbr or sofa.wood_color or "",
            "body_color": sofa.body_color_abbr or sofa.body_color or "",
            "wood_color_full": sofa.wood_color or "",
            "body_color_full": sofa.body_color or "",
            "odd_cloth": float(sofa.odd_cloth) if sofa.odd_cloth else 0,
            "even_cloth": float(sofa.even_cloth) if sofa.even_cloth else 0,
            "minor_cloth": float(sofa.minor_cloth) if sofa.minor_cloth else 0,
            "cushion_cloth": float(sofa.cushion_cloth) if sofa.cushion_cloth else 0,
            "Price": price,
            "formatted_Price": fmt_toman(sofa.price_list_rate or 0),
            "images": item_imgs,
            "stock_qty": sofa.projected_qty or 0,
            "yindex": sofa.yindex or "",
            "variant_of": "مبل",
            "all_wood_colors": [],
            "is_minor": bool(sofa.minor_cloth),
        })

    # 4. Fetch Product Groups (model meta: photo, description, yindex, bundles)
    try:
        ProductGroups = frappe.db.get_all(
            "Product Group",
            fields=["name", "product_model", "description", "main_photo", "icon_photo", "yindex"],
            order_by="yindex asc"
        )
    except Exception:
        ProductGroups = []

    # 5. Fetch bundles for each product group
    all_bundle_names = []
    group_items_map = {}
    for group in ProductGroups:
        try:
            g_items = frappe.db.get_all(
                "Product Group Item",
                filters={"parent": group["name"]},
                fields=["product_bundel", "sofa_cloth", "cushion_cloth"],
            )
            group_items_map[group["name"]] = g_items
            for gi in g_items:
                if gi.product_bundel:
                    all_bundle_names.append(gi.product_bundel)
        except Exception:
            group_items_map[group["name"]] = []

    # Fetch bundle details in bulk
    bundle_lookup = {}
    if all_bundle_names:
        try:
            ph = ','.join(['%s'] * len(all_bundle_names))
            bundle_query = f"""
                SELECT pb.name, pb.new_item_code, pb.description, pb.disabled,
                       pb.show_on_site, pb.cover_photo, pb.yindex,
                       COALESCE(ip.price_list_rate, 0) as price_list_rate,
                       COALESCE(i.odd_cloth, 0) as odd_fabric,
                       COALESCE(i.even_cloth, 0) as even_fabric,
                       COALESCE(i.cushion_cloth, 0) as cushion_fabric,
                       COALESCE(i.minor_cloth, 0) as minor_fabric
                FROM `tabProduct Bundle` pb
                LEFT JOIN `tabItem` i ON pb.name = i.name
                LEFT JOIN `tabItem Price` ip ON pb.name = ip.item_code AND ip.price_list = %s
                WHERE pb.name IN ({ph}) AND pb.show_on_site = 1
            """
            bundles_raw = frappe.db.sql(bundle_query, (price_list_param or '',) + tuple(all_bundle_names), as_dict=True)
            for b in bundles_raw:
                bundle_lookup[b.name] = b
        except Exception as e:
            frappe.log_error(f"sofas.py bundle query error: {e}")

    # Fetch bundle constituent items
    bundle_items_map = {}
    bi_rows = []
    if all_bundle_names:
        try:
            ph = ','.join(['%s'] * len(all_bundle_names))
            bi_rows = frappe.db.sql(
                f"SELECT parent, item_code, qty, uom FROM `tabProduct Bundle Item` WHERE parent IN ({ph})",
                tuple(all_bundle_names), as_dict=True
            )
            for row in bi_rows:
                bundle_items_map.setdefault(row.parent, []).append(row)
        except Exception:
            pass

    # Build bundle objects
    item_lookup_by_code = {s["item_code"]: s for s in sofas}
    bundle_item_fallback_lookup = {}
    bundle_item_codes = sorted({(row.item_code or "") for row in bi_rows if row.item_code})
    if bundle_item_codes:
        try:
            ph = ','.join(['%s'] * len(bundle_item_codes))
            fallback_rows = frappe.db.sql(
                f"""
                SELECT
                    i.item_code,
                    i.name as item_name,
                    i.item_name as display_name,
                    i.image,
                    i.variant_of,
                    COALESCE(ip.price_list_rate, 0) as price_list_rate,
                    COALESCE(i.odd_cloth, 0) as odd_cloth,
                    COALESCE(i.even_cloth, 0) as even_cloth,
                    COALESCE(i.minor_cloth, 0) as minor_cloth,
                    COALESCE(i.cushion_cloth, 0) as cushion_cloth,
                    module_attr.attribute_value as module
                FROM `tabItem` i
                LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
                LEFT JOIN `tabItem Variant Attribute` module_attr ON i.name = module_attr.parent AND module_attr.attribute = 'ماژول'
                WHERE i.item_code IN ({ph})
                """,
                (price_list_param or '',) + tuple(bundle_item_codes),
                as_dict=True
            )
            for row in fallback_rows:
                price_toman = int((row.price_list_rate or 0) / 10) if row.price_list_rate else 0
                bundle_item_fallback_lookup[row.item_code] = {
                    "item_name": row.item_name or row.item_code or "",
                    "item_code": row.item_code or row.item_name or "",
                    "display_name": row.display_name or row.item_name or row.item_code or "",
                    "image": row.image or "",
                    "module": row.module or "",
                    "variant_of": row.variant_of or "",
                    "odd_cloth": float(row.odd_cloth) if row.odd_cloth else 0,
                    "even_cloth": float(row.even_cloth) if row.even_cloth else 0,
                    "minor_cloth": float(row.minor_cloth) if row.minor_cloth else 0,
                    "cushion_cloth": float(row.cushion_cloth) if row.cushion_cloth else 0,
                    "Price": price_toman,
                    "formatted_Price": fmt_toman(row.price_list_rate or 0),
                    "is_minor": bool(row.minor_cloth),
                }
        except Exception as e:
            frappe.log_error(f"sofas.py bundle item fallback query error: {e}")

    def make_bundle_obj(bundle_name, all_sofas):
        b = bundle_lookup.get(bundle_name)
        if not b:
            return None
        
        price = int(b.price_list_rate / 10) if b.price_list_rate and b.price_list_rate > 0 else 0
        base_name = clean_wood_color(b.name)
        
        # Constituent items
        table_items = []
        for bi in bundle_items_map.get(bundle_name, []):
            info = item_lookup_by_code.get(bi.item_code) or bundle_item_fallback_lookup.get(bi.item_code)
            if not info:
                info = {
                    "item_name": bi.item_code or "",
                    "item_code": bi.item_code or "",
                    "display_name": bi.item_code or "",
                    "image": "",
                    "module": "",
                    "variant_of": "",
                    "odd_cloth": 0,
                    "cushion_cloth": 0,
                    "minor_cloth": 0,
                    "Price": 0,
                    "formatted_Price": "۰",
                    "is_minor": False,
                }
            table_items.append({
                "item_code": bi.item_code or "",
                "qty": bi.qty or 1,
                "uom": bi.uom or "",
                "module_name": info.get("module") or "",
                "item_name": info.get("item_name") or bi.item_code or "",
                "display_name": info.get("display_name") or bi.item_code or "",
                "image": info.get("image") or "",
                "Price": info.get("Price") or 0,
                "formatted_Price": info.get("formatted_Price") or "۰",
                "odd_cloth": info.get("odd_cloth") or 0,
                "cushion_cloth": info.get("cushion_cloth") or 0,
                "minor_cloth": info.get("minor_cloth") or 0,
                "is_minor": info.get("is_minor") or False,
                "variant_of": info.get("variant_of") or "",
            })
        total_units = 0
        for t in table_items:
            try:
                total_units += float(t.get("qty") or 1)
            except Exception:
                total_units += 1

        # Skip pseudo-bundles that are effectively a single standalone module.
        if not table_items or total_units <= 1:
            return None

        return {
            "name": base_name,
            "bundle_name": bundle_name,
            "sofa_bundle_name": base_name,
            "sofa_bundle_display_name": b.new_item_code or base_name,
            "bundle_cover_photo": b.cover_photo or "",
            "bundle_price": price,
            "bundle_formatted_price": fmt_toman(b.price_list_rate),
            "odd_fabric": float(b.odd_fabric) if b.odd_fabric else 0,
            "even_fabric": float(b.even_fabric) if b.even_fabric else 0,
            "cushion_fabric": float(b.cushion_fabric) if b.cushion_fabric else 0,
            "minor_fabric": float(b.minor_fabric) if b.minor_fabric else 0,
            "total_fabric": round((b.odd_fabric or 0) + (b.cushion_fabric or 0) + (b.minor_fabric or 0), 2),
            "is_minor": bool(b.minor_fabric),
            "yindex": b.yindex or "",
            "sofa_bundle_table_items": table_items,
        }

    # 6. Group products by model
    product_group_lookup = {g["product_model"]: g for g in ProductGroups}
    all_models = sorted(set(s["model"] for s in sofas if s["model"]))

    def sort_key(x):
        try:
            return (0, int(x.get("yindex") or x.get("sofa_yindex") or 9999))
        except Exception:
            return (1, 0)

    nested_products = []
    for model_name in all_models:
        model_sofas = [s for s in sofas if s["model"] == model_name]
        if not model_sofas:
            continue

        group_info = product_group_lookup.get(model_name, {})

        # Collect all model images (de-duplicated)
        model_images = []
        seen_urls = set()
        for sofa in model_sofas:
            for img in sofa["images"]:
                if img["file_url"] not in seen_urls:
                    model_images.append(img)
                    seen_urls.add(img["file_url"])

        # Build modules: group by (module, module_feature, length, width, height)
        module_groups = {}
        for sofa in model_sofas:
            key = (
                sofa["module"],
                sofa["module_feature"],
                sofa["module_length"],
                sofa["module_width"],
                sofa["module_height"],
            )
            module_groups.setdefault(key, []).append(sofa)

        modules = []
        for (mod_name, mod_feature, length, width, height), items in module_groups.items():
            # Sub-group by body_color
            subgroups = {}
            for s in items:
                subgroups.setdefault(s["body_color"], []).append(s)

            module_items = []
            all_images = []
            seen_img_urls = set()

            for body_color, sub_items in subgroups.items():
                max_item = max(sub_items, key=lambda x: x["Price"])
                wood_colors = list(set(s["wood_color"] for s in sub_items if s["wood_color"]))
                
                item_copy = max_item.copy()
                item_copy["all_wood_colors"] = wood_colors
                item_copy["module_feature"] = mod_feature
                module_items.append(item_copy)

                for s in sub_items:
                    for img in s["images"]:
                        if img["file_url"] not in seen_img_urls:
                            all_images.append(img)
                            seen_img_urls.add(img["file_url"])

            odd = max((s.get("odd_cloth") or 0) for s in items)
            even = max((s.get("even_cloth") or 0) for s in items)
            minor = max((s.get("minor_cloth") or 0) for s in items)
            cushion = max((s.get("cushion_cloth") or 0) for s in items)

            yindexes = []
            for s in items:
                try:
                    if s.get("yindex") not in (None, ""):
                        yindexes.append(float(s["yindex"]))
                except Exception:
                    pass
            avg_yindex = sum(yindexes) / len(yindexes) if yindexes else None

            modules.append({
                "sofa_module_name": f"مبل {mod_name} {model_name}",
                "sofa_module_type": "مبل",
                "sofa_model": model_name,
                "sofa_product_type": "مبل",
                "sofa_length": length,
                "sofa_width": width,
                "sofa_height": height,
                "sofa_diameter": "",
                "sofa_shape": "",
                "sofa_odd_cloth": round(odd, 2),
                "sofa_even_cloth": round(even, 2),
                "sofa_minor_cloth": round(minor, 2),
                "sofa_cushion_cloth": round(cushion, 2),
                "is_minor": bool(minor),
                "total_cloth_for_sofa": round(odd + minor, 2),
                "sofa_module_images": all_images,
                "sofa_module_items": sorted(module_items, key=sort_key),
                "sofa_yindex": avg_yindex,
                "sofa_yindex_source": "items_avg" if yindexes else "",
            })

        modules.sort(key=sort_key)

        # ── Related products: باکس، نیمکت، میز جلومبلی، میز عسلی، کوسن ──
        # These share the same sofa model name but have different variant_of
        try:
            related_query = """
                SELECT 
                    i.name as item_name,
                    i.item_code,
                    i.item_name as display_name,
                    i.description,
                    i.image,
                    i.creation,
                    i.variant_of,
                    COALESCE(bin.projected_qty, 0) as projected_qty,
                    COALESCE(i.odd_cloth, 0) as odd_cloth,
                    COALESCE(i.even_cloth, 0) as even_cloth,
                    COALESCE(i.minor_cloth, 0) as minor_cloth,
                    COALESCE(i.cushion_cloth, 0) as cushion_cloth,
                    COALESCE(ip.price_list_rate, 0) as price_list_rate,
                    model_attr.attribute_value as model,
                    module_attr.attribute_value as module,
                    feature_attr.attribute_value as module_feature,
                    shape_attr.attribute_value as shape,
                    color_attr.attribute_value as body_color,
                    wood_color_attr.attribute_value as wood_color,
                    length_attr.attribute_value as length_value,
                    width_attr.attribute_value as width_value,
                    height_attr.attribute_value as height_value,
                    diameter_attr.attribute_value as diameter_value,
                    i.yindex as yindex
                FROM `tabItem` i
                LEFT JOIN `tabBin` bin ON i.name = bin.item_code
                LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
                LEFT JOIN `tabItem Variant Attribute` model_attr ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
                LEFT JOIN `tabItem Variant Attribute` module_attr ON i.name = module_attr.parent AND module_attr.attribute = 'ماژول'
                LEFT JOIN `tabItem Variant Attribute` feature_attr ON i.name = feature_attr.parent AND feature_attr.attribute = 'ویژگی ماژول'
                LEFT JOIN `tabItem Variant Attribute` shape_attr ON i.name = shape_attr.parent AND shape_attr.attribute = 'شکل'
                LEFT JOIN `tabItem Variant Attribute` color_attr ON i.name = color_attr.parent AND color_attr.attribute = 'رنگ بدنه'
                LEFT JOIN `tabItem Variant Attribute` wood_color_attr ON i.name = wood_color_attr.parent AND wood_color_attr.attribute = 'رنگ چوب'
                LEFT JOIN `tabItem Variant Attribute` length_attr ON i.name = length_attr.parent AND length_attr.attribute = 'طول'
                LEFT JOIN `tabItem Variant Attribute` width_attr ON i.name = width_attr.parent AND width_attr.attribute = 'عرض'
                LEFT JOIN `tabItem Variant Attribute` height_attr ON i.name = height_attr.parent AND height_attr.attribute = 'ارتفاع'
                LEFT JOIN `tabItem Variant Attribute` diameter_attr ON i.name = diameter_attr.parent AND diameter_attr.attribute = 'قطر'
                WHERE i.item_group = 'محصولات'
                    AND i.show_on_site = 1
                    AND COALESCE(i.has_variants, 0) = 0
                    AND (
                        i.variant_of IN ('میز جلومبلی', 'میز عسلی', 'باکس', 'نیمکت')
                        OR COALESCE(i.variant_of, '') LIKE 'کوسن%%'
                        OR COALESCE(i.variant_of, '') LIKE 'تشکچه%%'
                        OR i.item_name LIKE 'کوسن%%'
                        OR i.item_name LIKE 'تشکچه%%'
                    )
                    AND (
                        COALESCE(model_attr.attribute_value, '') = %s
                        OR (
                            (
                                COALESCE(i.variant_of, '') LIKE 'کوسن%%'
                                OR COALESCE(i.variant_of, '') LIKE 'تشکچه%%'
                                OR i.item_name LIKE 'کوسن%%'
                                OR i.item_name LIKE 'تشکچه%%'
                            )
                            AND i.item_name LIKE %s
                        )
                    )
                ORDER BY i.variant_of, i.yindex
            """
            related_raw = frappe.db.sql(
                related_query,
                (price_list_param or '', model_name, f"%{model_name}%"),
                as_dict=True,
            )

            # Fetch images for related items in bulk
            related_names = [r.item_name for r in related_raw if r.item_name]
            rel_image_lookup = {}
            if related_names:
                rph = ','.join(['%s'] * len(related_names))
                rel_files = frappe.db.sql(
                    f"""SELECT name, file_url, attached_to_name, custom_yindex, custom_alt_text, custom_tag
                        FROM `tabFile`
                        WHERE attached_to_doctype = 'Item'
                          AND attached_to_name IN ({rph})
                          AND (file_url LIKE '%%.jpg' OR file_url LIKE '%%.jpeg'
                               OR file_url LIKE '%%.png' OR file_url LIKE '%%.webp'
                               OR file_url LIKE '%%.svg')
                        ORDER BY CAST(COALESCE(custom_yindex, 0) AS SIGNED) ASC""",
                    tuple(related_names), as_dict=True
                )
                for img in rel_files:
                    tag = img.custom_tag or ''
                    rel_image_lookup.setdefault(img.attached_to_name, []).append({
                        "file_url": img.file_url or "",
                        "custom_alt_text": img.custom_alt_text or "",
                        "custom_tag": tag,
                        "cover": tag == "کاور",
                        "dimentions": tag == "اندازه",
                        "gallary": tag == "گالری",
                        "icon": tag == "آیکون",
                    })

            # Group related items by (variant_of, module/shape, body_color, dimensions)
            related_groups = {}
            for item in related_raw:
                variant_of = (item.variant_of or '').strip()
                item_name = item.item_name or ''
                is_cushion_like = (
                    'کوسن' in variant_of
                    or 'تشکچه' in variant_of
                    or item_name.startswith('کوسن')
                    or item_name.startswith('تشکچه')
                )

                mod_or_shape = item.module or item.shape or ''
                if is_cushion_like and not mod_or_shape:
                    inferred = clean_wood_color(item.display_name or item.item_name or '')
                    inferred = inferred.replace(model_name, '').strip()
                    mod_or_shape = inferred or item.item_name or model_name

                body_c = item.body_color or ''
                dims = (item.length_value or '', item.width_value or '', item.height_value or '', item.diameter_value or '')
                key = (
                    item.variant_of,
                    mod_or_shape,
                    body_c,
                    dims,
                    item.shape or '',
                    item.item_name if is_cushion_like else '',
                )
                related_groups.setdefault(key, []).append(item)

            for (var_of, mod_name_r, body_c, dims, shape_v, _cushion_key), r_items in related_groups.items():
                max_item = max(r_items, key=lambda x: x.price_list_rate or 0)
                wood_colors_r = list(set(r.wood_color for r in r_items if r.wood_color))

                all_rim = []
                seen_rim_urls = set()
                for r in r_items:
                    for img in rel_image_lookup.get(r.item_name, []):
                        if img["file_url"] not in seen_rim_urls:
                            all_rim.append(img)
                            seen_rim_urls.add(img["file_url"])

                r_price = int(max_item.price_list_rate / 10) if max_item.price_list_rate else 0
                r_odd = max((r.odd_cloth or 0) for r in r_items)
                r_even = max((r.even_cloth or 0) for r in r_items)
                r_minor = max((r.minor_cloth or 0) for r in r_items)
                r_cushion = max((r.cushion_cloth or 0) for r in r_items)

                module_item = {
                    "item_name": max_item.item_name or "",
                    "item_code": max_item.item_code or max_item.item_name or "",
                    "display_name": max_item.display_name or max_item.item_name or "",
                    "display_name_without_wood_color": clean_wood_color(max_item.item_name),
                    "description": max_item.description or "",
                    "image": max_item.image or "",
                    "creation": str(max_item.creation) if max_item.creation else "",
                    "projected_qty": max_item.projected_qty or 0,
                    "price_list_rate": max_item.price_list_rate or 0,
                    "model": model_name,
                    "module": mod_name_r,
                    "module_feature": max_item.module_feature or "",
                    "module_length": dims[0],
                    "module_width": dims[1],
                    "module_height": dims[2],
                    "module_diameter": dims[3],
                    "module_shape": shape_v,
                    "module_color": "",
                    "wood_color": max_item.wood_color or "",
                    "body_color": body_c,
                    "odd_cloth": float(r_odd) if r_odd else 0,
                    "even_cloth": float(r_even) if r_even else 0,
                    "minor_cloth": float(r_minor) if r_minor else 0,
                    "cushion_cloth": float(r_cushion) if r_cushion else 0,
                    "Price": r_price,
                    "formatted_Price": fmt_toman(max_item.price_list_rate),
                    "images": rel_image_lookup.get(max_item.item_name, []),
                    "stock_qty": max_item.projected_qty or 0,
                    "yindex": max_item.yindex or "",
                    "variant_of": var_of,
                    "all_wood_colors": wood_colors_r,
                    "is_minor": bool(r_minor),
                }

                try:
                    yidx_r = float(max_item.yindex) if max_item.yindex else None
                except Exception:
                    yidx_r = None

                module_suffix = (mod_name_r or shape_v or model_name or "").strip()
                if module_suffix and var_of and module_suffix.startswith(var_of):
                    module_display_name = module_suffix
                else:
                    module_display_name = f"{var_of} {module_suffix}".strip()
                module_display_name = " ".join(module_display_name.split())

                modules.append({
                    "sofa_module_name": module_display_name,
                    "sofa_module_type": var_of,
                    "sofa_model": model_name,
                    "sofa_product_type": var_of,
                    "sofa_length": dims[0],
                    "sofa_width": dims[1],
                    "sofa_height": dims[2],
                    "sofa_diameter": dims[3],
                    "sofa_shape": shape_v,
                    "sofa_odd_cloth": round(r_odd, 2),
                    "sofa_even_cloth": round(r_even, 2),
                    "sofa_minor_cloth": round(r_minor, 2),
                    "sofa_cushion_cloth": round(r_cushion, 2),
                    "is_minor": bool(r_minor),
                    "total_cloth_for_sofa": round(r_odd + r_minor, 2),
                    "sofa_module_images": all_rim,
                    "sofa_module_items": [module_item],
                    "sofa_yindex": yidx_r,
                    "sofa_yindex_source": "related_product",
                })

            # Re-sort after adding related products
            modules.sort(key=sort_key)

        except Exception as e:
            frappe.log_error(f"sofas.py related_products error for model {model_name}: {e}")

        # Build bundles for this model from Product Group
        group_name = group_info.get("name")
        bundles = []
        if group_name:
            for gi in group_items_map.get(group_name, []):
                if gi.product_bundel:
                    b_obj = make_bundle_obj(gi.product_bundel, model_sofas)
                    if b_obj:
                        bundles.append(b_obj)
            bundles.sort(key=sort_key)

        nested_products.append({
            "sofa_model_name": model_name,
            "sofa_route": f"sofas/{model_name}",
            "sofa_model_description": group_info.get("description") or "",
            "sofa_main_photo": group_info.get("main_photo") or "",
            "sofa_icon_photo": group_info.get("icon_photo") or "",
            "sofa_images": model_images,
            "sofa_modules": modules,
            "sofa_bundles": bundles,
            "sofa_bundles_count": len(bundles),
            "sofa_yindex": group_info.get("yindex") or "",
        })

    # Sort models by Product Group yindex
    nested_products.sort(key=lambda x: sort_key({"yindex": x.get("sofa_yindex")}))

    # Final cleanup: replace None with ""
    final_json = json.dumps(nested_products, default=str)
    final_json = final_json.replace(': null', ': ""')
    return json.loads(final_json)
