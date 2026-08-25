# ==========================================================
# Page Data Script - فقط مبلمان و پارچه‌ها
# نسخه بهینه‌شده - فقط NestedSofaProducts و ClothGroups
# Version: 2.3 - Fixed related products grouping by dimensions
# ==========================================================

def safe_get(obj, key, default=""):
    """
    دریافت مقدار از dict با تبدیل None به رشته خالی
    """
    value = obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)
    return value if value is not None else default

def to_persian_digits(number):
    """Convert English/Arabic digits to Persian digits"""
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    text = str(number)
    for english, persian in persian_digits.items():
        text = text.replace(english, persian)
    return text

def clean_bundle_name(name):
    """Remove wood color from item name"""
    WOOD_COLORS = [
        "خودرنگ", "رنگ فندقی روشن", "رنگ گردویی روشن",
        "رنگ فندوقی تیره", "رنگ گردویی تیره", "چوب مشکی",
        "رنگ عسلی روشن", "رنگ عسلی تیره", "چوب سفید"
    ]
    n = name or ''
    for color in WOOD_COLORS:
        if n.endswith(color):
            n = n[: -len(color)].strip()
    return n

def get_wood_color_fields(wood_color):
    """رنگ چوب فارسی را به فیلدهای boolean انگلیسی تبدیل می‌کند"""
    wood_color_mapping = {
        "خودرنگ": "wood_color",
        "رنگ فندقی روشن": "light_hazelnut",
        "رنگ گردویی روشن": "light_walnut",
        "رنگ فندوقی تیره": "dark_hazelnut",
        "رنگ گردویی تیره": "dark_walnut",
        "چوب مشکی": "black_wood",
        "رنگ عسلی روشن": "light_honey",
        "رنگ عسلی تیره": "dark_honey",
        "چوب سفید": "white_wood"
    }
    
    fields = {}
    if wood_color and wood_color in wood_color_mapping:
        field_name = wood_color_mapping[wood_color]
        fields[field_name] = True
    
    return fields

# ==========================================================
# دریافت پارامترها
# ==========================================================
price_list_param = frappe.form_dict.get("price_list")
sofa_models = []  # می‌توانید فیلتر اضافه کنید
sofa_modules = []  # می‌توانید فیلتر اضافه کنید

# پیدا کردن لیست قیمت پیش‌فرض
if not price_list_param:
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
    except Exception:
        default_pl = None
    
    if default_pl:
        price_list_param = default_pl
    else:
        default_price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")
        if default_price_list:
            price_list_param = default_price_list

# ==========================================================
# بخش ۱: بارگذاری NestedSofaProducts (مبلمان)
# ==========================================================

# Build WHERE clause for filtering
where_conditions = ["i.variant_of='مبل'", "i.item_group='محصولات'", "i.show_on_site = 1", "no_structure=0"]
params = []

if sofa_models:
    model_placeholders = ','.join(['%s'] * len(sofa_models))
    where_conditions.append(f"""
        i.name IN (
            SELECT DISTINCT iva.parent
            FROM `tabItem Variant Attribute` iva
            WHERE iva.attribute = 'مدل محصول' 
            AND iva.attribute_value IN ({model_placeholders})
        )
    """)
    params.extend(sofa_models)

if sofa_modules:
    module_placeholders = ','.join(['%s'] * len(sofa_modules))
    where_conditions.append(f"""
        i.name IN (
            SELECT DISTINCT iva.parent
            FROM `tabItem Variant Attribute` iva
            WHERE iva.attribute = 'ماژول' 
            AND iva.attribute_value IN ({module_placeholders})
        )
    """)
    params.extend(sofa_modules)

where_clause = ' AND '.join(where_conditions)

# Main query to get sofa data
sofa_query = f"""
    SELECT 
        i.name as item_name,
        i.item_code,
        i.item_name as display_name,
        i.description,
        i.image,
        i.creation,
        COALESCE(bin.projected_qty, 0) as projected_qty,
        COALESCE(i.odd_cloth, 0) as odd_cloth,
        COALESCE(i.even_cloth, 0) as even_cloth,
        COALESCE(i.minor_cloth, 0) as minor_cloth,
        COALESCE(i.cushion_cloth, 0) as cushion_cloth,
        COALESCE(ip.price_list_rate, 0) as price_list_rate,
        model_attr.attribute_value as model,
        module_attr.attribute_value as module,
        feature_attr.attribute_value as module_feature,
        length_attr.attribute_value as length_value,
        COALESCE(length_abbr.abbr, length_attr.attribute_value) as length,
        width_attr.attribute_value as width_value,
        COALESCE(width_abbr.abbr, width_attr.attribute_value) as width,
        height_attr.attribute_value as height_value,
        COALESCE(height_abbr.abbr, height_attr.attribute_value) as height,
        wood_color_attr.attribute_value as wood_color,
        body_color_attr.attribute_value as body_color,
        i.yindex as yindex
    FROM `tabItem` i
    LEFT JOIN `tabBin` bin ON i.name = bin.item_code
    LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
    LEFT JOIN `tabItem Variant Attribute` model_attr ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
    LEFT JOIN `tabItem Variant Attribute` module_attr ON i.name = module_attr.parent AND module_attr.attribute = 'ماژول'
    LEFT JOIN `tabItem Variant Attribute` feature_attr ON i.name = feature_attr.parent AND feature_attr.attribute = 'ویژگی ماژول'
    LEFT JOIN `tabItem Variant Attribute` length_attr ON i.name = length_attr.parent AND length_attr.attribute = 'طول'
    LEFT JOIN `tabItem Attribute Value` length_abbr ON length_attr.attribute = length_abbr.parent AND length_attr.attribute_value = length_abbr.attribute_value
    LEFT JOIN `tabItem Variant Attribute` width_attr ON i.name = width_attr.parent AND width_attr.attribute = 'عرض'
    LEFT JOIN `tabItem Attribute Value` width_abbr ON width_attr.attribute = width_abbr.parent AND width_attr.attribute_value = width_abbr.attribute_value
    LEFT JOIN `tabItem Variant Attribute` height_attr ON i.name = height_attr.parent AND height_attr.attribute = 'ارتفاع'
    LEFT JOIN `tabItem Attribute Value` height_abbr ON height_attr.attribute = height_abbr.parent AND height_attr.attribute_value = height_abbr.attribute_value
    LEFT JOIN `tabItem Variant Attribute` wood_color_attr ON i.name = wood_color_attr.parent AND wood_color_attr.attribute = 'رنگ چوب'
    LEFT JOIN `tabItem Variant Attribute` body_color_attr ON i.name = body_color_attr.parent AND body_color_attr.attribute = 'رنگ بدنه'
    WHERE {where_clause}
    ORDER BY i.creation DESC
"""

params.append(price_list_param or '')
sofas_raw = frappe.db.sql(sofa_query, params, as_dict=True)

# واکشی abbr برای attribute values
attribute_names = [
    'مدل محصول', 'ماژول', 'ویژگی ماژول', 'طول', 'عرض', 'ارتفاع', 'رنگ چوب', 'رنگ بدنه'
]
abbr_map = {}
for attr in attribute_names:
    rows = frappe.db.sql(
        '''SELECT parent, attribute_value, abbr FROM `tabItem Attribute Value` WHERE parent=%s''',
        (attr,), as_dict=True
    )
    for row in rows:
        abbr_map[(attr, row['attribute_value'])] = row.get('abbr')

# Process each sofa item
sofas = []
for sofa in sofas_raw:
    # Calculate price
    price = int(sofa.price_list_rate / 10) if sofa.price_list_rate and sofa.price_list_rate > 0 else 0
    
    # Format price
    if price > 0:
        price_str = str(price)
        formatted_price = ",".join([price_str[::-1][i:i + 3] for i in range(0, len(price_str), 3)])[::-1]
        formatted_price = to_persian_digits(formatted_price)
    else:
        formatted_price = "تماس بگیرید"
    
    # Get images for this item
    images = []
    if sofa.item_name:
        # Generate name variants (with space and dash)
        name_variants = {sofa.item_name}
        name = sofa.item_name
        indices = [i for i, c in enumerate(name) if c in [' ', '-']]
        n = len(indices)
        for bits in range(2 ** n):
            chars = list(name)
            for j in range(n):
                if (bits >> j) & 1:
                    chars[indices[j]] = '-' if chars[indices[j]] == ' ' else ' '
            name_variants.add(''.join(chars))
        
        # Get images
        if name_variants:
            placeholders = ','.join(['%s'] * len(name_variants))
            images_query = f"""
                SELECT 
                    name, file_name, file_url, file_size, file_type,
                    attached_to_name, custom_yindex, custom_alt_text, custom_tag
                FROM `tabFile`
                WHERE attached_to_doctype = 'Item'
                    AND attached_to_name IN ({placeholders})
                    AND is_private = 0
                    AND (file_type LIKE 'image%%' OR file_url LIKE '%%.jpg' OR file_url LIKE '%%.jpeg' 
                        OR file_url LIKE '%%.png' OR file_url LIKE '%%.gif' OR file_url LIKE '%%.webp' 
                        OR file_url LIKE '%%.svg')
                ORDER BY CAST(COALESCE(custom_yindex, 0) AS SIGNED) ASC
            """
            files = frappe.db.sql(images_query, tuple(name_variants), as_dict=True)
            seen_urls = set()
            for img in files:
                if img.file_url and img.file_url not in seen_urls:
                    images.append({
                        "name": img.name,
                        "file_name": img.file_name,
                        "file_url": img.file_url,
                        "file_size": img.file_size,
                        "file_type": img.file_type,
                        "attached_to_name": img.attached_to_name,
                        "custom_yindex": img.custom_yindex,
                        "custom_alt_text": img.custom_alt_text,
                        "custom_tag": img.custom_tag,
                        "cover": True if img.custom_tag == "کاور" else False,
                        "dimentions": True if img.custom_tag == "اندازه" else False,
                        "gallary": True if img.custom_tag == "گالری" else False,
                        "icon": True if img.custom_tag == "آیکون" else False
                    })
                    seen_urls.add(img.file_url)
    
    odd_cloth_val = float(sofa.odd_cloth) if sofa.odd_cloth and sofa.odd_cloth > 0 else 0
    even_cloth_val = float(sofa.even_cloth) if sofa.even_cloth and sofa.even_cloth > 0 else 0
    
    # Add processed sofa to list
    sofa_item = sofa.copy()
    
    # مقداردهی ویژگی‌ها با abbr
    sofa_item['model'] = abbr_map.get(('مدل محصول', sofa.get('model'))) or sofa.get('model')
    sofa_item['module'] = abbr_map.get(('ماژول', sofa.get('module'))) or sofa.get('module')
    sofa_item['module_feature'] = abbr_map.get(('ویژگی ماژول', sofa.get('module_feature'))) or sofa.get('module_feature')
    sofa_item['length'] = sofa.get('length')
    sofa_item['width'] = sofa.get('width')
    sofa_item['height'] = sofa.get('height')
    sofa_item['wood_color'] = abbr_map.get(('رنگ چوب', sofa.get('wood_color'))) or sofa.get('wood_color')
    sofa_item['body_color'] = abbr_map.get(('رنگ بدنه', sofa.get('body_color'))) or sofa.get('body_color')
    
    sofa_item.update({
        "Price": price,
        "formatted_Price": formatted_price,
        "images": images,
        "stock_qty": sofa.get('projected_qty', 0),
        "odd_cloth": odd_cloth_val,
        "even_cloth": even_cloth_val
    })
    sofas.append(sofa_item)

