from urllib.parse import quote

import frappe
from frappe.utils import cint

from mysite.www.projects_service import get_projects_payload
from mysite.www.shop_by_look_service import get_shop_by_look_payload


BESTSELLER_KIND_ORDER = [
    "sofa",
    "barstool",
    "chair",
    "dining_table",
    "bench",
    "coffee_table",
]
BESTSELLER_MIN_PER_KIND = {kind: 5 for kind in BESTSELLER_KIND_ORDER}


def _to_toman(value):
    try:
        amount = float(value or 0)
    except Exception:
        return 0
    if amount <= 0:
        return 0
    return int(amount / 10)


def _guess_kind(variant_of, item_name, item_code):
    raw = " ".join([str(variant_of or ""), str(item_name or ""), str(item_code or "")]).lower()
    if "کوسن" in raw or "سرویس خواب" in raw or "تخت" in raw or "تشک" in raw:
        return "other"
    if "صندلی ناهارخوری" in raw and "اپن" not in raw and "بار" not in raw:
        return "chair"
    if "صندلی اپن" in raw or "بار" in raw or "اپن" in raw:
        return "barstool"
    if "نیمکت" in raw or "پاف" in raw:
        return "bench"
    if "میز ناهارخوری" in raw or ("ناهارخوری" in raw and "میز" in raw):
        return "dining_table"
    if (
        "میز جلومبلی" in raw
        or "جلو مبلی" in raw
        or "جلومبلی" in raw
        or "میز عسلی" in raw
        or "عسلی" in raw
        or "باکس" in raw
        or "میز" in raw
    ):
        return "coffee_table"
    return "sofa"


def _route_kind_value(kind):
    if kind in {"dining_table", "coffee_table"}:
        return "table"
    return str(kind or "").strip().lower()


def _extract_model_from_item_name(item_name):
    label = str(item_name or "").strip()
    if not label:
        return ""

    if "مدل " in label:
        label = label.split("مدل ", 1)[1].strip()
    else:
        for prefix in (
            "صندلی اپن ",
            "صندلی ناهارخوری ",
            "کلاف چوبی رنگ شده صندلی اپن ",
            "کلاف چوبی رنگ شده ",
            "میز ناهارخوری ",
            "میز جلومبلی ",
            "میز عسلی ",
            "نیم ست ",
            "ست ",
            "مبل ",
            "مبل راحتی ",
            "کاناپه ",
        ):
            if label.startswith(prefix):
                label = label[len(prefix):].strip()
                break

    for separator in (
        " همراه ",
        " بدون ",
        " آبکاری ",
        " با ",
        " رنگ ",
        " - ",
        " | ",
        " / ",
        "(",
        "،",
        ",",
    ):
        if separator in label:
            label = label.split(separator, 1)[0].strip()

    return " ".join(label.split()).strip()


def _is_generic_model_label(value):
    label = " ".join(str(value or "").split()).strip()
    if not label:
        return True
    if label in {
        "مبل",
        "کاناپه",
        "صندلی اپن",
        "صندلی ناهارخوری",
        "کلاف چوبی رنگ شده",
        "میز",
        "میز ناهارخوری",
        "میز جلومبلی",
        "میز عسلی",
        "نیمکت",
        "پاف",
        "باکس",
        "محصولات",
    }:
        return True
    return False


def _normalize_image(raw):
    image = str(raw or "").strip()
    if not image:
        return "/assets/mysite/img/placeholder.png"
    return image.replace("/private/files/", "/files/")


