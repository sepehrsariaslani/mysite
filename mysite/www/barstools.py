"""
Barstools Page Controller - صندلی اپن
Fetches BodyColorChairs and WoodColorChairs for the Vue frontend.
"""

import frappe
import json
from mysite.www.cloth import get_cloth_groups

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

    # Fetch only "صندلی اپن"
    all_barstools = get_chairs_by_type("صندلی اپن", price_list_param)
    
    # Split by color capability
    body_chairs = [m for m in all_barstools if any(not c.get("is_wood") for c in m.get("colors", []))]
    wood_chairs = [m for m in all_barstools if any(c.get("is_wood") for c in m.get("colors", []))]
    cloth_groups = get_cloth_groups("Standard Selling") # Strictly use Standard Selling for fabrics

    # Extract available models for filtering
    available_models = sorted(list(set(c["name"] for c in body_chairs + wood_chairs)))
    
    # Extract available colors
    body_colors = []
    wood_colors = []
    seen_body = set()
    seen_wood = set()
    
    for c in body_chairs:
        for clr in c.get("colors", []):
            if clr["name"] not in seen_body:
                body_colors.append({"label": clr["name"], "value": clr["name"]})
                seen_body.add(clr["name"])
                
    for c in wood_chairs:
        for clr in c.get("colors", []):
            if clr["name"] not in seen_wood:
                wood_colors.append({"label": clr["name"], "value": clr["name"]})
                seen_wood.add(clr["name"])

    return {
        "BodyColorChairs": body_chairs,
        "WoodColorChairs": wood_chairs,
        "AvailableModels": available_models,
        "AvailableBodyColors": body_colors,
        "AvailableWoodColors": wood_colors,
        "ClothGroups": cloth_groups,
        "site_name": frappe.local.site,
    }