# واکشی Product Groups و باندل‌ها
ProductGroups = frappe.db.get_all(
    "Product Group",
    fields=["name", "product_model", "description", "main_photo", "icon_photo", "yindex"],
    order_by="creation desc"
)

# واکشی قیمت‌های باندل‌ها
all_prices = frappe.db.get_all(
    "Item Price",
    filters={"price_list": price_list_param},
    fields=["item_code", "price_list_rate"]
)

# آماده‌سازی داده برای هر گروه
for group in ProductGroups:
    group_items = frappe.db.get_all(
        "Product Group Item",
        filters={"parent": group["name"]},
        fields=["product_bundel", "sofa_cloth", "cushion_cloth"]
    )

    bundle_names = [item["product_bundel"] for item in group_items if item["product_bundel"]]

    bundles = []
    if bundle_names:
        placeholders = ', '.join(['%s'] * len(bundle_names))
        bundle_query = f"""
            SELECT 
                pb.name, pb.new_item_code, pb.description, pb.disabled,
                pb.show_on_site, pb.cover_photo, pb.yindex,
                COALESCE(i.odd_cloth, 0) as odd_fabric,
                COALESCE(i.even_cloth, 0) as even_fabric,
                COALESCE(i.cushion_cloth, 0) as cushion_fabric,
                COALESCE(i.minor_cloth, 0) as minor_fabric
            FROM `tabProduct Bundle` pb
            LEFT JOIN `tabItem` i ON pb.name = i.name
            WHERE pb.name IN ({placeholders}) AND pb.show_on_site = 1
        """
        bundles = frappe.db.sql(bundle_query, tuple(bundle_names), as_dict=True)

        for bundle in bundles:
            price_row = None
            for p in all_prices:
                if p["item_code"] == bundle["name"]:
                    price_row = p
                    break

            price = price_row["price_list_rate"] if price_row else 0
            bundle["bundle_price"] = int(price / 10) if price > 0 else 0

            if bundle["bundle_price"] > 0:
                formatted = ",".join([str(bundle["bundle_price"])[::-1][i:i + 3] for i in range(0, len(str(bundle["bundle_price"])), 3)])[::-1]
                bundle["bundle_formatted_price"] = to_persian_digits(formatted)
            else:
                bundle["bundle_formatted_price"] = "۰"

            bundle["is_available"] = not bundle.get("disabled", 0)
            bundle["show_on_website"] = bundle.get("show_on_site", 0)
            bundle["has_cover_photo"] = bool(bundle.get("cover_photo"))
            bundle["bundle_name"] = bundle["name"]
            bundle["bundle_code"] = bundle["new_item_code"] if bundle.get("new_item_code") else bundle["name"]
            bundle["bundle_description"] = bundle.get("description", "")
            bundle["bundle_cover_photo"] = bundle.get("cover_photo")
            bundle["yindex"] = bundle.get("yindex")
            
            odd = bundle.get("odd_fabric", 0) or 0
            even = bundle.get("even_fabric", 0) or 0
            cushion = bundle.get("cushion_fabric", 0) or 0
            minor = bundle.get("minor_fabric", 0) or 0
            
            bundle["total_fabric"] = odd + cushion + minor
            bundle["is_minor"] = True if minor else False

        for item in group_items:
            bundle_data = None
            for b in bundles:
                if b["name"] == item["product_bundel"]:
                    bundle_data = b
                    break
            item["product_bundel_info"] = bundle_data or {}

    group["group_items"] = group_items
    group["product_bundles"] = bundles
    group["product_group_name"] = group["name"]
    if "yindex" not in group:
        group["yindex"] = None

# ساخت lookup برای Product Groups
product_group_lookup = {g['product_model']: g for g in ProductGroups}

# گروه‌بندی مبل‌ها بر اساس مدل و ماژول
sofa_grouped = {}
for sofa in sofas:
    model = sofa.get('model') or ''
    module = sofa.get('module') or ''
    key = (model, module)
    if key not in sofa_grouped:
        sofa_grouped[key] = []
    sofa_grouped[key].append(sofa)

integrated_sofa_products = []
for (model, module), group_sofas in sofa_grouped.items():
    max_price_sofa = max(group_sofas, key=lambda s: s.get('Price') or 0)
    wood_colors = list(set([s.get('wood_color') for s in group_sofas if s.get('wood_color') and s.get('wood_color') != '']))
    
    group = product_group_lookup.get(model)
    sofa_item = max_price_sofa.copy()
    sofa_item['all_wood_colors'] = wood_colors
    
    if group:
        sofa_item['has_product_group'] = True
        sofa_item['product_group_name'] = group.get('product_group_name', model)
        sofa_item['product_model'] = group.get('product_model', model)
        sofa_item['product_description'] = group.get('description', '')
        sofa_item['main_photo'] = group.get('main_photo')
        sofa_item['icon_photo'] = group.get('icon_photo')
        
        bundles = []
        for item in group.get('group_items', []):
            if item.get('product_bundel_info'):
                bundles.append(item['product_bundel_info'])
        sofa_item['bundles'] = bundles
        sofa_item['bundles_count'] = len(bundles)
        sofa_item['available_bundles_count'] = len([b for b in bundles if not b.get('disabled', 0)])
        sofa_item.pop('product_bundles', None)
        sofa_item.pop('group_items', None)
    else:
        sofa_item['has_product_group'] = False
        sofa_item['product_group_name'] = None
        sofa_item['product_model'] = model
        sofa_item['product_description'] = ''
        sofa_item['main_photo'] = None
        sofa_item['icon_photo'] = None
        sofa_item['bundles'] = []
        sofa_item['bundles_count'] = 0
        sofa_item['available_bundles_count'] = 0
        sofa_item.pop('product_bundles', None)
        sofa_item.pop('group_items', None)
    
    integrated_sofa_products.append(sofa_item)

# ساخت ساختار نستد نهایی برای مدل‌های مبل
all_models = set([sofa.get('model') or '' for sofa in sofas])

