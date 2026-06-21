import frappe
from urllib.parse import quote

def get_context(context):
    context.page_name = "gallery"
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "گالری دن‌روم"

    # ── همه آیتم‌های فعال و قابل نمایش در سایت ──
    items = frappe.db.sql("""
        SELECT
            i.name,
            i.item_name,
            i.description,
            i.item_group,
            i.image
        FROM `tabItem` i
        WHERE i.disabled = 0
          AND COALESCE(i.show_on_site, 0) = 1
        ORDER BY i.creation DESC
    """, as_dict=True)

    gallery_items = []
    filters_list = [{"id": "all", "label": "همه"}]

    if items:
        item_names = [i["name"] for i in items]
        placeholders = ", ".join(["%s"] * len(item_names))

        # ── اتچمنت‌های تصویری از tabFile ──
        attachments = frappe.db.sql(f"""
            SELECT
                f.attached_to_name,
                f.file_url,
                f.file_name
            FROM `tabFile` f
            WHERE f.attached_to_doctype = 'Item'
              AND f.attached_to_name IN ({placeholders})
              AND f.is_private = 0
              AND (
                  f.file_name LIKE '%%.jpg'
                OR f.file_name LIKE '%%.jpeg'
                OR f.file_name LIKE '%%.png'
                OR f.file_name LIKE '%%.webp'
              )
            ORDER BY f.creation ASC
        """, tuple(item_names), as_dict=True)

        # گروه‌بندی تصاویر
        attach_map = {}
        for att in attachments:
            key = att["attached_to_name"]
            if key not in attach_map:
                attach_map[key] = []
            attach_map[key].append(att["file_url"])

        # ساخت URL درست برای هر آیتم
        def make_url(item):
            if item.get("route"):
                return "/" + item["route"]
            # fallback: لینک به صفحه محصول با item name
            return "/product?name=" + quote(item["name"])

        sizes = ["normal", "tall", "wide", "normal", "normal", "tall"]
        seen_groups = set()

        for idx, item in enumerate(items):
            images = attach_map.get(item["name"], [])
            primary_image = images[0] if images else item.get("image")
            if not primary_image:
                continue

            group = item.get("item_group") or "سایر"
            group_slug = frappe.utils.slug(group)

            gallery_items.append({
                "id":       item["name"],
                "title":    item["item_name"] or item["name"],
                "desc":     frappe.utils.strip_html(item.get("description") or ""),
                "category": group,
                "filter":   group_slug,
                "url":      make_url(item),
                "img":      primary_image,
                "images":   images or [primary_image],
                "size":     sizes[idx % len(sizes)],
            })

            if group not in seen_groups:
                seen_groups.add(group)
                filters_list.append({"id": group_slug, "label": group})

    context.gallery_items = gallery_items
    context.gallery_filters = filters_list