def _query_bestseller_codes(limit):
    safe_limit = max(6, min(int(limit or 10), 120))
    sql_limit = max(240, safe_limit * 25)

    sold_map = {}
    rank_map = {}

    def absorb_rows(rows):
        for row in rows or []:
            code = str(row.get("item_code") or "").strip()
            if not code:
                continue
            qty = float(row.get("sold_qty") or 0)
            sold_map[code] = float(sold_map.get(code) or 0) + qty
            if code not in rank_map:
                rank_map[code] = len(rank_map)

    try:
        invoice_rows = frappe.db.sql(
            f"""
            SELECT
              sii.item_code AS item_code,
              SUM(COALESCE(sii.qty, 0)) AS sold_qty
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
            WHERE
              si.docstatus = 1
              AND COALESCE(si.is_return, 0) = 0
              AND COALESCE(sii.item_code, '') != ''
            GROUP BY sii.item_code
            ORDER BY sold_qty DESC
            LIMIT {sql_limit}
            """,
            as_dict=True,
        )
    except Exception:
        invoice_rows = []
    absorb_rows(invoice_rows)

    # Count bundle constituents sold through submitted Sales Invoices.
    # This ensures "بسته مبلمان" sales are credited to actual component items.
    try:
        packed_rows = frappe.db.sql(
            f"""
            SELECT
              pi.item_code AS item_code,
              SUM(COALESCE(pi.qty, 0)) AS sold_qty
            FROM `tabPacked Item` pi
            INNER JOIN `tabSales Invoice` si ON si.name = pi.parent
            WHERE
              COALESCE(pi.parenttype, '') = 'Sales Invoice'
              AND si.docstatus = 1
              AND COALESCE(si.is_return, 0) = 0
              AND COALESCE(pi.item_code, '') != ''
            GROUP BY pi.item_code
            ORDER BY sold_qty DESC
            LIMIT {sql_limit}
            """,
            as_dict=True,
        )
    except Exception:
        packed_rows = []
    absorb_rows(packed_rows)

    # Fallback path if packed rows are unavailable for some bundle invoices.
    try:
        exploded_bundle_rows = frappe.db.sql(
            f"""
            SELECT
              pbi.item_code AS item_code,
              SUM(COALESCE(sii.qty, 0) * COALESCE(pbi.qty, 0)) AS sold_qty
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
            INNER JOIN `tabProduct Bundle` pb ON pb.new_item_code = sii.item_code
            INNER JOIN `tabProduct Bundle Item` pbi ON pbi.parent = pb.name
            WHERE
              si.docstatus = 1
              AND COALESCE(si.is_return, 0) = 0
              AND COALESCE(pb.disabled, 0) = 0
              AND COALESCE(pbi.item_code, '') != ''
            GROUP BY pbi.item_code
            ORDER BY sold_qty DESC
            LIMIT {sql_limit}
            """,
            as_dict=True,
        )
    except Exception:
        exploded_bundle_rows = []
    absorb_rows(exploded_bundle_rows)

    try:
        fallback_rows = frappe.db.sql(
            f"""
            SELECT
              i.name AS item_code,
              0 AS sold_qty
            FROM `tabItem` i
            WHERE COALESCE(i.show_on_site, 0) = 1
              AND COALESCE(i.disabled, 0) = 0
            ORDER BY i.modified DESC
            LIMIT {sql_limit}
            """,
            as_dict=True,
        )
    except Exception:
        fallback_rows = []

    for row in fallback_rows:
        code = str(row.get("item_code") or "").strip()
        if not code:
            continue
        if code not in sold_map:
            sold_map[code] = 0
            rank_map[code] = len(rank_map)

    ranked = [
        {
            "item_code": code,
            "sold_qty": float(qty or 0),
            "_rank": int(rank_map.get(code) or 0),
        }
        for code, qty in sold_map.items()
    ]
    ranked.sort(key=lambda row: (-float(row.get("sold_qty") or 0), int(row.get("_rank") or 0), str(row.get("item_code") or "")))
    payload = []
    for row in ranked[:sql_limit]:
        row.pop("_rank", None)
        payload.append(row)
    return payload