nested_sofa_products = []
for model_name in all_models:
    model_sofas = [sofa for sofa in sofas if (sofa.get('model') or '') == model_name]
    if not model_sofas:
        continue
    
    # عکس‌های مدل
    model_images = []
    seen_urls = set()
    for sofa in model_sofas:
        for img in sofa.get('images', []):
            if img['file_url'] not in seen_urls:
                model_images.append(img)
                seen_urls.add(img['file_url'])
    
    # ماژول‌ها
    modules = []
    module_groups = {}
    for sofa in model_sofas:
        module_name = sofa.get('module') or ''
        module_feature = sofa.get('module_feature') or ''
        length = sofa.get('length') or ''
        width = sofa.get('width') or ''
        height = sofa.get('height') or ''
        # کلید شامل: ماژول، ویژگی ماژول، طول، عرض، ارتفاع (رنگ چوب شامل نیست)
        key = (module_name, module_feature, length, width, height)
        if key not in module_groups:
            module_groups[key] = []
        module_groups[key].append(sofa)
    
    for (module_name, module_feature, length, width, height), items in module_groups.items():
        # رنگ چوب‌های مختلف در یک sofa_module قرار می‌گیرند
        # فقط بر اساس رنگ بدنه گروه‌بندی می‌کنیم (چون بقیه ویژگی‌ها قبلاً در key اصلی هستند)
        subgroups = {}
        for sofa in items:
            body_color = sofa.get('body_color') or ''
            # کلید فقط رنگ بدنه
            if body_color not in subgroups:
                subgroups[body_color] = []
            subgroups[body_color].append(sofa)
        
        modules_items = []
        all_images = []
        seen_urls = set()
        
        for body_color, group_items in subgroups.items():
            # پیدا کردن آیتم با بالاترین قیمت
            max_price_item = max(group_items, key=lambda s: s.get('Price') or 0)
            
            # جمع‌آوری تمام رنگ‌های چوب این گروه
            wood_colors = list(set([s.get('wood_color') for s in group_items if s.get('wood_color') and s.get('wood_color') != '']))
            item_copy = max_price_item.copy()
            item_copy['all_wood_colors'] = wood_colors
            
            standardized_item = {
                'item_name': item_copy.get('item_name') or "",
                'item_code': item_copy.get('item_code') or "",
                'display_name': item_copy.get('display_name') or item_copy.get('item_name') or "",
                'display_name_without_wood_color': clean_bundle_name(item_copy.get('item_name', '')),
                'description': item_copy.get('description', ''),
                'description_without_wood_color': clean_bundle_name(item_copy.get('description', '')),
                'image': item_copy.get('image') or "",
                'creation': item_copy.get('creation') or "",
                'projected_qty': item_copy.get('projected_qty', 0),
                'price_list_rate': item_copy.get('price_list_rate', 0),
                'model': item_copy.get('model') or "",
                'module': item_copy.get('module') or "",
                'module_feature': module_feature,
                'module_length': length,
                'module_width': width,
                'module_height': height,
                'module_diameter': "",
                'module_shape': "",
                'module_color': "",
                'wood_color': item_copy.get('wood_color') or "",
                'body_color': item_copy.get('body_color') or "",
                'odd_cloth': item_copy.get('odd_cloth', 0),
                'even_cloth': item_copy.get('even_cloth', 0),
                'minor_cloth': item_copy.get('minor_cloth', 0),
                'cushion_cloth': item_copy.get('cushion_cloth', 0),
                'Price': item_copy.get('Price', 0),
                'formatted_Price': item_copy.get('formatted_Price', 'تماس بگیرید'),
                'images': item_copy.get('images', []),
                'stock_qty': item_copy.get('stock_qty', 0),
                'yindex': item_copy.get('yindex') or "",
                'variant_of': 'مبل',
                'all_wood_colors': wood_colors,
                'is_minor': True if item_copy.get('minor_cloth', 0) else False
            }
            item_copy = standardized_item
            
            for s in group_items:
                for img in s.get('images', []):
                    if img['file_url'] not in seen_urls:
                        all_images.append(img)
                        seen_urls.add(img['file_url'])
            
            modules_items.append(item_copy)
        
        # محاسبه مقادیر پارچه
        odd_cloth_vals = [s.get('odd_cloth', 0) for s in items if s.get('odd_cloth') is not None]
        even_cloth_vals = [s.get('even_cloth', 0) for s in items if s.get('even_cloth') is not None]
        minor_cloth_vals = [s.get('minor_cloth', 0) for s in items if s.get('minor_cloth') is not None]
        cushion_cloth_vals = [s.get('cushion_cloth', 0) for s in items if s.get('cushion_cloth') is not None]
        
        odd_cloth_max = max(odd_cloth_vals) if odd_cloth_vals else 0
        even_cloth_max = max(even_cloth_vals) if even_cloth_vals else 0
        minor_cloth_max = max(minor_cloth_vals) if minor_cloth_vals else 0
        cushion_cloth_max = max(cushion_cloth_vals) if cushion_cloth_vals else 0
        
        yindexes = []
        for s in items:
            yidx = s.get('yindex')
            try:
                if yidx is not None:
                    yindexes.append(float(yidx))
            except Exception:
                pass
        module_yindex = sum(yindexes) / len(yindexes) if yindexes else None
        
        first_module_item_model = modules_items[0].get('model') if modules_items else model_name
        first_module_item_variant = 'مبل'
        
        module_obj = {
            'sofa_module_name': module_name,
            'sofa_module_type': 'مبل',
            'sofa_model': first_module_item_model,
            'sofa_product_type': first_module_item_variant,
            'sofa_length': length,
            'sofa_width': width,
            'sofa_height': height,
            'sofa_diameter': "",
            'sofa_shape': "",
            'sofa_odd_cloth': round(odd_cloth_max, 2),
            'sofa_even_cloth': round(even_cloth_max, 2),
            'sofa_minor_cloth': round(minor_cloth_max, 2),
            'sofa_cushion_cloth': round(cushion_cloth_max, 2),
            'is_minor': True if minor_cloth_max else False,
            'total_cloth_for_sofa': round(odd_cloth_max + minor_cloth_max, 2),
            'sofa_module_images': all_images,
            'sofa_module_items': modules_items,
            'sofa_yindex': module_yindex,
            'sofa_yindex_source': 'module_items_avg' if yindexes else ""
        }
        modules.append(module_obj)
    
    # مرتب‌سازی ماژول‌ها
    def yindex_sort_key(x):
        yidx = x.get("sofa_yindex") or x.get("yindex")
        try:
            return (0, int(yidx))
        except (TypeError, ValueError):
            return (1, 0)
    
    modules.sort(key=yindex_sort_key)
    
    # باندل‌های مدل
    bundles = []
    group_info = {}
    for g in ProductGroups:
        if g.get('product_model') == model_name:
            group_info = g
            break
    
    for item in group_info.get('group_items', []):
        if item.get('product_bundel_info'):
            bundles.append(item['product_bundel_info'])
    
    bundles.sort(key=yindex_sort_key)
    
    nested_sofa_products.append({
        'sofa_model_name': model_name,
        'sofa_route': f'sofas/{model_name}',
        'sofa_model_description': group_info.get('description', ''),
        'sofa_main_photo': group_info.get('main_photo') or "",
        'sofa_icon_photo': group_info.get('icon_photo') or "",
        'sofa_images': model_images,
        'sofa_modules': modules,
        'sofa_bundles': bundles,
        'sofa_bundles_count': len(bundles),
        'sofa_available_bundles_count': len([b for b in bundles if not b.get('disabled', 0)]),
        'sofa_yindex': group_info.get('yindex') or ""
    })

# ادغام باندل‌هایی که فقط در رنگ چوب فرق دارند
def extract_base_name_and_wood_color(bundle_name):
    WOOD_COLORS = [
        "خودرنگ", "رنگ فندقی روشن", "رنگ گردویی روشن",
        "رنگ فندوقی تیره", "رنگ گردویی تیره", "چوب مشکی",
        "رنگ عسلی روشن", "رنگ عسلی تیره", "چوب سفید"
    ]
    name = (bundle_name or '').strip()
    for color in WOOD_COLORS:
        if name.endswith(color):
            base = name[: -len(color)].strip()
            return base, color
    return name, None

