"""
Benches Page Controller - نیمکت
Fetches Benches for the Vue frontend.
"""

import frappe
import json
from mysite.www.mysite.cloth import get_cloth_groups

no_cache = 1

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

    # Fetch all "نیمکت" and "پاف"
    related_types = ('نیمکت', 'پاف')
    all_related = get_related_items(related_types, price_list_param)
    
    body_items = all_related
    wood_items = []
    
    cloth_groups = get_cloth_groups("Standard Selling")

    # Extract available models for filtering
    available_models = sorted(list(set(c["name"] for c in body_items + wood_items)))
    
    return {
        "BodyColorChairs": body_items,
        "WoodColorChairs": wood_items,
        "AvailableModels": available_models,
        "AvailableBodyColors": [],
        "AvailableWoodColors": [],
        "ClothGroups": cloth_groups,
        "site_name": frappe.local.site,
    }

def get_related_items(variant_of_list, price_list):
    # Ensure the tuple string is SQL compatible (especially safe for single-item tuples like ('Item',))
    v_list_str = str(variant_of_list)
    if len(variant_of_list) == 1:
        v_list_str = v_list_str.replace(',)', ')')
        
    query = """
        SELECT 
            i.name as item_name,
            i.item_code,
            i.item_name as display_name,
            i.image,
            COALESCE(ip.price_list_rate, 0) as price_list_rate,
            model_attr.attribute_value as model,
            shape_attr.attribute_value as shape,
            length_attr.attribute_value as length,
            width_attr.attribute_value as width,
            color_attr.attribute_value as color,
            color_attr.attribute as color_type,
            jav.abbr as color_abbr,
            i.variant_of,
            COALESCE(i.odd_cloth, 0) as odd_cloth,
            COALESCE(i.even_cloth, 0) as even_cloth,
            COALESCE(i.minor_cloth, 0) as minor_cloth
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
        LEFT JOIN `tabItem Variant Attribute` model_attr ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
        LEFT JOIN `tabItem Variant Attribute` shape_attr ON i.name = shape_attr.parent AND shape_attr.attribute = 'شکل'
        LEFT JOIN `tabItem Variant Attribute` length_attr ON i.name = length_attr.parent AND length_attr.attribute = 'طول'
        LEFT JOIN `tabItem Variant Attribute` width_attr ON i.name = width_attr.parent AND width_attr.attribute = 'عرض'
        LEFT JOIN `tabItem Variant Attribute` color_attr ON i.name = color_attr.parent AND color_attr.attribute IN ('رنگ بدنه', 'رنگ چوب')
        LEFT JOIN `tabItem Attribute Value` jav ON color_attr.attribute_value = jav.attribute_value AND color_attr.attribute = jav.parent
        WHERE (i.variant_of IN {0} OR (i.item_group = 'محصولات' AND (i.item_name LIKE '%%نیمکت%%' OR i.item_name LIKE '%%پاف%%')))
          AND i.show_on_site = 1
        ORDER BY i.creation DESC
    """.format(v_list_str)
    
    items = frappe.db.sql(query, (price_list or '',), as_dict=True)

    # 2. Fetch item images in bulk with tags (prioritize 'کاور')
    item_names = list(set(itm.item_name for itm in items if itm.item_name))
    image_lookup = {}
    if item_names:
        ph = ','.join(['%s'] * len(item_names))
        files = frappe.db.sql(f"""
            SELECT attached_to_name, file_url, custom_tag, name
            FROM `tabFile`
            WHERE attached_to_doctype = 'Item' AND attached_to_name IN ({ph})
              AND (file_url LIKE '%%.jpg' OR file_url LIKE '%%.jpeg' OR file_url LIKE '%%.png' OR file_url LIKE '%%.webp')
            ORDER BY CASE WHEN custom_tag = 'کاور' THEN 0 ELSE 1 END, creation ASC
        """, tuple(item_names), as_dict=True)
        for f in files:
            image_lookup.setdefault(f.attached_to_name, []).append({
                "file_url": f.file_url.replace('/private/files/', '/files/'),
                "custom_tag": f.custom_tag
            })

    # Group by model + shape + dimensions
    models = {}
    for itm in items:
        base_model = itm.model
        if not base_model:
            full_name = itm.item_name or ""
            base_model = full_name.split(' - ')[0].split(' مدل ')[0].strip()
        
        shape_term = itm.shape or ""
        length_term = itm.length or ""
        width_term = itm.width or ""
        
        if not length_term or not width_term:
            full_name = itm.item_name or ""
            import re
            m = re.search(r'طول\s+(\d+)\s+عرض\s+(\d+)', full_name)
            if m:
                length_term = f"طول {m.group(1)} سم"
                width_term = f"عرض {m.group(2)} سم"
        
        prefix = ""
        full_name = itm.item_name or ""
        if "نیمکت" in full_name:
            prefix = "نیمکت"
        elif "پاف" in full_name:
            prefix = "پاف"
        
        m_name = base_model
        if prefix and prefix not in m_name:
            m_name = f"{prefix} {m_name}"

        if shape_term: m_name += f" {shape_term}"
        
        if not m_name:
            m_name = itm.item_name or itm.item_code
            
        group_key = m_name
        if length_term: group_key += f" {length_term}"
        if width_term: group_key += f" {width_term}"

        if group_key not in models:
            models[group_key] = {
                "name": m_name,
                "display_name": m_name,
                "image": None,
                "images": [],
                "colors": {},
                "odd_cloth": float(itm.odd_cloth or 0),
                "even_cloth": float(itm.even_cloth or 0),
                "minor_cloth": float(itm.minor_cloth or 0),
                "length": length_term,
                "width": width_term,
                "shape": shape_term,
                "all_images": [],
                "all_body_colors": set(),
                "all_wood_colors": set(),
                "all_heights": set()
            }
        
        item_imgs = image_lookup.get(itm.item_name, [])
        cover_img = next((img["file_url"] for img in item_imgs if img["custom_tag"] == "کاور"), None)
        main_img = cover_img or (item_imgs[0]["file_url"] if item_imgs else itm.image)
        
        if main_img:
            m_img = main_img.replace('/private/files/', '/files/')
            if not models[group_key]["image"] or cover_img:
                models[group_key]["image"] = m_img
        
        for img in item_imgs:
            f_url = img["file_url"].replace('/private/files/', '/files/')
            if f_url not in [x["file_url"] for x in models[group_key]["all_images"]]:
                models[group_key]["all_images"].append({"file_url": f_url, "custom_tag": img["custom_tag"]})

        color_name = itm.color_abbr or itm.color or "نامشخص"
        color_type = itm.color_type
        
        if color_name not in models[group_key]["colors"]:
            is_wood = color_type == 'رنگ چوب'
            found_variant = {
                "item_code": itm.item_code,
                "raw_price": itm.price_list_rate,
                "formatted_price": fmt_toman(itm.price_list_rate),
                "odd_cloth": float(itm.odd_cloth or 0),
                "even_cloth": float(itm.even_cloth or 0),
                "minor_cloth": float(itm.minor_cloth or 0),
                "abbr": itm.color_abbr,
                "full_color_name": itm.color
            }
            models[group_key]["colors"][color_name] = {
                "name": color_name,
                "is_wood": is_wood,
                "variant": found_variant
            }
            models[group_key]["odd_cloth"] = max(models[group_key]["odd_cloth"], float(itm.odd_cloth or 0))
            models[group_key]["even_cloth"] = max(models[group_key]["even_cloth"], float(itm.even_cloth or 0))
            models[group_key]["minor_cloth"] = max(models[group_key]["minor_cloth"], float(itm.minor_cloth or 0))
            
            if is_wood:
                models[group_key]["all_wood_colors"].add(color_name)
            else:
                models[group_key]["all_body_colors"].add(color_name)
        
    results = []
    for m_key in models:
        models[m_key]["all_body_colors"] = list(models[m_key]["all_body_colors"])
        models[m_key]["all_wood_colors"] = list(models[m_key]["all_wood_colors"])
        models[m_key]["all_heights"] = sorted(list(models[m_key]["all_heights"]))
        models[m_key]["images"] = list(models[m_key]["all_images"])
        if not models[m_key]["image"] and models[m_key]["images"]:
            models[m_key]["image"] = models[m_key]["images"][0].get("file_url")
        
        sorted_colors = []
        for c_name in sorted(models[m_key]["colors"].keys()):
            sorted_colors.append(models[m_key]["colors"][c_name])
        models[m_key]["colors"] = sorted_colors
        del models[m_key]["all_images"]
        results.append(models[m_key])
        
    return results

def fmt_toman(rial_price):
    if not rial_price: return "۰"
    toman = int(rial_price / 10)
    s = str(toman)
    formatted = ",".join([s[::-1][i:i+3] for i in range(0, len(s), 3)])[::-1]
    persian = {'0':'۰','1':'۱','2':'۲','3':'۳','4':'۴','5':'۵','6':'۶','7':'۷','8':'۸','9':'۹'}
    for en, fa in persian.items():
        formatted = formatted.replace(en, fa)
    return formatted