def get_chairs_by_type(variant_of, price_list):
    query = """
        SELECT 
            i.name as item_name,
            i.item_code,
            i.item_name as display_name,
            i.image,
            COALESCE(ip.price_list_rate, 0) as price_list_rate,
            model_attr.attribute_value as model,
            color_attr.attribute_value as color,
            color_attr.attribute as color_type,
            jav.abbr as color_abbr,
            height_attr.attribute_value as height,
            i.variant_of,
            COALESCE(i.odd_cloth, 0) as odd_cloth,
            COALESCE(i.even_cloth, 0) as even_cloth,
            COALESCE(i.minor_cloth, 0) as minor_cloth
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
        LEFT JOIN `tabItem Variant Attribute` model_attr ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
        LEFT JOIN `tabItem Variant Attribute` color_attr ON i.name = color_attr.parent AND color_attr.attribute IN ('رنگ بدنه', 'رنگ چوب')
        LEFT JOIN `tabItem Attribute Value` jav ON color_attr.attribute_value = jav.attribute_value AND color_attr.attribute = jav.parent
        LEFT JOIN `tabItem Variant Attribute` height_attr ON i.name = height_attr.parent AND height_attr.attribute = 'ارتفاع'
        WHERE (i.variant_of IN ('صندلی اپن', 'صندلی ناهارخوری', 'کلاف چوبی رنگ شده') OR i.item_group = 'محصولات')
          AND i.item_name LIKE %s
          AND i.show_on_site = 1
        ORDER BY i.creation DESC
    """
    # Use variant_of as a name filter if it's not a generic category
    name_filter = f"%{variant_of}%"
    items = frappe.db.sql(query, (price_list or '', name_filter), as_dict=True)

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

    # Group by model
    models = {}
    for itm in items:
        # Extract a clean model name
        m_name = itm.model
        if not m_name:
            full_name = itm.item_name or ""
            if variant_of and variant_of in full_name:
                m_name = variant_of
            else:
                for prefix in ["صندلی اپن مدل ", "صندلی اپن ", "صندلی ناهارخوری مدل ", "صندلی ناهارخوری ", "کلاف چوبی رنگ شده صندلی اپن ", "کلاف چوبی رنگ شده "]:
                    if full_name.startswith(prefix):
                        full_name = full_name[len(prefix):]
                        break
                m_name = full_name.split(' - ')[0].split(' مدل ')[0].strip()
        
        if not m_name:
            m_name = itm.item_name or itm.item_code

        if m_name not in models:
            models[m_name] = {
                "name": m_name,
                "display_name": m_name,
                "image": None,
                "max_price": 0,
                "colors": {},
                "all_images": [],
                "all_body_colors": set(),
                "all_wood_colors": set(),
                "all_heights": set(),
                "odd_cloth": float(itm.odd_cloth or 0),
                "even_cloth": float(itm.even_cloth or 0),
                "minor_cloth": float(itm.minor_cloth or 0)
            }
        
        # Determine Main Image (Prioritize 'کاور' tag)
        item_imgs = image_lookup.get(itm.item_name, [])
        cover_img = next((img["file_url"] for img in item_imgs if img["custom_tag"] == "کاور"), None)
        main_img = cover_img or (item_imgs[0]["file_url"] if item_imgs else itm.image)
        
        if main_img:
            m_img = main_img.replace('/private/files/', '/files/')
            # If we find a 'کاور' image, it's the ultimate priority
            if not models[m_name]["image"] or (cover_img and 'کاور' in [img.get("custom_tag") for img in item_imgs]):
                 models[m_name]["image"] = m_img
        
        for img in item_imgs:
            f_url = img["file_url"].replace('/private/files/', '/files/')
            if f_url not in [x["file_url"] for x in models[m_name]["all_images"]]:
                models[m_name]["all_images"].append({"file_url": f_url, "custom_tag": img["custom_tag"]})

        # Tracking Max Price (Highest height price)
        current_price = float(itm.price_list_rate or 0)
        if current_price > models[m_name]["max_price"]:
            models[m_name]["max_price"] = current_price

        color_name = itm.color_abbr or itm.color or "نامشخص"
        color_type = itm.color_type
        
        if color_name not in models[m_name]["colors"]:
            is_wood = color_type == 'رنگ چوب'
            models[m_name]["colors"][color_name] = {
                "name": color_name,
                "full_name": itm.color,
                "is_wood": is_wood,
                "variant": {
                    "item_code": itm.item_code,
                    "raw_price": itm.price_list_rate,
                    "formatted_price": fmt_toman(itm.price_list_rate),
                    "odd_cloth": float(itm.odd_cloth or 0),
                    "even_cloth": float(itm.even_cloth or 0),
                    "minor_cloth": float(itm.minor_cloth or 0)
                }
            }
            if is_wood:
                models[m_name]["all_wood_colors"].add(color_name)
            else:
                models[m_name]["all_body_colors"].add(color_name)
        
        if itm.height:
            models[m_name]["all_heights"].add(itm.height)
        models[m_name]["odd_cloth"] = max(models[m_name]["odd_cloth"], float(itm.odd_cloth or 0))
        models[m_name]["even_cloth"] = max(models[m_name]["even_cloth"], float(itm.even_cloth or 0))
        models[m_name]["minor_cloth"] = max(models[m_name]["minor_cloth"], float(itm.minor_cloth or 0))
        
    # Finalize models
    final_models = []
    for m in models.values():
        m["colors"] = list(m["colors"].values())
        
        # Sort colors to ensure a predictable "first" color for the card
        # Prioritize wood colors if any
        m["colors"].sort(key=lambda x: (not x["is_wood"], x["name"]))

        # Override color variant price with model's max price for initial display
        if m["colors"]:
            # Note: The user wants the max height price to be the one shown on cards.
            m["colors"][0]["variant"]["raw_price"] = m["max_price"]
            m["colors"][0]["variant"]["formatted_price"] = fmt_toman(m["max_price"])

        m["images"] = m["all_images"]
        m["all_body_colors"] = list(m["all_body_colors"])
        m["all_wood_colors"] = list(m["all_wood_colors"])
        m["all_heights"] = sorted(list(m["all_heights"]))
        del m["all_images"]
        final_models.append(m)
        
    return final_models

def fmt_toman(rial_price):
    if not rial_price: return "۰"
    toman = int(rial_price / 10)
    s = str(toman)
    formatted = ",".join([s[::-1][i:i+3] for i in range(0, len(s), 3)])[::-1]
    # Convert to Persian digits
    persian = {'0':'۰','1':'۱','2':'۲','3':'۳','4':'۴','5':'۵','6':'۶','7':'۷','8':'۸','9':'۹'}
    for en, fa in persian.items():
        formatted = formatted.replace(en, fa)
    return formatted