for model in nested_sofa_products:
    all_items = []
    for module in model.get('sofa_modules', []):
        all_items.extend(module.get('sofa_module_items', []))
    
    bundle_groups = {}
    for bundle in model.get('sofa_bundles', []):
        result = extract_base_name_and_wood_color(bundle.get('name', ''))
        base_name = result[0]
        wood_color = result[1]
        if base_name not in bundle_groups:
            bundle_groups[base_name] = {'bundles': [], 'wood_colors': set()}
        bundle_groups[base_name]['bundles'].append(bundle)
        if wood_color:
            bundle_groups[base_name]['wood_colors'].add(wood_color)
    
    merged_bundles = []
    for base_name, group in bundle_groups.items():
        bundle_items = []
        bundle_texts = []
        for b in group['bundles']:
            bundle_texts.extend([
                (b.get('description') or ''),
                (b.get('bundle_description') or ''),
                (b.get('name') or ''),
                (b.get('bundle_name') or '')
            ])
        
        for item in all_items:
            item_name = (item.get('item_name') or '').strip()
            module_name = (item.get('module') or '').strip()
            found = False
            for text in bundle_texts:
                if (
                    (' ' + item_name + ' ' in ' ' + text + ' ') or
                    ('-' + item_name + '-' in '-' + text + '-') or
                    (module_name and ((' ' + module_name + ' ' in ' ' + text + ' ') or ('-' + module_name + '-' in '-' + text + '-')))
                ):
                    found = True
                    break
            if found:
                bundle_items.append(item)
        
        merged_bundle = group['bundles'][0].copy()
        merged_bundle['sofa_available_wood_colors'] = list(group['wood_colors'])
        merged_bundle['sofa_bundle_name'] = clean_bundle_name(merged_bundle.get('name', ''))
        merged_bundle['sofa_bundle_display_name'] = clean_bundle_name(merged_bundle.get('bundle_name', ''))
        merged_bundle['sofa_bundle_code'] = clean_bundle_name(merged_bundle.get('bundle_code', ''))
        
        original_bundle_name = merged_bundle.get('name', '')
        
        merged_bundle['name'] = merged_bundle['sofa_bundle_name']
        merged_bundle['new_item_code'] = merged_bundle['sofa_bundle_name']
        merged_bundle.pop('items', None)
        
        # واکشی آیتم‌های جدول باندل
        bundle_table_items = []
        try:
            bundle_table_items = frappe.db.get_all(
                "Product Bundle Item",
                filters={"parent": original_bundle_name},
                fields=["item_code", "qty", "uom"]
            )
        except Exception:
            bundle_table_items = []
        
        # Enrich bundle_table_items
        item_lookup = {item.get('item_code'): item for item in all_items}
        for entry in bundle_table_items:
            item_info = item_lookup.get(entry['item_code'])
            if not item_info:
                for s in sofas:
                    if s.get('item_code') == entry['item_code']:
                        item_info = s
                        break
            if item_info:
                entry.update({
                    'item_name': item_info.get('item_name'),
                    'display_name': item_info.get('display_name'),
                    'description': item_info.get('description'),
                    'image': item_info.get('image'),
                    'price_list_rate': item_info.get('price_list_rate'),
                    'Price': item_info.get('Price'),
                    'formatted_Price': item_info.get('formatted_Price'),
                    'model': item_info.get('model'),
                    'module': item_info.get('module'),
                    'module_feature': item_info.get('module_feature'),
                    'length': item_info.get('length'),
                    'width': item_info.get('width'),
                    'height': item_info.get('height'),
                    'wood_color': item_info.get('wood_color'),
                    'body_color': item_info.get('body_color'),
                    'images': item_info.get('images'),
                    'stock_qty': item_info.get('stock_qty'),
                    'all_wood_colors': item_info.get('all_wood_colors'),
                    'odd_cloth': item_info.get('odd_cloth', 0),
                    'even_cloth': item_info.get('even_cloth', 0),
                    'cushion_cloth': item_info.get('cushion_cloth', 0),
                    'minor_cloth': item_info.get('minor_cloth', 0),
                    'is_minor': True if item_info.get('minor_cloth', 0) else False
                })
            
            # همیشه قیمت را چک کن
            price_found = False
            if 'Price' in entry and entry['Price'] and entry['Price'] > 0:
                price_found = True
            if not price_found:
                try:
                    price_row = frappe.db.get_value("Item Price", {"item_code": entry['item_code'], "price_list": price_list_param}, ["price_list_rate"])
                    if price_row:
                        price_val = price_row[0] if isinstance(price_row, (list, tuple)) else price_row
                        entry['price_list_rate'] = price_val
                        entry['Price'] = int(price_val / 10) if price_val and price_val > 0 else 0
                        if entry['Price'] > 0:
                            price_str = str(entry['Price'])
                            formatted_price = ",".join([price_str[::-1][i:i + 3] for i in range(0, len(price_str), 3)])[::-1]
                            persian_digits = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
                            for english, persian in persian_digits.items():
                                formatted_price = formatted_price.replace(english, persian)
                            entry['formatted_Price'] = formatted_price
                        else:
                            entry['formatted_Price'] = "تماس بگیرید"
                    else:
                        entry['formatted_Price'] = "تماس بگیرید"
                except Exception:
                    entry['formatted_Price'] = "تماس بگیرید"
            
            # اگر داده‌های پایه نبود، واکشی کن
            if (not entry.get('item_name')) or (not entry.get('description')) or (not entry.get('image')) or (not entry.get('odd_cloth') and not entry.get('even_cloth') and not entry.get('cushion_cloth') and not entry.get('minor_cloth')):
                try:
                    item_row = frappe.db.get_value("Item", {"name": entry['item_code']}, ["item_name", "description", "image", "odd_cloth", "even_cloth", "cushion_cloth", "minor_cloth"])
                    if item_row:
                        if not entry.get('item_name'):
                            entry['item_name'] = item_row[0] if isinstance(item_row, (list, tuple)) else item_row
                        if isinstance(item_row, (list, tuple)):
                            if len(item_row) > 1 and not entry.get('description'):
                                entry['description'] = item_row[1]
                            if len(item_row) > 2 and not entry.get('image'):
                                entry['image'] = item_row[2]
                            if len(item_row) > 3 and not entry.get('odd_cloth'):
                                entry['odd_cloth'] = item_row[3] or 0
                            if len(item_row) > 4 and not entry.get('even_cloth'):
                                entry['even_cloth'] = item_row[4] or 0
                            if len(item_row) > 5 and not entry.get('cushion_cloth'):
                                entry['cushion_cloth'] = item_row[5] or 0
                            if len(item_row) > 6 and not entry.get('minor_cloth'):
                                entry['minor_cloth'] = item_row[6] or 0
                                entry['is_minor'] = True if (item_row[6] or 0) else False
                except Exception:
                    pass
        
        # ساخت دیکشنری با ترتیب صحیح
        final_bundle_items = []
        for entry in bundle_table_items:
            ordered_entry = {
                'item_name': entry.get('item_name'),
                'item_code': entry.get('item_code'),
                'display_name': entry.get('display_name') or entry.get('item_name'),
                'display_name_without_wood_color': clean_bundle_name(entry.get('item_name', '')),
                'description': entry.get('description', ''),
                'description_without_wood_color': clean_bundle_name(entry.get('description', '')),
                'image': entry.get('image'),
                'creation': entry.get('creation'),
                'projected_qty': entry.get('projected_qty', 0),
                'price_list_rate': entry.get('price_list_rate'),
                'model': entry.get('model'),
                'module': entry.get('module'),
                'module_feature': entry.get('module_feature'),
                'module_length': entry.get('length'),
                'module_width': entry.get('width'),
                'module_height': entry.get('height'),
                'module_diameter': entry.get('diameter'),
                'module_shape': entry.get('shape'),
                'module_color': entry.get('color'),
                'wood_color': entry.get('wood_color'),
                'body_color': entry.get('body_color'),
                'odd_cloth': entry.get('odd_cloth', 0),
                'even_cloth': entry.get('even_cloth', 0),
                'minor_cloth': entry.get('minor_cloth', 0),
                'cushion_cloth': entry.get('cushion_cloth', 0),
                'Price': entry.get('Price'),
                'formatted_Price': entry.get('formatted_Price'),
                'images': entry.get('images', []),
                'stock_qty': entry.get('stock_qty', 0),
                'yindex': entry.get('yindex'),
                'variant_of': entry.get('variant_of'),
                'all_wood_colors': entry.get('all_wood_colors', []),
                'is_minor': entry.get('is_minor', False),
                'qty': entry.get('qty'),
                'uom': entry.get('uom')
            }
            final_bundle_items.append(ordered_entry)
        
        merged_bundle['sofa_bundle_table_items'] = final_bundle_items
        
        # استفاده از داده‌های پارچه از خود bundle
        bundle_odd = merged_bundle.get('odd_fabric', 0) or 0
        bundle_even = merged_bundle.get('even_fabric', 0) or 0
        bundle_cushion = merged_bundle.get('cushion_fabric', 0) or 0
        bundle_minor = merged_bundle.get('minor_fabric', 0) or 0
        
        if bundle_odd == 0 and bundle_even == 0 and bundle_cushion == 0 and bundle_minor == 0:
            total_odd = 0
            total_even = 0
            total_cushion = 0
            total_minor = 0
            for item in bundle_table_items:
                total_odd = total_odd + ((item.get('odd_cloth', 0) or 0) * (item.get('qty', 1) or 1))
                total_even = total_even + ((item.get('even_cloth', 0) or 0) * (item.get('qty', 1) or 1))
                total_cushion = total_cushion + ((item.get('cushion_cloth', 0) or 0) * (item.get('qty', 1) or 1))
                total_minor = total_minor + ((item.get('minor_cloth', 0) or 0) * (item.get('qty', 1) or 1))
            merged_bundle['odd_fabric'] = total_odd
            merged_bundle['even_fabric'] = total_even
            merged_bundle['cushion_fabric'] = total_cushion
            merged_bundle['minor_fabric'] = total_minor
        
        merged_bundle['is_minor'] = True if merged_bundle.get('minor_fabric', 0) else False
        merged_bundle['total_fabric'] = merged_bundle.get('odd_fabric', 0) + merged_bundle.get('cushion_fabric', 0) + merged_bundle.get('minor_fabric', 0)
        merged_bundle.pop('bundle_items', None)
        
        merged_bundles.append(merged_bundle)
    
    model['sofa_bundles'] = merged_bundles

# حذف آیتم‌های تکراری
for model in nested_sofa_products:
    for bundle in model.get('sofa_bundles', []):
        unique = {}
        for item in bundle['sofa_bundle_table_items']:
            key = item.get('item_code') or item.get('item_name')
            if key and key not in unique:
                unique[key] = item
        bundle['sofa_bundle_table_items'] = list(unique.values())

# اطمینان از وجود کلیدها
for model in nested_sofa_products:
    if 'sofa_modules' not in model or not isinstance(model['sofa_modules'], list):
        model['sofa_modules'] = []
    if 'sofa_bundles' not in model or not isinstance(model['sofa_bundles'], list):
        model['sofa_bundles'] = []
    for module in model['sofa_modules']:
        if 'sofa_module_items' not in module or not isinstance(module['sofa_module_items'], list):
            module['sofa_module_items'] = []
    for bundle in model['sofa_bundles']:
        if 'sofa_bundle_table_items' not in bundle or not isinstance(bundle['sofa_bundle_table_items'], list):
            bundle['sofa_bundle_table_items'] = []

# مرتب‌سازی نهایی
def yindex_sort_key_final(obj):
    yidx = obj.get('sofa_yindex') or obj.get('yindex')
    try:
        return (0, int(yidx))
    except (TypeError, ValueError):
        return (1, 0)

nested_sofa_products.sort(key=yindex_sort_key_final)

for model in nested_sofa_products:
    if 'sofa_modules' in model and isinstance(model['sofa_modules'], list):
        model['sofa_modules'].sort(key=yindex_sort_key_final)
        for module in model['sofa_modules']:
            if 'sofa_module_items' in module and isinstance(module['sofa_module_items'], list):
                module['sofa_module_items'].sort(key=yindex_sort_key_final)

    if 'sofa_bundles' in model and isinstance(model['sofa_bundles'], list):
        model['sofa_bundles'].sort(key=yindex_sort_key_final)
        for bundle in model['sofa_bundles']:
            if 'sofa_bundle_table_items' in bundle and isinstance(bundle['sofa_bundle_table_items'], list):
                bundle['sofa_bundle_table_items'].sort(key=yindex_sort_key_final)