def _fetch_bestseller_products(price_list, selected_customer=None, limit=10):
    requested_limit = max(6, int(limit or 10))
    minimum_target = sum(BESTSELLER_MIN_PER_KIND.values())
    safe_limit = max(requested_limit, minimum_target)
    safe_limit = min(safe_limit, 120)
    ranked_rows = _query_bestseller_codes(safe_limit)
    if not ranked_rows:
        return []

    code_rank = []
    sold_map = {}
    for row in ranked_rows:
        code = str(row.get("item_code") or "").strip()
        if not code or code in sold_map:
            continue
        code_rank.append(code)
        sold_map[code] = float(row.get("sold_qty") or 0)

    if not code_rank:
        return []

    item_rows = frappe.get_all(
        "Item",
        filters={"name": ["in", code_rank]},
        fields=[
            "name",
            "item_name",
            "image",
            "variant_of",
            "item_group",
            "show_on_site",
            "disabled",
        ],
        limit_page_length=0,
    )
    item_map = {
        row.name: row
        for row in item_rows
        if cint(row.get("show_on_site") or 0) == 1 and cint(row.get("disabled") or 0) == 0
    }
    if not item_map:
        return []

    valid_codes = [code for code in code_rank if code in item_map]
    if not valid_codes:
        return []

    variant_model_rows = frappe.get_all(
        "Item Variant Attribute",
        filters={
            "parent": ["in", valid_codes],
            "attribute": "مدل محصول",
        },
        fields=["parent", "attribute_value"],
        limit_page_length=0,
    )
    model_by_code = {}
    for row in variant_model_rows:
        parent = str(row.get("parent") or "").strip()
        value = str(row.get("attribute_value") or "").strip()
        if parent and value and parent not in model_by_code:
            model_by_code[parent] = value

    price_rows = []
    if price_list:
        price_rows = frappe.get_all(
            "Item Price",
            filters={"price_list": price_list, "item_code": ["in", valid_codes]},
            fields=["item_code", "price_list_rate"],
            order_by="modified desc",
            limit_page_length=0,
        )
    price_map = {}
    for row in price_rows:
        code = row.get("item_code")
        if code and code not in price_map:
            price_map[code] = row.get("price_list_rate")

    missing_price_codes = [code for code in valid_codes if not price_map.get(code)]
    if missing_price_codes:
        try:
            fallback_price_rows = frappe.db.sql(
                """
                SELECT
                  ip.item_code,
                  ip.price_list_rate
                FROM `tabItem Price` ip
                INNER JOIN `tabPrice List` pl ON pl.name = ip.price_list
                WHERE ip.item_code IN %(codes)s
                  AND COALESCE(pl.selling, 0) = 1
                  AND COALESCE(pl.enabled, 1) = 1
                ORDER BY ip.modified DESC
                """,
                {"codes": tuple(missing_price_codes)},
                as_dict=True,
            )
        except Exception:
            fallback_price_rows = []

        for row in fallback_price_rows:
            code = row.get("item_code")
            if code and code not in price_map:
                price_map[code] = row.get("price_list_rate")

    parent_codes = []
    for code in valid_codes:
        variant_of = str((item_map.get(code) or {}).get("variant_of") or "").strip()
        if variant_of and variant_of not in parent_codes:
            parent_codes.append(variant_of)

    parent_map = {}
    if parent_codes:
        parent_rows = frappe.get_all(
            "Item",
            filters={"name": ["in", parent_codes]},
            fields=["name", "item_name", "image", "item_group"],
            limit_page_length=0,
        )
        parent_map = {row.name: row for row in parent_rows}
        parent_model_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={
                "parent": ["in", parent_codes],
                "attribute": "مدل محصول",
            },
            fields=["parent", "attribute_value"],
            limit_page_length=0,
        )
        for row in parent_model_rows:
            parent = str(row.get("parent") or "").strip()
            value = str(row.get("attribute_value") or "").strip()
            if parent and value and parent not in model_by_code:
                model_by_code[parent] = value

    grouped_kinds = set(BESTSELLER_KIND_ORDER)
    grouped_models = {}
    singles = []

    for rank, code in enumerate(valid_codes):
        item = item_map.get(code)
        if not item:
            continue

        variant_of = str(item.get("variant_of") or "").strip()
        parent_item = parent_map.get(variant_of) if variant_of else None

        kind = _guess_kind(item.get("variant_of"), item.get("item_name"), item.get("name"))
        if kind not in BESTSELLER_MIN_PER_KIND:
            continue

        item_model = str(model_by_code.get(code) or "").strip()
        parent_model = str(model_by_code.get(variant_of) or "").strip() if variant_of else ""
        model_name = " ".join((item_model or parent_model).split()).strip()
        extracted_model = _extract_model_from_item_name(item.get("item_name"))
        if not model_name and extracted_model and len(extracted_model.split()) <= 3 and not _is_generic_model_label(extracted_model):
            model_name = extracted_model
        fallback_model_name = extracted_model
        if not fallback_model_name:
            fallback_model_name = str(
                (parent_item.get("item_name") if parent_item else "")
                or item.get("item_name")
                or item.get("name")
                or ""
            ).strip()
        fallback_model_name = " ".join(fallback_model_name.split()).strip()

        item_group = str(
            (parent_item.get("item_group") if parent_item else "")
            or item.get("item_group")
            or ""
        ).strip()
        image = _normalize_image((parent_item.get("image") if parent_item else "") or item.get("image"))
        sold_qty = int(round(float(sold_map.get(code) or 0)))
        base_price = _to_toman(price_map.get(code))

        route_target_name = str(model_name or fallback_model_name or item.get("item_name") or item.get("name") or "").strip()
        route_kind = _route_kind_value(kind)
        route = f"/product?name={quote(str(route_target_name or model_name))}&kind={quote(str(route_kind))}"
        if selected_customer:
            route = f"{route}&customer={quote(str(selected_customer))}"

        can_group_by_model = kind in grouped_kinds and bool(model_name) and not _is_generic_model_label(model_name)
        if can_group_by_model:
            model_identifier = model_name
            group_key = f"{kind}::{model_identifier}"
            current = grouped_models.get(group_key)
            if not current:
                grouped_models[group_key] = {
                    "id": f"model-{kind}-{quote(str(model_identifier), safe='')}",
                    "item_code": model_identifier,
                    "title": model_name,
                    "subtitle": item_group,
                    "image": image,
                    "base_price": base_price if base_price > 0 else 0,
                    "sold_qty": sold_qty,
                    "kind": kind,
                    "item_group": item_group,
                    "route": route,
                    "_rank": rank,
                }
            else:
                current["sold_qty"] += sold_qty
                current["_rank"] = min(int(current.get("_rank") or rank), rank)
                if (not current.get("subtitle")) and item_group:
                    current["subtitle"] = item_group
                    current["item_group"] = item_group
                if current.get("image") == "/assets/mysite/img/placeholder.png" and image != "/assets/mysite/img/placeholder.png":
                    current["image"] = image
                if base_price > 0 and (not current.get("base_price") or int(current.get("base_price") or 0) <= 0 or base_price < int(current.get("base_price") or 0)):
                    current["base_price"] = base_price
            continue

        subtitle = str(item.get("variant_of") or item_group or "").strip()
        singles.append(
            {
                "id": code,
                "item_code": code,
                "title": str(item.get("item_name") or fallback_model_name or code).strip(),
                "subtitle": subtitle,
                "image": image,
                "base_price": base_price,
                "sold_qty": sold_qty,
                "kind": kind,
                "item_group": item_group,
                "route": route,
                "_rank": rank,
            }
        )

    combined = list(grouped_models.values()) + singles
    combined.sort(key=lambda row: (-int(row.get("sold_qty") or 0), int(row.get("_rank") or 0)))
    categorized_rows = {kind: [] for kind in BESTSELLER_KIND_ORDER}
    for row in combined:
        kind = str(row.get("kind") or "").strip().lower()
        if kind in categorized_rows:
            categorized_rows[kind].append(row)

    payload = []
    used_ids = set()

    def append_row(row):
        row_id = str(row.get("id") or row.get("item_code") or "").strip()
        if not row_id or row_id in used_ids:
            return False
        used_ids.add(row_id)
        item = dict(row)
        item.pop("_rank", None)
        payload.append(item)
        return True

    # Ensure at least 5 items per requested category (if available).
    for kind in BESTSELLER_KIND_ORDER:
        need = int(BESTSELLER_MIN_PER_KIND.get(kind) or 0)
        if need <= 0:
            continue
        taken = 0
        for row in categorized_rows.get(kind, []):
            if append_row(row):
                taken += 1
            if taken >= need:
                break

    for row in combined:
        if len(payload) >= safe_limit:
            break
        append_row(row)

    return payload[:safe_limit]

def get_context(context):
    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    shop_payload = get_shop_by_look_payload(
        requested_customer=requested_customer,
        only_homepage=True,
        limit=6,
    )
    projects_payload = get_projects_payload(
        requested_customer=requested_customer,
        only_homepage=True,
        limit=6,
    )
    selected_customer = shop_payload.get("SelectedCustomer", "")
    selected_price_list = shop_payload.get("SelectedPriceList", "") or frappe.db.get_single_value("Selling Settings", "selling_price_list")
    best_sellers = _fetch_bestseller_products(
        price_list=selected_price_list,
        selected_customer=selected_customer,
        limit=10,
    )

    context.boot = {
        "Categories": frappe.get_all("Item Group", fields=["name", "image", "route"]),
        "ShopByLookHighlights": shop_payload.get("ShopByLookScenes", []),
        "ProjectHighlights": projects_payload.get("Projects", []),
        "BestSellerProducts": best_sellers,
        "SelectedCustomer": selected_customer,
        "SelectedPriceList": selected_price_list,
        "PriceSource": shop_payload.get("PriceSource", "default"),
    }
    return context
