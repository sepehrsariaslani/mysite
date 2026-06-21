"""
Dining Chairs Page Controller - صندلی ناهارخوری
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

    body_chairs = get_chairs_by_type("صندلی ناهارخوری", price_list_param)
    # Filter wood_chairs to be zero for now if they are the same category, 
    # OR better yet, use get_chairs_by_type and then partition by color_type.
    # Actually, let's keep the existing logic but both call the same name filter,
    # then we split them in the frontend or here.
    
    # Let's fetch all "صندلی ناهارخوری" and split them by their variants' colors.
    all_dining = get_chairs_by_type("صندلی ناهارخوری", price_list_param)
    
    body_chairs = [m for m in all_dining if any(not c.get("is_wood") for c in m.get("colors", []))]
    wood_chairs = [m for m in all_dining if any(c.get("is_wood") for c in m.get("colors", []))]
    cloth_groups = get_cloth_groups(price_list_param)

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
            height_attr.attribute_value as height,
            i.variant_of,
            COALESCE(i.odd_cloth, 0) as odd_cloth,
            COALESCE(i.even_cloth, 0) as even_cloth,
            COALESCE(i.minor_cloth, 0) as minor_cloth
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
        LEFT JOIN `tabItem Variant Attribute` model_attr ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
        LEFT JOIN `tabItem Variant Attribute` color_attr ON i.name = color_attr.parent AND color_attr.attribute IN ('رنگ بدنه', 'رنگ چوب')
        LEFT JOIN `tabItem Variant Attribute` height_attr ON i.name = height_attr.parent AND height_attr.attribute = 'ارتفاع'
        WHERE (i.variant_of IN ('صندلی اپن', 'صندلی ناهارخوری', 'کلاف چوبی رنگ شده') OR i.item_group = 'محصولات')
          AND i.item_name LIKE %s
          AND i.show_on_site = 1
        ORDER BY i.creation DESC
    """
    # Use variant_of as a name filter if it's not a generic category
    name_filter = f"%{variant_of}%"
    items = frappe.db.sql(query, (price_list or '', name_filter), as_dict=True)

    # Group by model
    models = {}
    for itm in items:
        # Extract a clean model name
        m_name = itm.model
        if not m_name:
            # Fallback extraction from item_name
            full_name = itm.item_name or ""
            
            # If variant_of (search term) is in the name, use it!
            if variant_of and variant_of in full_name:
                m_name = variant_of
            else:
                # Remove common prefixes
                for prefix in ["صندلی اپن مدل ", "صندلی اپن ", "صندلی ناهارخوری مدل ", "صندلی ناهارخوری ", "کلاف چوبی رنگ شده صندلی اپن ", "کلاف چوبی رنگ شده "]:
                    if full_name.startswith(prefix):
                        full_name = full_name[len(prefix):]
                        break
                # Use first word or until first hyphen
                m_name = full_name.split(' - ')[0].split(' مدل ')[0].strip()
        
        if not m_name:
            m_name = itm.item_name or itm.item_code

        if m_name not in models:
            models[m_name] = {
                "name": m_name,
                "display_name": m_name,
                "image": itm.image,
                "colors": {},
                "all_images": set(),
                "all_body_colors": set(),
                "all_wood_colors": set(),
                "all_heights": set(),
                "odd_cloth": float(itm.odd_cloth or 0),
                "even_cloth": float(itm.even_cloth or 0),
                "minor_cloth": float(itm.minor_cloth or 0)
            }
        
        if itm.image:
            img_path = itm.image.replace('/private/files/', '/files/')
            models[m_name]["all_images"].add(img_path)
            if not models[m_name]["image"]:
                models[m_name]["image"] = img_path

        color_name = itm.color or "نامشخص"
        color_type = itm.color_type
        
        if color_name not in models[m_name]["colors"]:
            is_wood = color_type == 'رنگ چوب'
            models[m_name]["colors"][color_name] = {
                "name": color_name,
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
        m["images"] = [{"file_url": img} for img in m["all_images"]]
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