# اضافه کردن محصولات مرتبط (میز عسلی، میز جلومبلی، کوسن، باکس، نیمکت)
for model in nested_sofa_products:
    model_name = model.get('sofa_model_name', '')
    if not model_name:
        continue
    
    related_products_query = """
        SELECT 
            i.*,
            model_attr.attribute_value as model_value,
            COALESCE(model_abbr.abbr, model_attr.attribute_value) as model,
            module_attr.attribute_value as module_value,
            COALESCE(module_abbr.abbr, module_attr.attribute_value) as module,
            shape_attr.attribute_value as shape_value,
            COALESCE(shape_abbr.abbr, shape_attr.attribute_value) as shape,
            color_attr.attribute_value as color_value,
            COALESCE(color_abbr.abbr, color_attr.attribute_value) as color,
            wood_color_attr.attribute_value as wood_color_value,
            COALESCE(wood_color_abbr.abbr, wood_color_attr.attribute_value) as wood_color,
            length_attr.attribute_value as length_value,
            width_attr.attribute_value as width_value,
            height_attr.attribute_value as height_value,
            diameter_attr.attribute_value as diameter_value,
            i.odd_cloth as fabric_odd,
            i.even_cloth as fabric_even,
            i.minor_cloth as fabric_minor,
            i.cushion_cloth as fabric_cushion,
            COALESCE(ip.price_list_rate, 0) as price_list_rate
        FROM `tabItem` i
        LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code AND ip.price_list = %s
        LEFT JOIN `tabItem Variant Attribute` model_attr 
            ON i.name = model_attr.parent AND model_attr.attribute = 'مدل محصول'
        LEFT JOIN `tabItem Attribute Value` model_abbr
            ON model_attr.attribute = model_abbr.parent AND model_attr.attribute_value = model_abbr.attribute_value
        LEFT JOIN `tabItem Variant Attribute` module_attr 
            ON i.name = module_attr.parent AND module_attr.attribute = 'ماژول'
        LEFT JOIN `tabItem Attribute Value` module_abbr
            ON module_attr.attribute = module_abbr.parent AND module_attr.attribute_value = module_abbr.attribute_value
        LEFT JOIN `tabItem Variant Attribute` shape_attr 
            ON i.name = shape_attr.parent AND shape_attr.attribute = 'شکل'
        LEFT JOIN `tabItem Attribute Value` shape_abbr
            ON shape_attr.attribute = shape_abbr.parent AND shape_attr.attribute_value = shape_abbr.attribute_value
        LEFT JOIN `tabItem Variant Attribute` color_attr 
            ON i.name = color_attr.parent AND color_attr.attribute = 'رنگ بدنه'
        LEFT JOIN `tabItem Attribute Value` color_abbr
            ON color_attr.attribute = color_abbr.parent AND color_attr.attribute_value = color_abbr.attribute_value
        LEFT JOIN `tabItem Variant Attribute` wood_color_attr 
            ON i.name = wood_color_attr.parent AND wood_color_attr.attribute = 'رنگ چوب'
        LEFT JOIN `tabItem Attribute Value` wood_color_abbr
            ON wood_color_attr.attribute = wood_color_abbr.parent AND wood_color_attr.attribute_value = wood_color_abbr.attribute_value
        LEFT JOIN `tabItem Variant Attribute` length_attr 
            ON i.name = length_attr.parent AND length_attr.attribute = 'طول'
        LEFT JOIN `tabItem Variant Attribute` width_attr 
            ON i.name = width_attr.parent AND width_attr.attribute = 'عرض'
        LEFT JOIN `tabItem Variant Attribute` height_attr 
            ON i.name = height_attr.parent AND height_attr.attribute = 'ارتفاع'
        LEFT JOIN `tabItem Variant Attribute` diameter_attr 
            ON i.name = diameter_attr.parent AND diameter_attr.attribute = 'قطر'
        WHERE i.variant_of IN ('میز جلومبلی', 'میز عسلی', 'کوسن', 'باکس', 'نیمکت')
            AND i.item_group = 'محصولات'
            AND i.show_on_site = 1
            AND EXISTS (
                SELECT 1 FROM `tabItem Variant Attribute` iva 
                WHERE iva.parent = i.name 
                AND iva.attribute = 'مدل محصول' 
                AND iva.attribute_value = %s
            )
        ORDER BY i.variant_of, COALESCE(model_abbr.abbr, model_attr.attribute_value)
    """
    
    related_items = frappe.db.sql(related_products_query, (price_list_param, model_name), as_dict=True)
    
    related_by_type = {}
    
    for item in related_items:
        item_price = item.get('price_list_rate', 0)
        if item_price > 0:
            item_price = int(item_price / 10)
            price_str = str(item_price)
            formatted_price = ",".join([price_str[::-1][i:i + 3] for i in range(0, len(price_str), 3)])[::-1]
            formatted_price = to_persian_digits(formatted_price)
        else:
            formatted_price = "تماس بگیرید"
        
        item_images = []
        if item.item_name:
            name_variants = {item.item_name}
            name = item.item_name
            indices = [i for i, c in enumerate(name) if c in [' ', '-']]
            n = len(indices)
            for bits in range(2 ** n):
                chars = list(name)
                for j in range(n):
                    if (bits >> j) & 1:
                        chars[indices[j]] = '-' if chars[indices[j]] == ' ' else ' '
                name_variants.add(''.join(chars))
            
            if name_variants:
                placeholders = ','.join(['%s'] * len(name_variants))
                images_query = f"""
                    SELECT 
                        name, file_name, file_url, file_size, file_type,
                        attached_to_name, custom_yindex, custom_alt_text, custom_tag
                    FROM `tabFile`
                    WHERE attached_to_doctype = 'Item'
                        AND attached_to_name IN ({placeholders})
                        AND is_private = 0
                        AND (file_type LIKE 'image%%' OR file_url LIKE '%%.jpg' OR file_url LIKE '%%.jpeg' 
                            OR file_url LIKE '%%.png' OR file_url LIKE '%%.gif' OR file_url LIKE '%%.webp' 
                            OR file_url LIKE '%%.svg')
                    ORDER BY CAST(COALESCE(custom_yindex, 0) AS SIGNED) ASC
                """
                files = frappe.db.sql(images_query, tuple(name_variants), as_dict=True)
                seen_urls = set()
                for img in files:
                    if img.file_url and img.file_url not in seen_urls:
                        item_images.append({
                            "name": img.name,
                            "file_name": img.file_name,
                            "file_url": img.file_url,
                            "file_size": img.file_size,
                            "file_type": img.file_type,
                            "attached_to_name": img.attached_to_name,
                            "custom_yindex": img.custom_yindex,
                            "custom_alt_text": img.custom_alt_text,
                            "custom_tag": img.custom_tag,
                            "cover": True if img.custom_tag == "کاور" else False,
                            "dimentions": True if img.custom_tag == "اندازه" else False,
                            "gallary": True if img.custom_tag == "گالری" else False,
                            "icon": True if img.custom_tag == "آیکون" else False
                        })
                        seen_urls.add(img.file_url)
        
        item_obj = {
            "item_name": item.item_name,
            "item_code": item.item_code,
            "display_name": item.item_name,
            "display_name_without_wood_color": clean_bundle_name(item.item_name),
            "description": item.get('description', ''),
            "description_without_wood_color": clean_bundle_name(item.get('description', '')),
            "image": item.get('image', ''),
            "creation": item.get('creation'),
            "projected_qty": item.get('total_projected_qty', 0),
            "price_list_rate": item_price * 10 if item_price > 0 else 0,
            "model": item.get('model'),
            "module": item.get('module'),
            "module_feature": item.get('module_feature'),
            "module_length": item.get('length_value'),
            "module_width": item.get('width_value'),
            "module_height": item.get('height_value'),
            "module_diameter": item.get('diameter_value'),
            "module_shape": item.get('shape'),
            "module_color": item.get('color'),
            "wood_color": item.get('wood_color'),
            "body_color": item.get('body_color'),
            "odd_cloth": item.get('fabric_odd', 0),
            "even_cloth": item.get('fabric_even', 0),
            "minor_cloth": item.get('fabric_minor', 0),
            "cushion_cloth": item.get('fabric_cushion', 0),
            "Price": item_price if item_price > 0 else 0,
            "formatted_Price": formatted_price,
            "images": item_images,
            "stock_qty": item.get('total_projected_qty', 0),
            "yindex": item.get('yindex'),
            "variant_of": item.variant_of,
            "all_wood_colors": [],
            "is_minor": True if item.get('fabric_minor', 0) else False
        }
        
        variant_type = item.variant_of
        module_or_shape = item.get('shape') or item.get('module') or ''
        body_color = item.get('color') or ''
        
        # کلید گروه‌بندی شامل: نوع، ماژول/شکل، رنگ بدنه، ابعاد (بدون رنگ چوب)
        # رنگ‌های چوب مختلف در یک module قرار می‌گیرند
        dimensions = (
            item.get('length_value') or '',
            item.get('width_value') or '',
            item.get('height_value') or '',
            item.get('diameter_value') or ''
        )
        
        shape_value = item.get('shape') or ''
        
        # کلید بدون رنگ چوب - فقط شامل: نوع، ماژول، رنگ بدنه، ابعاد، شکل
        key = (variant_type, module_or_shape, body_color, dimensions, shape_value)
        if key not in related_by_type:
            related_by_type[key] = []
        related_by_type[key].append(item_obj)
    
    merged_items_by_type = {}
    for key in related_by_type:
        items_group = related_by_type[key]
        variant_type = key[0]
        module_or_shape_name = key[1]
        body_color = key[2]  # این رنگ بدنه است، نه رنگ چوب
        dimensions = key[3]
        shape_value = key[4]
        
        # پیدا کردن آیتم با بالاترین قیمت
        max_price_item = max(items_group, key=lambda x: x.get('Price') or 0)
        
        # جمع‌آوری تمام رنگ‌های چوب
        wood_colors = []
        all_images = []
        seen_image_urls = set()
        
        for item in items_group:
            wood_color = item.get('wood_color')
            if wood_color and wood_color not in wood_colors:
                wood_colors.append(wood_color)
            
            for img in item.get('images', []):
                if img['file_url'] not in seen_image_urls:
                    all_images.append(img)
                    seen_image_urls.add(img['file_url'])
        
        merged_item = max_price_item.copy()
        merged_item['all_wood_colors'] = wood_colors
        merged_item['images'] = all_images
        
        # کلید نهایی: نوع، ماژول/شکل، شکل (برای جدا کردن شکل‌های مختلف)
        final_key = (variant_type, module_or_shape_name or variant_type, shape_value)
        if final_key not in merged_items_by_type:
            merged_items_by_type[final_key] = []
        merged_items_by_type[final_key].append(merged_item)
    
    if 'sofa_modules' not in model:
        model['sofa_modules'] = []
    
    for final_key in merged_items_by_type:
        items = merged_items_by_type[final_key]
        variant_type = final_key[0]
        module_or_shape_name = final_key[1]
        shape_val = final_key[2] if len(final_key) > 2 else None
        
        items.sort(key=yindex_sort_key_final)
        
        first_item_model = items[0].get('model') if items else None
        first_item_variant = items[0].get('variant_of') if items else variant_type
        
        final_module_name = module_or_shape_name if module_or_shape_name != variant_type else ''
        
        length_val = None
        width_val = None
        height_val = None
        diameter_val = None
        
        odd_cloth_vals = [i.get('odd_cloth', 0) for i in items if i.get('odd_cloth') is not None]
        even_cloth_vals = [i.get('even_cloth', 0) for i in items if i.get('even_cloth') is not None]
        minor_cloth_vals = [i.get('minor_cloth', 0) for i in items if i.get('minor_cloth') is not None]
        cushion_cloth_vals = [i.get('cushion_cloth', 0) for i in items if i.get('cushion_cloth') is not None]
        odd_cloth = max(odd_cloth_vals) if odd_cloth_vals else 0
        even_cloth = max(even_cloth_vals) if even_cloth_vals else 0
        minor_cloth = max(minor_cloth_vals) if minor_cloth_vals else 0
        cushion_cloth = max(cushion_cloth_vals) if cushion_cloth_vals else 0
        
        new_module = {
            'sofa_module_name': final_module_name,
            'sofa_module_type': variant_type,
            'sofa_model': first_item_model or "",
            'sofa_product_type': first_item_variant,
            'sofa_length': "",
            'sofa_width': "",
            'sofa_height': "",
            'sofa_diameter': "",
            'sofa_shape': shape_val or "",
            'sofa_odd_cloth': odd_cloth,
            'sofa_even_cloth': even_cloth,
            'sofa_minor_cloth': minor_cloth,
            'sofa_cushion_cloth': cushion_cloth,
            'is_minor': True if minor_cloth else False,
            'total_cloth_for_sofa': round(odd_cloth + minor_cloth, 2),
            'sofa_module_images': [],
            'sofa_module_items': items,
            'sofa_yindex': items[0].get('yindex') if items else "",
            'sofa_yindex_source': 'related_product'
        }
        
        seen_urls = set()
        for item in items:
            for img in item.get('images', []):
                if img['file_url'] not in seen_urls:
                    new_module['sofa_module_images'].append(img)
                    seen_urls.add(img['file_url'])
        
        model['sofa_modules'].append(new_module)
    
    model['sofa_modules'].sort(key=yindex_sort_key_final)

