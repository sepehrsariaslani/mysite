"""
cloth.py - Shared module for fetching ClothGroups data
Used by both barstools.py and sofas.py controllers.
"""

import re

import frappe


def get_cloth_groups(price_list_param=None):
    """
    Fetch all cloth (پارچه) groups with their variants, prices, sample images and cloth_nature.
    Returns a list of ClothGroup dicts compatible with the Vue frontend.
    """

    def to_persian_digits(number):
        persian_digits = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        text = str(number)
        for en, fa in persian_digits.items():
            text = text.replace(en, fa)
        return text

    def fmt_toman(rial_price):
        if not rial_price:
            return "۰"
        toman = int(rial_price / 10)
        s = str(toman)
        formatted = ",".join([s[::-1][i:i+3] for i in range(0, len(s), 3)])[::-1]
        return to_persian_digits(formatted)

    def is_persian(text):
        for ch in str(text):
            if '\u0600' <= ch <= '\u06FF':
                continue
            if ch in ' 0123456789':
                continue
            return False
        return True

    def extract_code(item):
        direct_code = (item.get("cloth_code") or "").strip()
        if direct_code:
            return direct_code
        text = str(item.get("item_name") or item.get("name") or "").strip()
        if not text:
            return ""
        # Prefer the trailing numeric token in names like "پارچه فلان 301"
        matches = re.findall(r"([0-9\u06F0-\u06F9]+)", text)
        if not matches:
            return ""
        return matches[-1]

    try:
        # 1. Fetch all cloth items with their group attribute
        all_cloth_items = frappe.db.sql("""
            SELECT
                i.*,
                quality_attr.attribute_value as cloth_group,
                code_attr.attribute_value as cloth_code,
                bucket_attr.attribute_value as cloth_bucket
            FROM `tabItem` i
            INNER JOIN `tabItem Variant Attribute` quality_attr ON i.name = quality_attr.parent
            LEFT JOIN `tabItem Variant Attribute` code_attr
                ON i.name = code_attr.parent AND code_attr.attribute = 'کد'
            LEFT JOIN `tabItem Variant Attribute` bucket_attr
                ON i.name = bucket_attr.parent AND bucket_attr.attribute = 'گروه'
            WHERE i.variant_of = 'پارچه' AND i.item_group = 'پارچه'
            AND quality_attr.attribute = 'کالیته پارچه'
        """, as_dict=True)

        # 2. Build groups (only Persian group names)
        groups_set = set()
        items_by_group = {}
        all_keys = set()
        for item in all_cloth_items:
            g = item.cloth_group
            if g and is_persian(g):
                groups_set.add(g)
                items_by_group.setdefault(g, []).append(item)
                if item.name: all_keys.add(item.name)
                if item.item_code: all_keys.add(item.item_code)

        sorted_groups = sorted(list(groups_set))

        # 3. Fetch selling prices
        cloth_prices = {}
        if all_keys:
            keys_list = list(all_keys)
            ph = ','.join(['%s'] * len(keys_list))
            selling = frappe.db.sql(
                f"SELECT item_code, price_list, price_list_rate FROM `tabItem Price` WHERE item_code IN ({ph}) AND selling=1",
                tuple(keys_list), as_dict=True
            )
            for p in selling:
                cloth_prices.setdefault(p.item_code, {})[p.price_list] = p.price_list_rate

        # 4. Fetch sample cover images and cloth_nature per group
        sample_images = {}
        sample_natures = {}
        if sorted_groups:
            ph = ','.join(['%s'] * len(sorted_groups))
            covers = frappe.db.sql(
                f"""SELECT iva.attribute_value as cloth_group, i.image, i.cloth_nature
                    FROM `tabItem` i
                    INNER JOIN `tabItem Variant Attribute` iva ON i.name = iva.parent
                    WHERE iva.attribute_value IN ({ph})
                    AND i.variant_of='پارچه' AND i.cloth_cover='1' AND i.image IS NOT NULL
                    ORDER BY i.creation ASC""",
                tuple(sorted_groups), as_dict=True
            )
            for row in covers:
                if row.cloth_group not in sample_images:
                    sample_images[row.cloth_group] = row.image
                if row.cloth_nature and row.cloth_group not in sample_natures:
                    sample_natures[row.cloth_group] = row.cloth_nature

        # 5. Assemble result
        result = []
        for group in sorted_groups:
            items = items_by_group.get(group, [])
            if not items:
                continue

            max_rial = 0
            cloth_variants = []

            for item in items:
                ip = cloth_prices.get(item.item_code) or cloth_prices.get(item.name, {})
                p = (
                    ip.get("Standard Selling")
                    or (ip.get(price_list_param) if price_list_param else None)
                    or 0
                )
                if p and p > max_rial:
                    max_rial = p

                cloth_variants.append({
                    "name": item.get("item_name") or item.get("name") or "",
                    "item_name": item.get("item_name") or "",
                    "item_code": item.get("item_code") or item.get("name") or "",
                    "image": item.get("image") or "",
                    "code": extract_code(item),
                    "bucket": (item.get("cloth_bucket") or "").strip(),
                    "quality": group,
                    "Price": int(p / 10) if p else 0,
                    "formatted_Price": fmt_toman(p),
                })

            result.append({
                "name": group,
                "average_purchase_price": fmt_toman(max_rial),
                "sample_image": sample_images.get(group) or "",
                "cloth_nature": sample_natures.get(group) or "",
                "clothvariants": cloth_variants,
            })

        return result

    except Exception as e:
        frappe.log_error(f"cloth.get_cloth_groups error: {e}")
        return []