# خروجی نهایی
data['NestedSofaProducts'] = nested_sofa_products

# ==========================================================
# بخش ۲: بارگذاری ClothGroups (پارچه‌ها)
# ==========================================================

def is_persian(text):
    for ch in text:
        if '\u0600' <= ch <= '\u06FF':
            continue
        if ch in ' 0123456789':
            continue
        return False
    return True

# گرفتن همه آیتم‌های پارچه
all_cloth_items = frappe.db.sql("""
    SELECT i.*, iva.attribute_value as cloth_group
    FROM `tabItem` i
    INNER JOIN `tabItem Variant Attribute` iva ON i.name = iva.parent
    WHERE i.variant_of = 'پارچه' AND i.item_group = 'پارچه'
    AND iva.attribute = 'کالیته پارچه'
""", as_dict=True)

# فیلتر گروه‌های فارسی
cloth_groups_set = set()
for item in all_cloth_items:
    if item.cloth_group and is_persian(item.cloth_group):
        cloth_groups_set.add(item.cloth_group)
cloth_groups = sorted(list(cloth_groups_set))

# گروه‌بندی آیتم‌ها
items_by_group = {}
all_cloth_lookup_keys = set()
for item in all_cloth_items:
    group = item.cloth_group
    if group and is_persian(group):
        if group not in items_by_group:
            items_by_group[group] = []
        items_by_group[group].append(item)
        if item.name: all_cloth_lookup_keys.add(item.name)
        if item.item_code: all_cloth_lookup_keys.add(item.item_code)

# گرفتن قیمت‌ها
cloth_prices_lookup = {}
cloth_buying_prices = {}
if all_cloth_lookup_keys:
    lookup_keys_list = list(all_cloth_lookup_keys)
    placeholders = ','.join(['%s'] * len(lookup_keys_list))
    
    selling_prices = frappe.db.sql(f"""
        SELECT item_code, price_list, price_list_rate
        FROM `tabItem Price`
        WHERE item_code IN ({placeholders}) AND selling = 1
    """, tuple(lookup_keys_list), as_dict=True)
    
    for p in selling_prices:
        if p.item_code not in cloth_prices_lookup:
            cloth_prices_lookup[p.item_code] = {}
        cloth_prices_lookup[p.item_code][p.price_list] = p.price_list_rate
    
    buying_prices = frappe.db.sql(f"""
        SELECT item_code, price_list_rate, creation
        FROM `tabItem Price`
        WHERE item_code IN ({placeholders}) AND buying = 1
        ORDER BY creation DESC
    """, tuple(lookup_keys_list), as_dict=True)
    
    for p in buying_prices:
        if p.item_code not in cloth_buying_prices:
            cloth_buying_prices[p.item_code] = p.price_list_rate

# گرفتن تصاویر
sample_images = {}
sample_natures = {}
if cloth_groups:
    placeholders = ','.join(['%s'] * len(cloth_groups))
    
    cover_query = frappe.db.sql(f"""
        SELECT iva.attribute_value as cloth_group, i.image, i.creation
        FROM `tabItem` i
        INNER JOIN `tabItem Variant Attribute` iva ON i.name = iva.parent
        WHERE iva.attribute_value IN ({placeholders})
        AND i.variant_of = 'پارچه' AND i.item_group = 'پارچه'
        AND i.cloth_cover = '1' AND i.image IS NOT NULL
        ORDER BY i.creation ASC
    """, tuple(cloth_groups), as_dict=True)
    
    for row in cover_query:
        if row.cloth_group not in sample_images:
            sample_images[row.cloth_group] = row.image
    
    nature_query = frappe.db.sql(f"""
        SELECT iva.attribute_value as cloth_group, i.cloth_nature, i.creation
        FROM `tabItem` i
        INNER JOIN `tabItem Variant Attribute` iva ON i.name = iva.parent
        WHERE iva.attribute_value IN ({placeholders})
        AND i.variant_of = 'پارچه' AND i.item_group = 'پارچه'
        AND i.cloth_cover = '1' AND i.cloth_nature IS NOT NULL
        ORDER BY i.creation ASC
    """, tuple(cloth_groups), as_dict=True)
    
    for row in nature_query:
        if row.cloth_group not in sample_natures:
            sample_natures[row.cloth_group] = row.cloth_nature

# ساخت نتیجه نهایی
final_groups = []

for group in cloth_groups:
    items = items_by_group.get(group, [])
    if not items:
        continue
    
    # پیدا کردن بالاترین قیمت
    group_max_price = 0
    for item in items:
        item_prices = cloth_prices_lookup.get(item.item_code)
        if not item_prices:
            item_prices = cloth_prices_lookup.get(item.name, {})
        
        p1 = item_prices.get("Standard Selling")
        p2 = item_prices.get(price_list_param)
        
        p_max = max(p for p in [p1, p2, 0] if p is not None)
        if p_max > group_max_price:
            group_max_price = p_max
    
    group_max_price_toman = int(group_max_price / 10) if group_max_price else 0
    group_max_price_formatted = ",".join([str(group_max_price_toman)[::-1][i:i + 3] for i in range(0, len(str(group_max_price_toman)), 3)])[::-1] if group_max_price_toman else "۰"
    group_max_price_formatted = to_persian_digits(group_max_price_formatted)
    
    # اضافه کردن قیمت به هر آیتم
    for item in items:
        item_prices = cloth_prices_lookup.get(item.item_code)
        if not item_prices:
            item_prices = cloth_prices_lookup.get(item.name, {})
            
        price = item_prices.get("Standard Selling")
        
        if price is None:
            price = item_prices.get(price_list_param)
            
        if price is None:
            price = 0
            
        toman_price = int(price / 10)
        item["Price"] = toman_price
        
        if toman_price > 0:
            price_str = str(toman_price)
            formatted = ",".join([price_str[::-1][i:i + 3] for i in range(0, len(price_str), 3)])[::-1]
            item["formatted_Price"] = to_persian_digits(formatted)
        else:
            item["formatted_Price"] = "۰"
        
        # پاکسازی None
        for key, value in item.items():
            if value is None:
                item[key] = ""
    
    final_groups.append({
        "name": group or "",
        "average_purchase_price": group_max_price_formatted or "۰",
        "sample_image": sample_images.get(group) or "",
        "cloth_nature": sample_natures.get(group) or "",
        "clothvariants": items or []
    })

data.ClothGroups = final_groups

# Cleanup: تبدیل هر None باقیمانده به رشته خالی

final_json = json.dumps({"NestedSofaProducts": data.NestedSofaProducts, "ClothGroups": data.ClothGroups}, default=str)
final_data = json.loads(final_json.replace(': null', ': ""'))
data.NestedSofaProducts = final_data.get("NestedSofaProducts", [])
data.ClothGroups = final_data.get("ClothGroups", [])

# ==========================================================
# پایان - فقط دو گروه اصلی
# ==========================================================


{
  "NestedSofaProducts": [
    {
      "sofa_model_name": "دیبا",
      "sofa_route": "sofas/دیبا",
      "sofa_model_description": "",
      "sofa_main_photo": "/private/files/Gemini_Generated_Image_xi22b1xi22b1xi22.webp",
      "sofa_icon_photo": "",
      "sofa_images": [
        {
          "name": "b36254bd75",
          "file_name": "Gemini_Generated_Image_8g8d0k8g8d0k8g8d.webp",
          "file_url": "/files/Gemini_Generated_Image_8g8d0k8g8d0k8g8d.webp",
          "file_size": 246018,
          "file_type": "WEBP",
          "attached_to_name": "مبل دیبا اکسنت خودرنگ",
          "custom_yindex": "",
          "custom_alt_text": "",
          "custom_tag": "کاور",
          "cover": true,
          "dimentions": false,
          "gallary": false,
          "icon": false
        },
        {
          "name": "53c428d60c",
          "file_name": "Gemini_Generated_Image_kcc9lekcc9lekcc9.webp",
          "file_url": "/files/Gemini_Generated_Image_kcc9lekcc9lekcc9.webp",
          "file_size": 203156,
          "file_type": "WEBP",
          "attached_to_name": "مبل دیبا تک نفره بی دسته خودرنگ",
          "custom_yindex": "",
          "custom_alt_text": "",
          "custom_tag": "کاور",
          "cover": true,
          "dimentions": false,
          "gallary": false,
          "icon": false
        },
        {
          "name": "bc7b821bcd",
          "file_name": "Gemini_Generated_Image_i4243i4243i4243i.webp",
          "file_url": "/files/Gemini_Generated_Image_i4243i4243i4243i.webp",
          "file_size": 228560,
          "file_type": "WEBP",
          "attached_to_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
          "custom_yindex": "",
          "custom_alt_text": "",
          "custom_tag": "کاور",
          "cover": true,
          "dimentions": false,
          "gallary": false,
          "icon": false
        },
        {
          "name": "ab2252b625",
          "file_name": "Diba-Goshe.webp",
          "file_url": "/files/Diba-Goshe.webp",
          "file_size": 322923,
          "file_type": "WEBP",
          "attached_to_name": "مبل دیبا گوشه خودرنگ",
          "custom_yindex": "",
          "custom_alt_text": "",
          "custom_tag": "کاور",
          "cover": true,
          "dimentions": false,
          "gallary": false,
          "icon": false
        }
      ],
      "sofa_modules": [
        {
          "sofa_module_name": "اکسنت",
          "sofa_module_type": "مبل",
          "sofa_model": "دیبا",
          "sofa_product_type": "مبل",
          "sofa_length": "",
          "sofa_width": "",
          "sofa_height": "",
          "sofa_diameter": "",
          "sofa_shape": "",
          "sofa_odd_cloth": 1.8,
          "sofa_even_cloth": 3.6,
          "sofa_minor_cloth": 0,
          "sofa_cushion_cloth": 0,
          "is_minor": false,
          "total_cloth_for_sofa": 1.8,
          "sofa_module_images": [
            {
              "name": "b36254bd75",
              "file_name": "Gemini_Generated_Image_8g8d0k8g8d0k8g8d.webp",
              "file_url": "/files/Gemini_Generated_Image_8g8d0k8g8d0k8g8d.webp",
              "file_size": 246018,
              "file_type": "WEBP",
              "attached_to_name": "مبل دیبا اکسنت خودرنگ",
              "custom_yindex": "",
              "custom_alt_text": "",
              "custom_tag": "کاور",
              "cover": true,
              "dimentions": false,
              "gallary": false,
              "icon": false
            }
          ],
          "sofa_module_items": [
            {
              "item_name": "مبل دیبا اکسنت خودرنگ",
              "item_code": "مبل دیبا اکسنت خودرنگ",
              "display_name": "مبل دیبا اکسنت خودرنگ",
              "display_name_without_wood_color": "مبل دیبا اکسنت",
              "description": "مبل-دیبا-اکسنت-خودرنگ",
              "description_without_wood_color": "مبل-دیبا-اکسنت-",
              "image": "/files/Gemini_Generated_Image_8g8d0k8g8d0k8g8d.webp",
              "creation": "2025-08-23 13:02:35.410201",
              "projected_qty": 0,
              "price_list_rate": 121500000,
              "model": "دیبا",
              "module": "اکسنت",
              "module_feature": "",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 1.8,
              "even_cloth": 3.6,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 12150000,
              "formatted_Price": "۱۲,۱۵۰,۰۰۰",
              "images": [
                {
                  "name": "b36254bd75",
                  "file_name": "Gemini_Generated_Image_8g8d0k8g8d0k8g8d.webp",
                  "file_url": "/files/Gemini_Generated_Image_8g8d0k8g8d0k8g8d.webp",
                  "file_size": 246018,
                  "file_type": "WEBP",
                  "attached_to_name": "مبل دیبا اکسنت خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "مبل",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false
            }
          ],
          "sofa_yindex": "",
          "sofa_yindex_source": ""
        },
        {
          "sofa_module_name": "تک نفره",
          "sofa_module_type": "مبل",
          "sofa_model": "دیبا",
          "sofa_product_type": "مبل",
          "sofa_length": "",
          "sofa_width": "",
          "sofa_height": "",
          "sofa_diameter": "",
          "sofa_shape": "",
          "sofa_odd_cloth": 2.5,
          "sofa_even_cloth": 0,
          "sofa_minor_cloth": 0,
          "sofa_cushion_cloth": 0,
          "is_minor": false,
          "total_cloth_for_sofa": 2.5,
          "sofa_module_images": [
            {
              "name": "53c428d60c",
              "file_name": "Gemini_Generated_Image_kcc9lekcc9lekcc9.webp",
              "file_url": "/files/Gemini_Generated_Image_kcc9lekcc9lekcc9.webp",
              "file_size": 203156,
              "file_type": "WEBP",
              "attached_to_name": "مبل دیبا تک نفره بی دسته خودرنگ",
              "custom_yindex": "",
              "custom_alt_text": "",
              "custom_tag": "کاور",
              "cover": true,
              "dimentions": false,
              "gallary": false,
              "icon": false
            }
          ],
          "sofa_module_items": [
            {
              "item_name": "مبل دیبا تک نفره بی دسته خودرنگ",
              "item_code": "مبل دیبا تک نفره بی دسته خودرنگ",
              "display_name": "مبل دیبا تک نفره بی دسته خودرنگ",
              "display_name_without_wood_color": "مبل دیبا تک نفره بی دسته",
              "description": "مبل-دیبا-تک نفره-بی دسته-خودرنگ",
              "description_without_wood_color": "مبل-دیبا-تک نفره-بی دسته-",
              "image": "/files/Gemini_Generated_Image_kcc9lekcc9lekcc9.webp",
              "creation": "2025-08-23 13:02:15.090759",
              "projected_qty": 0,
              "price_list_rate": 142000000,
              "model": "دیبا",
              "module": "تک نفره",
              "module_feature": "بی دسته",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 2.5,
              "even_cloth": 0,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 14200000,
              "formatted_Price": "۱۴,۲۰۰,۰۰۰",
              "images": [
                {
                  "name": "53c428d60c",
                  "file_name": "Gemini_Generated_Image_kcc9lekcc9lekcc9.webp",
                  "file_url": "/files/Gemini_Generated_Image_kcc9lekcc9lekcc9.webp",
                  "file_size": 203156,
                  "file_type": "WEBP",
                  "attached_to_name": "مبل دیبا تک نفره بی دسته خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "مبل",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false
            }
          ],
          "sofa_yindex": "",
          "sofa_yindex_source": ""
        },
        {
          "sofa_module_name": "تک نفره تک دسته",
          "sofa_module_type": "مبل",
          "sofa_model": "دیبا",
          "sofa_product_type": "مبل",
          "sofa_length": "",
          "sofa_width": "",
          "sofa_height": "",
          "sofa_diameter": "",
          "sofa_shape": "",
          "sofa_odd_cloth": 3,
          "sofa_even_cloth": 6,
          "sofa_minor_cloth": 0,
          "sofa_cushion_cloth": 0,
          "is_minor": false,
          "total_cloth_for_sofa": 3,
          "sofa_module_images": [
            {
              "name": "bc7b821bcd",
              "file_name": "Gemini_Generated_Image_i4243i4243i4243i.webp",
              "file_url": "/files/Gemini_Generated_Image_i4243i4243i4243i.webp",
              "file_size": 228560,
              "file_type": "WEBP",
              "attached_to_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
              "custom_yindex": "",
              "custom_alt_text": "",
              "custom_tag": "کاور",
              "cover": true,
              "dimentions": false,
              "gallary": false,
              "icon": false
            }
          ],
          "sofa_module_items": [
            {
              "item_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
              "item_code": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
              "display_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
              "display_name_without_wood_color": "مبل دیبا تک نفره تک دسته دسته سمت چپ",
              "description": "مبل-دیبا-تک نفره تک دسته-دسته سمت چپ-خودرنگ",
              "description_without_wood_color": "مبل-دیبا-تک نفره تک دسته-دسته سمت چپ-",
              "image": "/files/Gemini_Generated_Image_i4243i4243i4243i.webp",
              "creation": "2025-08-23 13:01:55.174019",
              "projected_qty": 0,
              "price_list_rate": 178000000,
              "model": "دیبا",
              "module": "تک نفره تک دسته",
              "module_feature": "دسته سمت چپ",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 3,
              "even_cloth": 6,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 17800000,
              "formatted_Price": "۱۷,۸۰۰,۰۰۰",
              "images": [
                {
                  "name": "bc7b821bcd",
                  "file_name": "Gemini_Generated_Image_i4243i4243i4243i.webp",
                  "file_url": "/files/Gemini_Generated_Image_i4243i4243i4243i.webp",
                  "file_size": 228560,
                  "file_type": "WEBP",
                  "attached_to_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "مبل",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false
            }
          ],
          "sofa_yindex": "",
          "sofa_yindex_source": ""
        },
        {
          "sofa_module_name": "گوشه",
          "sofa_module_type": "مبل",
          "sofa_model": "دیبا",
          "sofa_product_type": "مبل",
          "sofa_length": "",
          "sofa_width": "",
          "sofa_height": "",
          "sofa_diameter": "",
          "sofa_shape": "",
          "sofa_odd_cloth": 3.6,
          "sofa_even_cloth": 7.2,
          "sofa_minor_cloth": 0,
          "sofa_cushion_cloth": 0,
          "is_minor": false,
          "total_cloth_for_sofa": 3.6,
          "sofa_module_images": [
            {
              "name": "ab2252b625",
              "file_name": "Diba-Goshe.webp",
              "file_url": "/files/Diba-Goshe.webp",
              "file_size": 322923,
              "file_type": "WEBP",
              "attached_to_name": "مبل دیبا گوشه خودرنگ",
              "custom_yindex": "",
              "custom_alt_text": "",
              "custom_tag": "کاور",
              "cover": true,
              "dimentions": false,
              "gallary": false,
              "icon": false
            }
          ],
          "sofa_module_items": [
            {
              "item_name": "مبل دیبا گوشه خودرنگ",
              "item_code": "مبل دیبا گوشه خودرنگ",
              "display_name": "مبل دیبا گوشه خودرنگ",
              "display_name_without_wood_color": "مبل دیبا گوشه",
              "description": "مبل-دیبا-گوشه-خودرنگ",
              "description_without_wood_color": "مبل-دیبا-گوشه-",
              "image": "/files/Diba-Goshe.webp",
              "creation": "2025-08-23 13:01:22.459829",
              "projected_qty": 0,
              "price_list_rate": 156000000,
              "model": "دیبا",
              "module": "گوشه",
              "module_feature": "",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 3.6,
              "even_cloth": 7.2,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 15600000,
              "formatted_Price": "۱۵,۶۰۰,۰۰۰",
              "images": [
                {
                  "name": "ab2252b625",
                  "file_name": "Diba-Goshe.webp",
                  "file_url": "/files/Diba-Goshe.webp",
                  "file_size": 322923,
                  "file_type": "WEBP",
                  "attached_to_name": "مبل دیبا گوشه خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "مبل",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false
            }
          ],
          "sofa_yindex": "",
          "sofa_yindex_source": ""
        },
        {
          "sofa_module_name": "ذوذنقه",
          "sofa_module_type": "باکس",
          "sofa_model": "دیبا",
          "sofa_product_type": "باکس",
          "sofa_length": "",
          "sofa_width": "",
          "sofa_height": "",
          "sofa_diameter": "",
          "sofa_shape": "ذوذنقه",
          "sofa_odd_cloth": 2,
          "sofa_even_cloth": 4,
          "sofa_minor_cloth": 0,
          "sofa_cushion_cloth": 0,
          "is_minor": false,
          "total_cloth_for_sofa": 2,
          "sofa_module_images": [
            {
              "name": "6bbc89a006",
              "file_name": "Diba-Box.webp",
              "file_url": "/files/Diba-Box.webp",
              "file_size": 102116,
              "file_type": "WEBP",
              "attached_to_name": "باکس دیبا ذوذنقه خودرنگ",
              "custom_yindex": "",
              "custom_alt_text": "",
              "custom_tag": "کاور",
              "cover": true,
              "dimentions": false,
              "gallary": false,
              "icon": false
            }
          ],
          "sofa_module_items": [
            {
              "item_name": "باکس دیبا ذوذنقه خودرنگ",
              "item_code": "باکس دیبا ذوذنقه خودرنگ",
              "display_name": "باکس دیبا ذوذنقه خودرنگ",
              "display_name_without_wood_color": "باکس دیبا ذوذنقه",
              "description": "باکس-دیبا-ذوذنقه-خودرنگ",
              "description_without_wood_color": "باکس-دیبا-ذوذنقه-",
              "image": "/files/Diba-Box.webp",
              "creation": "2025-10-14 11:24:22.353148",
              "projected_qty": 0,
              "price_list_rate": 133000000,
              "model": "دیبا",
              "module": "",
              "module_feature": "",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "ذوذنقه",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 2,
              "even_cloth": 4,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 13300000,
              "formatted_Price": "۱۳,۳۰۰,۰۰۰",
              "images": [
                {
                  "name": "6bbc89a006",
                  "file_name": "Diba-Box.webp",
                  "file_url": "/files/Diba-Box.webp",
                  "file_size": 102116,
                  "file_type": "WEBP",
                  "attached_to_name": "باکس دیبا ذوذنقه خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "باکس",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false
            }
          ],
          "sofa_yindex": "",
          "sofa_yindex_source": "related_product"
        },
        {
          "sofa_module_name": "مربع",
          "sofa_module_type": "باکس",
          "sofa_model": "دیبا",
          "sofa_product_type": "باکس",
          "sofa_length": "",
          "sofa_width": "",
          "sofa_height": "",
          "sofa_diameter": "",
          "sofa_shape": "مربع",
          "sofa_odd_cloth": 2,
          "sofa_even_cloth": 4,
          "sofa_minor_cloth": 0,
          "sofa_cushion_cloth": 0,
          "is_minor": false,
          "total_cloth_for_sofa": 2,
          "sofa_module_images": [
            {
              "name": "a5c7d44b49",
              "file_name": "Gemini_Generated_Image_yu4yn8yu4yn8yu4y.webp",
              "file_url": "/files/Gemini_Generated_Image_yu4yn8yu4yn8yu4y.webp",
              "file_size": 274767,
              "file_type": "WEBP",
              "attached_to_name": "باکس دیبا مربع خودرنگ",
              "custom_yindex": "",
              "custom_alt_text": "",
              "custom_tag": "کاور",
              "cover": true,
              "dimentions": false,
              "gallary": false,
              "icon": false
            }
          ],
          "sofa_module_items": [
            {
              "item_name": "باکس دیبا مربع خودرنگ",
              "item_code": "باکس دیبا مربع خودرنگ",
              "display_name": "باکس دیبا مربع خودرنگ",
              "display_name_without_wood_color": "باکس دیبا مربع",
              "description": "باکس-دیبا-مربع-خودرنگ",
              "description_without_wood_color": "باکس-دیبا-مربع-",
              "image": "/files/Gemini_Generated_Image_yu4yn8yu4yn8yu4y.webp",
              "creation": "2025-10-14 11:24:19.548107",
              "projected_qty": 0,
              "price_list_rate": 197500000,
              "model": "دیبا",
              "module": "",
              "module_feature": "",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "مربع",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 2,
              "even_cloth": 4,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 19750000,
              "formatted_Price": "۱۹,۷۵۰,۰۰۰",
              "images": [
                {
                  "name": "a5c7d44b49",
                  "file_name": "Gemini_Generated_Image_yu4yn8yu4yn8yu4y.webp",
                  "file_url": "/files/Gemini_Generated_Image_yu4yn8yu4yn8yu4y.webp",
                  "file_size": 274767,
                  "file_type": "WEBP",
                  "attached_to_name": "باکس دیبا مربع خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "باکس",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false
            }
          ],
          "sofa_yindex": "",
          "sofa_yindex_source": "related_product"
        },
        {
          "sofa_module_name": "مستطیل",
          "sofa_module_type": "باکس",
          "sofa_model": "دیبا",
          "sofa_product_type": "باکس",
          "sofa_length": "",
          "sofa_width": "",
          "sofa_height": "",
          "sofa_diameter": "",
          "sofa_shape": "مستطیل",
          "sofa_odd_cloth": 2,
          "sofa_even_cloth": 4,
          "sofa_minor_cloth": 0,
          "sofa_cushion_cloth": 0,
          "is_minor": false,
          "total_cloth_for_sofa": 2,
          "sofa_module_images": [
            {
              "name": "8222e89666",
              "file_name": "Rectangle-Dina.webp",
              "file_url": "/files/Rectangle-Dina.webp",
              "file_size": 383198,
              "file_type": "WEBP",
              "attached_to_name": "باکس دیبا مستطیل خودرنگ",
              "custom_yindex": "",
              "custom_alt_text": "",
              "custom_tag": "کاور",
              "cover": true,
              "dimentions": false,
              "gallary": false,
              "icon": false
            }
          ],
          "sofa_module_items": [
            {
              "item_name": "باکس دیبا مستطیل خودرنگ",
              "item_code": "باکس دیبا مستطیل خودرنگ",
              "display_name": "باکس دیبا مستطیل خودرنگ",
              "display_name_without_wood_color": "باکس دیبا مستطیل",
              "description": "باکس-دیبا-مستطیل-خودرنگ",
              "description_without_wood_color": "باکس-دیبا-مستطیل-",
              "image": "/files/Rectangle-Dina.webp",
              "creation": "2025-10-14 11:24:20.953899",
              "projected_qty": 0,
              "price_list_rate": 132500000,
              "model": "دیبا",
              "module": "",
              "module_feature": "",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "مستطیل",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 2,
              "even_cloth": 4,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 13250000,
              "formatted_Price": "۱۳,۲۵۰,۰۰۰",
              "images": [
                {
                  "name": "8222e89666",
                  "file_name": "Rectangle-Dina.webp",
                  "file_url": "/files/Rectangle-Dina.webp",
                  "file_size": 383198,
                  "file_type": "WEBP",
                  "attached_to_name": "باکس دیبا مستطیل خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "باکس",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false
            }
          ],
          "sofa_yindex": "",
          "sofa_yindex_source": "related_product"
        }
      ],
      "sofa_bundles": [
        {
          "name": "مبلمان دیبا چهار نفره همراه کوسن",
          "new_item_code": "مبلمان دیبا چهار نفره همراه کوسن",
          "description": "",
          "disabled": 0,
          "show_on_site": 1,
          "cover_photo": "/private/files/Dina 4 Person.webp",
          "yindex": "",
          "odd_fabric": 8.5,
          "even_fabric": 17,
          "cushion_fabric": 1.5,
          "minor_fabric": 0,
          "bundle_price": 49800000,
          "bundle_formatted_price": "۴۹,۸۰۰,۰۰۰",
          "is_available": true,
          "show_on_website": 1,
          "has_cover_photo": true,
          "bundle_name": "مبلمان دیبا چهار نفره همراه کوسن خودرنگ",
          "bundle_code": "مبلمان دیبا چهار نفره همراه کوسن خودرنگ",
          "bundle_description": "",
          "bundle_cover_photo": "/private/files/Dina 4 Person.webp",
          "total_fabric": 10,
          "is_minor": false,
          "sofa_available_wood_colors": [
            "خودرنگ"
          ],
          "sofa_bundle_name": "مبلمان دیبا چهار نفره همراه کوسن",
          "sofa_bundle_display_name": "مبلمان دیبا چهار نفره همراه کوسن",
          "sofa_bundle_code": "مبلمان دیبا چهار نفره همراه کوسن",
          "sofa_bundle_table_items": [
            {
              "item_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
              "item_code": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
              "display_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
              "display_name_without_wood_color": "مبل دیبا تک نفره تک دسته دسته سمت چپ",
              "description": "مبل-دیبا-تک نفره تک دسته-دسته سمت چپ-خودرنگ",
              "description_without_wood_color": "مبل-دیبا-تک نفره تک دسته-دسته سمت چپ-",
              "image": "/files/Gemini_Generated_Image_i4243i4243i4243i.webp",
              "creation": "",
              "projected_qty": 0,
              "price_list_rate": 178000000,
              "model": "دیبا",
              "module": "تک نفره تک دسته",
              "module_feature": "دسته سمت چپ",
              "module_length": "",
              "module_width": "",
              "module_height": "",
              "module_diameter": "",
              "module_shape": "",
              "module_color": "",
              "wood_color": "خودرنگ",
              "body_color": "",
              "odd_cloth": 3,
              "even_cloth": 6,
              "minor_cloth": 0,
              "cushion_cloth": 0,
              "Price": 17800000,
              "formatted_Price": "۱۷,۸۰۰,۰۰۰",
              "images": [
                {
                  "name": "bc7b821bcd",
                  "file_name": "Gemini_Generated_Image_i4243i4243i4243i.webp",
                  "file_url": "/files/Gemini_Generated_Image_i4243i4243i4243i.webp",
                  "file_size": 228560,
                  "file_type": "WEBP",
                  "attached_to_name": "مبل دیبا تک نفره تک دسته دسته سمت چپ خودرنگ",
                  "custom_yindex": "",
                  "custom_alt_text": "",
                  "custom_tag": "کاور",
                  "cover": true,
                  "dimentions": false,
                  "gallary": false,
                  "icon": false
                }
              ],
              "stock_qty": 0,
              "yindex": "",
              "variant_of": "",
              "all_wood_colors": [
                "خودرنگ"
              ],
              "is_minor": false,
              "qty": 1,
              "uom": "عدد"
            },
            {