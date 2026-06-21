import json
import hashlib
import os
import re
import ipaddress
import socket
import tempfile
from html import escape as html_escape, unescape as html_unescape
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from pathlib import Path
from datetime import datetime

import frappe
from jinja2 import TemplateSyntaxError
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils.jinja import get_jenv
from frappe.utils import add_days, cint, flt, get_url, markdown, now_datetime, strip_html

from mysite.management_audit import log_event as audit_log_event
from mysite.management_permissions import (
    can_access_management as can_access_management_permission,
    context as permission_context,
    has_capability,
    is_super_admin,
    require_capability,
)
from mysite.management_workflow import (
    default_capability_for_target,
    create_change_request,
    get_change_request,
    list_change_requests,
    module_for_target_type,
    parse_request_payload,
    shadow_create_if_enabled,
    should_enforce,
    transition_change_request,
    workflow_mode,
)


@frappe.whitelist(allow_guest=True)
def get_dealers():
    return frappe.get_all("MySite Dealer", fields=["dealer_name as name", "province", "city", "phone", "work_hours", "badge"])


def _blog_available_fields():
    return _available_fields("Blog Post")


def _available_fields(doctype):
    if not frappe.db.exists("DocType", doctype):
        return set()
    try:
        meta = frappe.get_meta(doctype)
        return {f.fieldname for f in meta.fields if f.fieldname}
    except Exception:
        return set()


def _clean_excerpt(*candidates):
    for candidate in candidates:
        text = strip_html(str(candidate or "")).strip()
        if text:
            return text[:220]
    return ""


def _normalize_body_candidate(candidate):
    raw = str(candidate or "").strip()
    if not raw:
        return ""
    if "\\n" in raw and "\n" not in raw:
        raw = raw.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
    return raw.strip()


def _html_has_meaningful_content(raw_html):
    raw = str(raw_html or "").strip()
    if not raw:
        return False
    lower = raw.lower()
    if any(tag in lower for tag in ("<img", "<picture", "<video", "<iframe", "<table", "<ul", "<ol", "<blockquote", "<h1", "<h2", "<h3", "<h4", "<h5", "<h6")):
        return True
    return bool(strip_html(raw).replace("\xa0", " ").strip())


def _resolve_post_body_html(row):
    candidates = [
        row.get("custom_article_body"),
        row.get("content_html"),
        row.get("content_md"),
        row.get("content"),
        row.get("blog_intro"),
        row.get("meta_description"),
    ]
    for candidate in candidates:
        raw = _normalize_body_candidate(candidate)
        if not raw:
            continue
        if "<" in raw and ">" in raw:
            if not _html_has_meaningful_content(raw):
                continue
            return raw
        rendered = str(markdown(raw))
        if _html_has_meaningful_content(rendered):
            return rendered
    return ""


def _estimate_read_time(post_row):
    custom_value = str(post_row.get("custom_read_time") or "").strip()
    if custom_value:
        return custom_value
    text = strip_html(_resolve_post_body_html(post_row))
    words = max(1, len(text.split()))
    minutes = max(1, round(words / 220))
    return f"{minutes} دقیقه"


def _serialize_blog_post(row, include_content=False):
    name = str(row.get("name") or "").strip()
    category = str(row.get("blog_category") or "مجله دن‌روم").strip() or "مجله دن‌روم"
    title = str(row.get("title") or name).strip() or "بدون عنوان"
    route = f"/blog?post={quote(name)}"

    payload = {
        "id": name,
        "name": name,
        "title": title,
        "route": route,
        "category": category,
        "blog_category": category,
        "published_on": row.get("published_on"),
        "read_time": _estimate_read_time(row),
        "custom_read_time": _estimate_read_time(row),
        "image": row.get("meta_image") or "/assets/mysite/img/placeholder.png",
        "meta_image": row.get("meta_image") or "/assets/mysite/img/placeholder.png",
        "excerpt": _clean_excerpt(
            row.get("meta_description"),
            row.get("blog_intro"),
            row.get("custom_article_body"),
            row.get("content_html"),
            row.get("content_md"),
            row.get("content"),
        ),
        "meta_description": _clean_excerpt(
            row.get("meta_description"),
            row.get("blog_intro"),
            row.get("custom_article_body"),
            row.get("content_html"),
            row.get("content_md"),
            row.get("content"),
        ),
        "subtitle": str(row.get("custom_subtitle") or "").strip(),
        "cover_credit": str(row.get("custom_cover_credit") or "").strip(),
        "cta_label": str(row.get("custom_cta_label") or "").strip(),
        "cta_link": str(row.get("custom_cta_link") or "").strip(),
    }
    if include_content:
        payload["content"] = _resolve_post_body_html(row)
    return payload


def _guess_item_kind(variant_of, item_name, item_code):
    raw = " ".join([str(variant_of or ""), str(item_name or ""), str(item_code or "")]).lower()
    if "صندلی ناهارخوری" in raw and "اپن" not in raw and "بار" not in raw:
        return "chair"
    if "صندلی اپن" in raw or "بار" in raw or "اپن" in raw:
        return "barstool"
    if "نیمکت" in raw or "پاف" in raw:
        return "bench"
    if "میز" in raw or "جلومبلی" in raw or "عسلی" in raw or "باکس" in raw:
        return "table"
    return "sofa"


def _default_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _to_toman(price):
    try:
        amount = float(price or 0)
    except Exception:
        return 0
    if amount <= 0:
        return 0
    return int(amount / 10)


MANAGEMENT_PRODUCT_FEATURES_FIELD = "custom_management_features_json"


def _normalize_management_feature_rows(raw_rows):
    rows = raw_rows
    if isinstance(rows, str):
        stripped = rows.strip()
        if not stripped:
            rows = []
        else:
            try:
                rows = frappe.parse_json(stripped)
            except Exception:
                try:
                    rows = json.loads(stripped)
                except Exception:
                    rows = []

    if isinstance(rows, dict):
        rows = rows.get("rows") or rows.get("items") or []
    if not isinstance(rows, (list, tuple)):
        return []

    normalized = []
    for row in rows:
        label = ""
        value = ""
        if isinstance(row, dict):
            label = str(row.get("label") or row.get("name") or row.get("title") or "").strip()
            value = str(row.get("value") or row.get("content") or row.get("description") or "").strip()
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            label = str(row[0] or "").strip()
            value = str(row[1] or "").strip()
        else:
            continue

        if not label and not value:
            continue
        normalized.append(
            {
                "label": label[:140],
                "value": value[:800],
            }
        )
        if len(normalized) >= 50:
            break
    return normalized


def ensure_management_product_custom_fields():
    if not frappe.db.exists("DocType", "Item"):
        return
    item_fields = _available_fields("Item")
    if MANAGEMENT_PRODUCT_FEATURES_FIELD in item_fields:
        return
    custom_fields = {
        "Item": [
            {
                "fieldname": MANAGEMENT_PRODUCT_FEATURES_FIELD,
                "label": "Management Features JSON",
                "fieldtype": "Long Text",
                "insert_after": "description",
                "hidden": 1,
            }
        ]
    }
    create_custom_fields(custom_fields)


def _serialize_management_price_row(row):
    rate = flt(row.get("price_list_rate") or 0)
    return {
        "name": str(row.get("name") or "").strip(),
        "item_code": str(row.get("item_code") or "").strip(),
        "price_list": str(row.get("price_list") or "").strip(),
        "currency": str(row.get("currency") or "IRR").strip() or "IRR",
        "uom": str(row.get("uom") or "").strip(),
        "rate": rate,
        "rate_toman": _to_toman(rate),
        "selling": bool(cint(row.get("selling") if row.get("selling") is not None else 1)),
        "buying": bool(cint(row.get("buying") or 0)),
        "valid_from": row.get("valid_from"),
        "valid_upto": row.get("valid_upto"),
        "modified": row.get("modified"),
    }


def _fetch_item_price_rows(item_codes):
    item_codes = [str(code or "").strip() for code in (item_codes or []) if str(code or "").strip()]
    if not item_codes or not frappe.db.exists("DocType", "Item Price"):
        return {}

    price_fields = _available_fields("Item Price")
    fields = ["name", "item_code", "price_list", "price_list_rate", "modified"]
    for optional in ["currency", "uom", "selling", "buying", "valid_from", "valid_upto"]:
        if optional in price_fields:
            fields.append(optional)

    rows = frappe.get_all(
        "Item Price",
        filters={"item_code": ["in", item_codes]},
        fields=fields,
        order_by="modified desc",
        limit_page_length=6000,
    )

    result = {}
    for row in rows:
        item_code = str(row.get("item_code") or "").strip()
        if not item_code:
            continue
        result.setdefault(item_code, []).append(_serialize_management_price_row(row))
    return result


def _list_management_price_lists(default_price_list=""):
    default_price_list = str(default_price_list or "").strip()
    if not frappe.db.exists("DocType", "Price List"):
        return []

    price_fields = _available_fields("Price List")
    fields = ["name"]
    for optional in ["currency", "enabled", "selling", "title"]:
        if optional in price_fields:
            fields.append(optional)

    filters = {}
    if "enabled" in price_fields:
        filters["enabled"] = 1
    if "selling" in price_fields:
        filters["selling"] = 1

    rows = frappe.get_all(
        "Price List",
        filters=filters,
        fields=fields,
        order_by="name asc",
        limit_page_length=500,
    )

    names = {str(row.get("name") or "").strip() for row in rows}
    if default_price_list and default_price_list not in names and frappe.db.exists("Price List", default_price_list):
        extra = frappe.get_all(
            "Price List",
            filters={"name": default_price_list},
            fields=fields,
            limit_page_length=1,
        )
        if extra:
            rows = extra + rows

    payload = []
    for row in rows:
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        payload.append(
            {
                "name": name,
                "title": str(row.get("title") or name).strip(),
                "currency": str(row.get("currency") or "IRR").strip() or "IRR",
                "is_default": bool(default_price_list and name == default_price_list),
            }
        )
    return payload


def _normalize_management_price_rows(raw_rows):
    rows = raw_rows
    if isinstance(rows, str):
        try:
            rows = frappe.parse_json(rows)
        except Exception:
            try:
                rows = json.loads(rows or "[]")
            except Exception:
                rows = []

    if not isinstance(rows, (list, tuple)):
        return []

    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        price_list = str(row.get("price_list") or "").strip()
        if not price_list:
            continue
        normalized.append(
            {
                "name": str(row.get("name") or "").strip(),
                "price_list": price_list,
                "currency": str(row.get("currency") or "").strip(),
                "uom": str(row.get("uom") or "").strip(),
                "rate": flt(row.get("rate") or 0),
                "selling": 1 if _to_bool(row.get("selling"), True) else 0,
                "buying": 1 if _to_bool(row.get("buying"), False) else 0,
                "valid_from": row.get("valid_from"),
                "valid_upto": row.get("valid_upto"),
            }
        )
        if len(normalized) >= 150:
            break
    return normalized


def _upsert_management_item_prices(item_code, raw_price_rows=None, raw_deleted_names=None):
    if not item_code or not frappe.db.exists("DocType", "Item Price"):
        return

    price_fields = _available_fields("Item Price")
    price_rows = _normalize_management_price_rows(raw_price_rows)
    deleted_names = raw_deleted_names
    if isinstance(deleted_names, str):
        try:
            deleted_names = frappe.parse_json(deleted_names)
        except Exception:
            deleted_names = [deleted_names]
    if not isinstance(deleted_names, (list, tuple)):
        deleted_names = []

    for raw_name in deleted_names:
        name = str(raw_name or "").strip()
        if not name or not frappe.db.exists("Item Price", name):
            continue
        existing_item = frappe.db.get_value("Item Price", name, "item_code")
        if str(existing_item or "").strip() != item_code:
            continue
        frappe.delete_doc("Item Price", name, ignore_permissions=True, force=1)

    for row in price_rows:
        row_name = str(row.get("name") or "").strip()
        target_doc = None

        if row_name and frappe.db.exists("Item Price", row_name):
            doc = frappe.get_doc("Item Price", row_name)
            if str(doc.item_code or "").strip() == item_code:
                target_doc = doc

        if not target_doc:
            dedupe_filters = {"item_code": item_code, "price_list": row.get("price_list")}
            if row.get("uom") and "uom" in price_fields:
                dedupe_filters["uom"] = row.get("uom")
            existing = frappe.get_all(
                "Item Price",
                filters=dedupe_filters,
                fields=["name"],
                order_by="modified desc",
                limit_page_length=1,
            )
            if existing:
                target_doc = frappe.get_doc("Item Price", existing[0].get("name"))

        is_new = False
        if not target_doc:
            target_doc = frappe.get_doc({"doctype": "Item Price"})
            is_new = True

        target_doc.item_code = item_code
        target_doc.price_list = row.get("price_list")
        if "price_list_rate" in price_fields:
            target_doc.price_list_rate = flt(row.get("rate") or 0)
        if "currency" in price_fields:
            target_doc.currency = (
                row.get("currency")
                or frappe.db.get_value("Price List", row.get("price_list"), "currency")
                or "IRR"
            )
        if "uom" in price_fields:
            target_doc.uom = row.get("uom") or ""
        if "selling" in price_fields:
            target_doc.selling = cint(row.get("selling") or 0)
        if "buying" in price_fields:
            target_doc.buying = cint(row.get("buying") or 0)
        if "valid_from" in price_fields:
            target_doc.valid_from = row.get("valid_from")
        if "valid_upto" in price_fields:
            target_doc.valid_upto = row.get("valid_upto")

        if is_new:
            target_doc.insert(ignore_permissions=True)
        else:
            target_doc.save(ignore_permissions=True)


def _get_related_products_for_post(post_name):
    if not post_name:
        return []
    if not frappe.db.exists("DocType", "Blog Post Product"):
        return []

    row_fields = _available_fields("Blog Post Product")
    if not row_fields:
        return []

    filters = {"parent": post_name}
    if "is_active" in row_fields:
        filters["is_active"] = 1

    selected_fields = ["name", "parent", "idx", "item_code", "custom_label", "note", "custom_image", "sort_order"]
    core_fields = {"name", "parent", "idx"}
    fields = [f for f in selected_fields if f in core_fields or f in row_fields]
    order_by = "sort_order asc, idx asc" if "sort_order" in row_fields else "idx asc"
    rows = frappe.get_all(
        "Blog Post Product",
        filters=filters,
        fields=fields,
        order_by=order_by,
        limit_page_length=100,
    )
    if not rows:
        return []

    item_codes = [row.item_code for row in rows if row.get("item_code")]
    if not item_codes:
        return []

    item_fields = _available_fields("Item")
    wanted_item_fields = ["name", "item_name", "image", "variant_of", "item_group", "show_on_site", "disabled"]
    final_item_fields = [f for f in wanted_item_fields if f in item_fields or f == "name"]
    item_rows = frappe.get_all(
        "Item",
        filters={"name": ["in", item_codes]},
        fields=final_item_fields,
        limit_page_length=0,
    )
    item_map = {
        row.name: row
        for row in item_rows
        if cint(row.get("disabled") or 0) == 0 and cint(row.get("show_on_site") or 1) == 1
    }

    price_rows = []
    default_pl = _default_price_list()
    if default_pl:
        price_rows = frappe.get_all(
            "Item Price",
            filters={"price_list": default_pl, "item_code": ["in", list(item_map.keys())]},
            fields=["item_code", "price_list_rate"],
            limit_page_length=0,
        )
    price_map = {}
    for row in price_rows:
        code = row.get("item_code")
        if code and code not in price_map:
            price_map[code] = row.get("price_list_rate")

    payload = []
    for row in rows:
        item_code = row.get("item_code")
        item = item_map.get(item_code)
        if not item:
            continue
        model_name = item.get("variant_of") or item.get("item_name") or item.get("name")
        kind = _guess_item_kind(item.get("variant_of"), item.get("item_name"), item.get("name"))
        payload.append(
            {
                "id": row.get("name"),
                "item_code": item_code,
                "title": str(row.get("custom_label") or item.get("item_name") or item_code).strip(),
                "note": str(row.get("note") or "").strip(),
                "image": row.get("custom_image") or item.get("image") or "/assets/mysite/img/placeholder.png",
                "base_price": _to_toman(price_map.get(item_code)),
                "route": f"/product?name={quote(str(model_name))}&kind={quote(kind)}",
            }
        )
    return payload


def _resolve_blog_name(identifier):
    raw = str(identifier or "").strip()
    if not raw:
        return ""

    if frappe.db.exists("Blog Post", raw):
        is_published = frappe.db.get_value("Blog Post", raw, "published")
        if int(is_published or 0) == 1:
            return raw

    route_value = raw.lstrip("/")

    by_route = frappe.get_all(
        "Blog Post",
        filters={"published": 1, "route": route_value},
        fields=["name"],
        limit_page_length=1,
    )
    if by_route:
        return by_route[0].name

    by_title = frappe.get_all(
        "Blog Post",
        filters={"published": 1, "title": raw},
        fields=["name"],
        limit_page_length=1,
    )
    if by_title:
        return by_title[0].name
    return ""


@frappe.whitelist(allow_guest=True)
def get_blog_posts(limit=3, search=None, category=None):
    if not frappe.db.exists("DocType", "Blog Post"):
        return []

    available_fields = _blog_available_fields()
    wanted_fields = [
        "name",
        "title",
        "blog_category",
        "published_on",
        "content",
        "content_html",
        "content_md",
        "custom_article_body",
        "meta_description",
        "meta_image",
        "route",
        "blog_intro",
        "custom_read_time",
        "custom_subtitle",
        "custom_cover_credit",
        "custom_cta_label",
        "custom_cta_link",
    ]
    final_fields = [f for f in wanted_fields if f == "name" or f in available_fields]

    filters = {"published": 1}
    selected_category = str(category or "").strip()
    if selected_category and selected_category != "all" and "blog_category" in available_fields:
        filters["blog_category"] = selected_category

    query = str(search or "").strip()
    or_filters = None
    if query:
        like_query = f"%{query}%"
        or_filters = {"title": ["like", like_query]}
        if "blog_intro" in available_fields:
            or_filters["blog_intro"] = ["like", like_query]
        if "custom_article_body" in available_fields:
            or_filters["custom_article_body"] = ["like", like_query]
        if "meta_description" in available_fields:
            or_filters["meta_description"] = ["like", like_query]
        if "content_md" in available_fields:
            or_filters["content_md"] = ["like", like_query]
        if "content_html" in available_fields:
            or_filters["content_html"] = ["like", like_query]
        if "content" in available_fields:
            or_filters["content"] = ["like", like_query]

    rows = frappe.get_all(
        "Blog Post",
        fields=final_fields,
        filters=filters,
        or_filters=or_filters,
        order_by="published_on desc, modified desc",
        limit_page_length=max(1, min(cint(limit) or 3, 120)),
    )
    return [_serialize_blog_post(row, include_content=False) for row in rows]


@frappe.whitelist(allow_guest=True)
def get_blog_post_detail(post=None, name=None, route=None):
    if not frappe.db.exists("DocType", "Blog Post"):
        return {"post": None, "related_posts": []}

    identifier = post or name or route or frappe.form_dict.get("post") or frappe.form_dict.get("name")
    resolved_name = _resolve_blog_name(identifier)
    if not resolved_name:
        return {"post": None, "related_posts": []}

    available_fields = _blog_available_fields()
    wanted_fields = [
        "name",
        "title",
        "blog_category",
        "published_on",
        "content",
        "content_html",
        "content_md",
        "custom_article_body",
        "meta_description",
        "meta_image",
        "route",
        "blog_intro",
        "custom_read_time",
        "custom_subtitle",
        "custom_cover_credit",
        "custom_cta_label",
        "custom_cta_link",
    ]
    final_fields = [f for f in wanted_fields if f == "name" or f in available_fields]

    rows = frappe.get_all(
        "Blog Post",
        fields=final_fields,
        filters={"name": resolved_name, "published": 1},
        limit_page_length=1,
    )
    if not rows:
        return {"post": None, "related_posts": []}

    row = rows[0]
    post_payload = _serialize_blog_post(row, include_content=True)
    post_payload["related_products"] = _get_related_products_for_post(resolved_name)
    category = row.get("blog_category")

    related_filters = {"published": 1, "name": ["!=", resolved_name]}
    if category and "blog_category" in available_fields:
        related_filters["blog_category"] = category

    related_rows = frappe.get_all(
        "Blog Post",
        fields=final_fields,
        filters=related_filters,
        order_by="published_on desc, modified desc",
        limit_page_length=4,
    )
    related_posts = [_serialize_blog_post(r, include_content=False) for r in related_rows]

    return {
        "post": post_payload,
        "related_posts": related_posts,
    }


@frappe.whitelist(allow_guest=True)
def get_blog_categories():
    if not frappe.db.exists("DocType", "Blog Post"):
        return []
    rows = frappe.db.sql(
        """
        SELECT DISTINCT blog_category
        FROM `tabBlog Post`
        WHERE published = 1 AND COALESCE(blog_category, '') != ''
        ORDER BY blog_category ASC
        """,
        as_dict=True,
    )
    return [row.blog_category for row in rows if row.blog_category]


def _management_blog_available_fields():
    return _blog_available_fields()


def _list_management_blog_categories(available_fields=None):
    field_set = set(available_fields or _management_blog_available_fields())
    categories = []
    seen = set()

    if frappe.db.exists("DocType", "Blog Category"):
        rows = frappe.get_all("Blog Category", fields=["name"], order_by="name asc", limit_page_length=300)
        for row in rows:
            name = str(row.get("name") or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            categories.append(name)

    if "blog_category" in field_set:
        extra = frappe.db.sql(
            """
            SELECT DISTINCT blog_category
            FROM `tabBlog Post`
            WHERE COALESCE(blog_category, '') != ''
            ORDER BY blog_category ASC
            """,
            as_dict=True,
        )
        for row in extra:
            name = str(row.get("blog_category") or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            categories.append(name)

    return categories


def _blog_route_slug(value):
    text = str(value or "").strip().replace("/", " ").replace("_", " ")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^0-9A-Za-z\u0600-\u06FF\-]+", "", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "blog-post"


def _normalize_management_blog_route(route, title, post_name=None):
    raw = str(route or "").strip()
    if raw:
        raw = raw.strip("/")
        if raw.startswith("blog/"):
            raw = raw[len("blog/"):]
    slug = _blog_route_slug(raw or title)

    candidate = slug
    suffix = 2
    while True:
        exists_filters = {"route": candidate}
        if post_name:
            exists_filters["name"] = ["!=", post_name]
        if not frappe.db.exists("Blog Post", exists_filters):
            break
        candidate = f"{slug}-{suffix}"
        suffix += 1
        if suffix > 2000:
            break
    return candidate


def _default_blogger_for_user(available_fields=None):
    field_set = set(available_fields or _management_blog_available_fields())
    if "blogger" not in field_set or not frappe.db.exists("DocType", "Blogger"):
        return ""
    try:
        if "user" in _available_fields("Blogger"):
            by_user = frappe.db.get_value("Blogger", {"user": frappe.session.user}, "name")
            if by_user:
                return by_user
        first_blogger = frappe.db.get_value("Blogger", {}, "name")
        return str(first_blogger or "").strip()
    except Exception:
        return ""


def _serialize_management_blog_row(row, include_body=False):
    name = str(row.get("name") or "").strip()
    title = str(row.get("title") or "").strip() or name or "بدون عنوان"
    published = bool(cint(row.get("published") or 0))
    featured = bool(cint(row.get("featured") or 0))
    status_key = "published" if published else "draft"
    status_label = "منتشر شده" if published else "پیش‌نویس"
    if featured:
        status_key = "featured" if published else "featured_draft"
        status_label = "ویژه" if published else "ویژه (پیش‌نویس)"

    body_html = _resolve_post_body_html(row)
    excerpt = _clean_excerpt(row.get("blog_intro"), row.get("meta_description"), body_html)
    plain_text = strip_html(body_html or row.get("blog_intro") or row.get("meta_description") or "")
    word_count = len([chunk for chunk in plain_text.split() if chunk])

    payload = {
        "name": name,
        "title": title,
        "blog_category": str(row.get("blog_category") or "").strip(),
        "blogger": str(row.get("blogger") or "").strip(),
        "route": str(row.get("route") or "").strip(),
        "preview_url": f"/blog?post={quote(name)}" if name else "/blog",
        "published": published,
        "published_on": row.get("published_on"),
        "featured": featured,
        "disable_comments": bool(cint(row.get("disable_comments") or 0)),
        "disable_likes": bool(cint(row.get("disable_likes") or 0)),
        "hide_cta": bool(cint(row.get("hide_cta") or 0)),
        "meta_image": str(row.get("meta_image") or "").strip(),
        "meta_title": str(row.get("meta_title") or "").strip(),
        "meta_description": str(row.get("meta_description") or "").strip(),
        "blog_intro": str(row.get("blog_intro") or "").strip(),
        "subtitle": str(row.get("custom_subtitle") or "").strip(),
        "cover_credit": str(row.get("custom_cover_credit") or "").strip(),
        "cta_label": str(row.get("custom_cta_label") or "").strip(),
        "cta_link": str(row.get("custom_cta_link") or "").strip(),
        "focus_keyword": str(row.get("custom_focus_keyword") or "").strip(),
        "secondary_keywords": str(row.get("custom_secondary_keywords") or "").strip(),
        "read_time": str(row.get("custom_read_time") or row.get("read_time") or _estimate_read_time(row)).strip(),
        "status_key": status_key,
        "status_label": status_label,
        "excerpt": excerpt,
        "word_count": word_count,
        "modified": row.get("modified"),
    }
    if include_body:
        payload["body_html"] = body_html
    return payload


def _management_blog_fields_for_query():
    available_fields = _management_blog_available_fields()
    wanted = [
        "name",
        "title",
        "blog_category",
        "blogger",
        "route",
        "published",
        "published_on",
        "featured",
        "disable_comments",
        "disable_likes",
        "hide_cta",
        "meta_image",
        "meta_title",
        "meta_description",
        "blog_intro",
        "custom_subtitle",
        "custom_cover_credit",
        "custom_cta_label",
        "custom_cta_link",
        "custom_focus_keyword",
        "custom_secondary_keywords",
        "custom_read_time",
        "read_time",
        "custom_article_body",
        "content",
        "content_md",
        "content_html",
        "modified",
    ]
    fields = [field for field in wanted if field == "name" or field in available_fields]
    return fields, available_fields


@frappe.whitelist()
def get_management_blog_posts(search=None, status="all", category=None, limit=60, offset=0):
    _require_management_access("content.edit")
    if not frappe.db.exists("DocType", "Blog Post"):
        return {"items": [], "total": 0, "limit": 0, "offset": 0, "categories": []}

    fields, available_fields = _management_blog_fields_for_query()

    limit = min(max(cint(limit or 60), 1), 300)
    offset = max(cint(offset or 0), 0)
    status = str(status or "all").strip().lower()
    category = str(category or "").strip()
    search_term = str(search or "").strip()

    filters = {}
    if status == "published" and "published" in available_fields:
        filters["published"] = 1
    elif status == "draft" and "published" in available_fields:
        filters["published"] = 0
    elif status == "featured" and "featured" in available_fields:
        filters["featured"] = 1

    if category and category != "all" and "blog_category" in available_fields:
        filters["blog_category"] = category

    or_filters = None
    if search_term:
        like_query = f"%{search_term}%"
        or_filters = {"title": ["like", like_query]}
        if "route" in available_fields:
            or_filters["route"] = ["like", like_query]
        if "blog_intro" in available_fields:
            or_filters["blog_intro"] = ["like", like_query]
        if "meta_description" in available_fields:
            or_filters["meta_description"] = ["like", like_query]
        if "custom_article_body" in available_fields:
            or_filters["custom_article_body"] = ["like", like_query]

    total_rows = frappe.get_all(
        "Blog Post",
        filters=filters,
        or_filters=or_filters,
        fields=["name"],
        order_by="modified desc",
        limit_page_length=0,
    )
    total = len(total_rows or [])

    rows = frappe.get_all(
        "Blog Post",
        fields=fields,
        filters=filters,
        or_filters=or_filters,
        order_by="modified desc",
        start=offset,
        limit_page_length=limit,
    )

    return {
        "items": [_serialize_management_blog_row(row, include_body=False) for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "categories": _list_management_blog_categories(available_fields),
    }


@frappe.whitelist()
def get_management_blog_post_detail(name=None):
    _require_management_access("content.edit")
    if not frappe.db.exists("DocType", "Blog Post"):
        return {"post": None}

    post_name = str(name or frappe.form_dict.get("name") or "").strip()
    if not post_name:
        return {"post": None}

    fields, _ = _management_blog_fields_for_query()
    rows = frappe.get_all(
        "Blog Post",
        fields=fields,
        filters={"name": post_name},
        limit_page_length=1,
    )
    if not rows:
        return {"post": None}
    return {"post": _serialize_management_blog_row(rows[0], include_body=True)}


@frappe.whitelist()
def save_management_blog_post(name=None, payload=None):
    _require_management_access("content.edit")
    payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(payload)

    if not frappe.db.exists("DocType", "Blog Post"):
        frappe.throw("DocType بلاگ در سیستم موجود نیست.")

    ensure_blog_custom_fields()
    fields, available_fields = _management_blog_fields_for_query()
    post_name = str(name or payload.get("name") or "").strip()
    title = str(payload.get("title") or "").strip()
    if not title:
        frappe.throw("عنوان بلاگ اجباری است.")

    if not workflow_bypass and should_enforce("content"):
        return _workflow_create_response(
            module_key="content",
            target_type="blog_post",
            target_key=post_name or title,
            payload=payload,
            current_snapshot={"name": post_name} if post_name else {},
            source_endpoint="save_management_blog_post",
        )

    is_new = not post_name
    if is_new:
        doc = frappe.new_doc("Blog Post")
    else:
        if not frappe.db.exists("Blog Post", post_name):
            frappe.throw("مقاله انتخاب‌شده پیدا نشد.")
        doc = frappe.get_doc("Blog Post", post_name)

    doc.title = title

    if "blog_category" in available_fields:
        selected_category = str(payload.get("blog_category") or "").strip()
        if not selected_category:
            categories = _list_management_blog_categories(available_fields)
            selected_category = categories[0] if categories else ""
        if selected_category:
            doc.blog_category = selected_category

    if "blogger" in available_fields:
        selected_blogger = str(payload.get("blogger") or "").strip() or _default_blogger_for_user(available_fields)
        if selected_blogger:
            doc.blogger = selected_blogger

    if "route" in available_fields:
        doc.route = _normalize_management_blog_route(payload.get("route"), title, post_name=doc.name if not is_new else None)

    for bool_field in ["featured", "disable_comments", "disable_likes", "hide_cta", "enable_email_notification"]:
        if bool_field in available_fields and bool_field in payload:
            setattr(doc, bool_field, 1 if _to_bool(payload.get(bool_field), False) else 0)

    publish_requested = _to_bool(payload.get("published"), bool(cint(getattr(doc, "published", 0))))
    if "published" in available_fields:
        doc.published = 1 if publish_requested else 0
    if "published_on" in available_fields:
        selected_published_on = payload.get("published_on")
        if publish_requested:
            doc.published_on = selected_published_on or getattr(doc, "published_on", None) or nowdate()
        elif selected_published_on:
            doc.published_on = selected_published_on

    for text_field in [
        "blog_intro",
        "meta_title",
        "meta_description",
        "meta_image",
        "custom_subtitle",
        "custom_cover_credit",
        "custom_cta_label",
        "custom_cta_link",
        "custom_focus_keyword",
        "custom_secondary_keywords",
        "custom_read_time",
    ]:
        if text_field in available_fields and text_field in payload:
            setattr(doc, text_field, str(payload.get(text_field) or "").strip())

    body_html = payload.get("body_html")
    if body_html is None:
        body_html = payload.get("content_html")
    normalized_body = str(body_html or "").strip()
    if "custom_article_body" in available_fields:
        doc.custom_article_body = normalized_body
    elif "content_html" in available_fields:
        doc.content_html = normalized_body
    elif "content" in available_fields:
        doc.content = normalized_body

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    rows = frappe.get_all("Blog Post", fields=fields, filters={"name": doc.name}, limit_page_length=1)
    if not rows:
        _workflow_shadow_record(
            module_key="content",
            target_type="blog_post",
            target_key=doc.name,
            payload=payload,
            source_endpoint="save_management_blog_post",
            publish_result={"name": doc.name, "title": title},
        )
        return {"ok": True, "post": {"name": doc.name, "title": title}}
    response = {"ok": True, "post": _serialize_management_blog_row(rows[0], include_body=True)}
    _workflow_shadow_record(
        module_key="content",
        target_type="blog_post",
        target_key=doc.name,
        payload=payload,
        source_endpoint="save_management_blog_post",
        publish_result=response,
    )
    return response


@frappe.whitelist()
def delete_management_blog_post(name=None, payload=None):
    _require_management_access("content.edit")
    post_name = str(name or frappe.form_dict.get("name") or "").strip()
    if not post_name:
        frappe.throw("نام مقاله ارسال نشده است.")

    payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(payload)
    if not workflow_bypass and should_enforce("content"):
        return _workflow_create_response(
            module_key="content",
            target_type="blog_delete",
            target_key=post_name,
            payload={"name": post_name},
            current_snapshot={"exists": bool(frappe.db.exists("Blog Post", post_name))},
            source_endpoint="delete_management_blog_post",
        )

    if not frappe.db.exists("Blog Post", post_name):
        return {"ok": True}
    frappe.delete_doc("Blog Post", post_name, ignore_permissions=True, force=1)
    frappe.db.commit()
    _workflow_shadow_record(
        module_key="content",
        target_type="blog_delete",
        target_key=post_name,
        payload={"name": post_name},
        source_endpoint="delete_management_blog_post",
        publish_result={"ok": True},
    )
    return {"ok": True}


@frappe.whitelist()
def ensure_blog_custom_fields():
    custom_fields = {
        "Blog Post": [
            {
                "fieldname": "custom_editor_guide",
                "label": "راهنمای ویرایش",
                "fieldtype": "HTML",
                "insert_after": "title",
            },
            {
                "fieldname": "custom_component_palette",
                "label": "پالت کامپوننت‌ها",
                "fieldtype": "HTML",
                "insert_after": "custom_editor_guide",
            },
            {
                "fieldname": "custom_read_time",
                "label": "زمان مطالعه",
                "fieldtype": "Data",
                "insert_after": "custom_component_palette",
            },
            {
                "fieldname": "custom_subtitle",
                "label": "زیرتیتر بلاگ",
                "fieldtype": "Data",
                "insert_after": "custom_read_time",
            },
            {
                "fieldname": "custom_article_body",
                "label": "محتوای کامل بلاگ",
                "fieldtype": "Text Editor",
                "insert_after": "blog_intro",
                "description": "اگر این فیلد پر شود، متن اصلی صفحه بلاگ از همین فیلد نمایش داده می‌شود.",
            },
            {
                "fieldname": "custom_cover_credit",
                "label": "اعتبار عکس کاور",
                "fieldtype": "Data",
                "insert_after": "meta_image",
            },
            {
                "fieldname": "custom_cta_label",
                "label": "متن دکمه CTA",
                "fieldtype": "Data",
                "insert_after": "custom_subtitle",
            },
            {
                "fieldname": "custom_cta_link",
                "label": "لینک دکمه CTA",
                "fieldtype": "Data",
                "insert_after": "custom_cta_label",
            },
            {
                "fieldname": "custom_related_products_section",
                "label": "محصولات مرتبط با مقاله",
                "fieldtype": "Section Break",
                "insert_after": "custom_cta_link",
            },
            {
                "fieldname": "custom_related_products",
                "label": "محصولات مرتبط",
                "fieldtype": "Table",
                "options": "Blog Post Product",
                "insert_after": "custom_related_products_section",
            },
            {
                "fieldname": "custom_live_preview",
                "label": "پیش‌نمایش زنده",
                "fieldtype": "HTML",
                "insert_after": "custom_related_products",
            },
        ]
    }
    create_custom_fields(custom_fields)
    return {"status": "ok"}


def _management_roles(user=None):
    return set(permission_context(user=user).roles)


def _has_management_access(user=None):
    return can_access_management_permission(user=user)


def _require_management_access(capability="management.access", message=None):
    default_message = "شما دسترسی لازم برای مشاهده پنل مدیریت را ندارید."
    try:
        require_capability(capability, message=message or default_message)
    except Exception:
        audit_log_event(
            module_key="system",
            action_key="permission.denied",
            target_type="capability",
            target_key=str(capability or "management.access"),
            result="denied",
            details={"message": message or default_message},
        )
        raise


def _module_action_capability(module_key, action="edit"):
    module = str(module_key or "").strip().lower()
    action_key = str(action or "edit").strip().lower()
    mapping = {
        ("content", "edit"): "content.edit",
        ("content", "review"): "content.review",
        ("content", "publish"): "content.publish",
        ("product", "edit"): "product.edit",
        ("product", "review"): "product.review",
        ("product", "publish"): "product.publish",
        ("support", "edit"): "support.manage",
        ("support", "review"): "support.manage",
        ("support", "publish"): "support.manage",
        ("analytics", "edit"): "analytics.manage",
        ("analytics", "review"): "analytics.manage",
        ("analytics", "publish"): "analytics.manage",
        ("system", "edit"): "management.access",
        ("system", "review"): "management.access",
        ("system", "publish"): "management.access",
    }
    return mapping.get((module, action_key), "management.access")


def _audit_allowed_modules():
    if is_super_admin() or has_capability("audit.view"):
        return None

    allowed = set()
    if has_capability("content.edit") or has_capability("content.review") or has_capability("content.publish"):
        allowed.add("content")
    if has_capability("product.edit") or has_capability("product.review") or has_capability("product.publish"):
        allowed.add("product")
    if has_capability("support.manage"):
        allowed.add("support")
    if has_capability("analytics.view") or has_capability("analytics.manage"):
        allowed.add("analytics")
    return allowed


def _workflow_bypass_enabled(payload=None):
    if isinstance(payload, dict):
        return _to_bool(payload.get("__workflow_bypass") or payload.get("workflow_bypass"), False)
    return False


def _workflow_create_response(
    *,
    module_key,
    target_type,
    target_key,
    payload,
    current_snapshot=None,
    diff_summary=None,
    source_endpoint="",
):
    request_info = create_change_request(
        module_key=module_key,
        target_type=target_type,
        target_key=target_key,
        request_payload=payload,
        current_snapshot=current_snapshot,
        diff_summary=diff_summary,
        source_endpoint=source_endpoint,
        initial_state="Draft",
        is_shadow_record=False,
    )
    audit_log_event(
        module_key=module_key,
        action_key="workflow.create_request",
        target_type=target_type,
        target_key=str(target_key or ""),
        change_request=request_info.get("name") or "",
        result="success",
        details={
            "source_endpoint": source_endpoint,
            "state": request_info.get("state"),
        },
    )
    return {
        "ok": True,
        "workflow_enforced": True,
        "change_request": request_info.get("name") or "",
        "state": request_info.get("state") or "Draft",
    }


def _workflow_shadow_record(
    *,
    module_key,
    target_type,
    target_key,
    payload,
    current_snapshot=None,
    diff_summary=None,
    source_endpoint="",
    publish_result=None,
):
    if _workflow_bypass_enabled(payload):
        return
    shadow = shadow_create_if_enabled(
        module_key=module_key,
        target_type=target_type,
        target_key=target_key,
        request_payload=payload,
        current_snapshot=current_snapshot,
        diff_summary=diff_summary,
        source_endpoint=source_endpoint,
        publish_result=publish_result or {},
    )
    audit_log_event(
        module_key=module_key,
        action_key=f"{module_key}.write",
        target_type=target_type,
        target_key=str(target_key or ""),
        change_request=shadow.get("name") or "",
        result="success",
        details={
            "source_endpoint": source_endpoint,
            "shadow_recorded": bool(shadow.get("name")),
        },
    )
    if shadow.get("name"):
        audit_log_event(
            module_key=module_key,
            action_key="workflow.shadow_record",
            target_type=target_type,
            target_key=str(target_key or ""),
            change_request=shadow.get("name") or "",
            result="success",
            details={"source_endpoint": source_endpoint},
        )


def _relative_path(path_obj, root_path):
    try:
        return path_obj.relative_to(root_path).as_posix()
    except Exception:
        return str(path_obj)


def _modified_at(path_obj):
    try:
        return datetime.fromtimestamp(path_obj.stat().st_mtime).isoformat(timespec="seconds")
    except Exception:
        return ""


def _scan_vue_files(directory, app_root):
    if not directory.exists():
        return []

    rows = []
    for vue_file in sorted(directory.rglob("*.vue")):
        rows.append(
            {
                "name": vue_file.stem,
                "file": _relative_path(vue_file, app_root),
                "modified_at": _modified_at(vue_file),
            }
        )
    return rows


def _extract_frontend_routes(app_vue_file, app_root):
    if not app_vue_file.exists():
        return []

    try:
        source = app_vue_file.read_text(encoding="utf-8")
    except Exception:
        return []

    import_map = {}
    for match in re.finditer(r"import\s+([A-Za-z0-9_]+)\s+from\s+'\.\/pages\/([^']+\.vue)'", source):
        import_map[match.group(1)] = f"frontend/src/pages/{match.group(2)}"

    route_rows = []
    for match in re.finditer(r"<([A-Za-z0-9_]+)\s+v(?:-else)?-if=\"page === '([^']+)'\"", source):
        component_name = match.group(1)
        page_key = match.group(2)
        route_rows.append(
            {
                "page_key": page_key,
                "component": component_name,
                "file": import_map.get(component_name, ""),
                "route_guess": "/mysite" if page_key == "home" else f"/{page_key}",
            }
        )

    fallback_match = re.search(r"<([A-Za-z0-9_]+)\s+v-else\s*/>", source)
    if fallback_match:
        component_name = fallback_match.group(1)
        route_rows.append(
            {
                "page_key": "fallback",
                "component": component_name,
                "file": import_map.get(component_name, ""),
                "route_guess": "default-route-fallback",
            }
        )

    return route_rows


def _scan_website_pages(app_root):
    website_dir = Path(app_root) / "mysite" / "www" / "mysite"
    if not website_dir.exists():
        return []

    rows = []
    for html_file in sorted(website_dir.glob("*.html")):
        stem = html_file.stem
        if stem in {"index", "home"}:
            route = "/mysite"
        else:
            route = f"/{stem}"

        py_exact = website_dir / f"{stem}.py"
        py_slug = website_dir / f"{stem.replace('-', '_')}.py"
        py_file = py_exact if py_exact.exists() else py_slug

        title = ""
        meta_description = ""
        canonical_url = ""
        meta_image = ""
        robots = ""
        try:
            html_text = html_file.read_text(encoding="utf-8")
            title_match = re.search(r"<title>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
            if title_match:
                title = html_unescape(title_match.group(1).strip())

            desc_match = re.search(
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
                html_text,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if desc_match:
                meta_description = html_unescape(strip_html(desc_match.group(1)).strip())

            canonical_match = re.search(
                r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']',
                html_text,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if canonical_match:
                canonical_url = html_unescape(canonical_match.group(1).strip())

            og_image_match = re.search(
                r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']',
                html_text,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if og_image_match:
                meta_image = html_unescape(og_image_match.group(1).strip())

            robots_match = re.search(
                r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'](.*?)["\']',
                html_text,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if robots_match:
                robots = robots_match.group(1).strip().lower()
        except Exception:
            title = ""
            meta_description = ""
            canonical_url = ""
            meta_image = ""
            robots = ""

        rows.append(
            {
                "name": stem,
                "route": route,
                "title": title,
                "meta_description": meta_description,
                "canonical_url": canonical_url,
                "meta_image": meta_image,
                "robots": robots,
                "noindex": "noindex" in robots,
                "html_file": _relative_path(html_file, app_root),
                "py_file": _relative_path(py_file, app_root) if py_file.exists() else "",
                "modified_at": _modified_at(html_file),
            }
        )
    return rows


def _scan_whitelisted_methods(app_root):
    scan_root = Path(app_root) / "mysite"
    if not scan_root.exists():
        return []

    methods = []
    for py_file in sorted(scan_root.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        try:
            lines = py_file.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue

        pending_whitelist = ""
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("@frappe.whitelist"):
                pending_whitelist = stripped
                continue

            def_match = re.match(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", stripped)
            if def_match and pending_whitelist:
                func_name = def_match.group(1)
                module_name = _relative_path(py_file, app_root).replace("/", ".").replace(".py", "")
                methods.append(
                    {
                        "method": f"{module_name}.{func_name}",
                        "allow_guest": "allow_guest=True" in pending_whitelist.replace(" ", ""),
                        "file": _relative_path(py_file, app_root),
                    }
                )
                pending_whitelist = ""
            elif stripped and not stripped.startswith("@"):
                pending_whitelist = ""

    return methods


def _collect_management_counts():
    targets = [
        ("items", "Item"),
        ("customers", "Customer"),
        ("quotation_requests", "Quotation Request"),
        ("quotations", "Quotation"),
        ("sales_orders", "Sales Order"),
        ("sales_invoices", "Sales Invoice"),
        ("blog_posts", "Blog Post"),
        ("projects", "Customer Project"),
    ]
    result = {}
    for key, doctype in targets:
        if frappe.db.exists("DocType", doctype):
            result[key] = frappe.db.count(doctype)
        else:
            result[key] = 0
    return result


def _normalize_tracked_path(raw_url):
    value = str(raw_url or "").strip()
    if not value:
        return ""
    try:
        parsed = urlsplit(value)
        path = parsed.path or value
    except Exception:
        path = value
    if not path.startswith("/"):
        path = f"/{path.lstrip('/')}"
    path = re.sub(r"/{2,}", "/", path)
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return path


def _to_bool(value, default=False):
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off", ""}:
        return False
    return bool(default)


def _normalize_content_text(value):
    text = html_unescape(str(value or ""))
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_meaningful_content_text(text):
    value = _normalize_content_text(text)
    if len(value) < 3:
        return False
    if "{{" in value or "}}" in value or "{%" in value or "%}" in value:
        return False
    if re.fullmatch(r"[-–—_=+*/|\\:;,.!?()\[\]{}0-9٪%<>#@]+", value):
        return False
    return bool(re.search(r"[A-Za-z\u0600-\u06FF]", value))


def _extract_static_text_candidates_from_markup(markup, limit=350):
    source = str(markup or "")
    source = re.sub(r"<!--[\s\S]*?-->", " ", source)
    source = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", source, flags=re.IGNORECASE)

    candidates = []
    seen = set()

    attr_pattern = re.compile(r"""(?<![:@])(?:placeholder|title|alt|aria-label)\s*=\s*(?:"([^"]+)"|'([^']+)')""", re.IGNORECASE)
    for match in attr_pattern.finditer(source):
        raw = match.group(1) if match.group(1) is not None else match.group(2)
        text = _normalize_content_text(raw)
        if not _is_meaningful_content_text(text):
            continue
        if text in seen:
            continue
        seen.add(text)
        candidates.append(text)
        if len(candidates) >= limit:
            return candidates

    text_pattern = re.compile(r">([^<>]+)<")
    for match in text_pattern.finditer(source):
        raw = match.group(1)
        text = _normalize_content_text(raw)
        if not _is_meaningful_content_text(text):
            continue
        if text in seen:
            continue
        seen.add(text)
        candidates.append(text)
        if len(candidates) >= limit:
            break
    return candidates


def _extract_vue_template_markup(vue_source):
    source = str(vue_source or "")
    match = re.search(r"<template(?:\s[^>]*)?>([\s\S]*?)</template>", source, flags=re.IGNORECASE)
    return match.group(1) if match else source


def _scan_content_candidates_from_vue_file(file_path, app_root, scope="page"):
    if not file_path or not Path(file_path).exists():
        return []
    try:
        source = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return []

    template_markup = _extract_vue_template_markup(source)
    texts = _extract_static_text_candidates_from_markup(template_markup)
    if not texts:
        return []

    rel_file = _relative_path(Path(file_path), Path(app_root))
    scope_label = {"page": "صفحه", "component": "کامپوننت", "template": "قالب"}.get(scope, "متن")

    rows = []
    seen_keys = set()
    for index, text in enumerate(texts, start=1):
        key_seed = f"{scope}|{rel_file}|{text}"
        key = hashlib.md5(key_seed.encode("utf-8")).hexdigest()[:16]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        rows.append(
            {
                "key": key,
                "scope": scope,
                "scope_label": scope_label,
                "source_file": rel_file,
                "source_text": text,
                "replacement_text": "",
                "position": index,
            }
        )
    return rows


def _scan_content_candidates_from_html_file(file_path, app_root):
    if not file_path or not Path(file_path).exists():
        return []
    try:
        source = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return []
    texts = _extract_static_text_candidates_from_markup(source, limit=220)
    if not texts:
        return []

    rel_file = _relative_path(Path(file_path), Path(app_root))
    rows = []
    seen_keys = set()
    for index, text in enumerate(texts, start=1):
        key_seed = f"template|{rel_file}|{text}"
        key = hashlib.md5(key_seed.encode("utf-8")).hexdigest()[:16]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        rows.append(
            {
                "key": key,
                "scope": "template",
                "scope_label": "قالب",
                "source_file": rel_file,
                "source_text": text,
                "replacement_text": "",
                "position": index,
            }
        )
    return rows


def _extract_local_vue_component_files(vue_path, app_root, max_files=30):
    if not vue_path or not Path(vue_path).exists():
        return []
    try:
        source = Path(vue_path).read_text(encoding="utf-8")
    except Exception:
        return []

    app_root_path = Path(app_root).resolve()
    frontend_src = (app_root_path / "frontend" / "src").resolve()
    files = []
    seen = set()

    for match in re.finditer(r"""from\s+['"]([^'"]+\.vue)['"]""", source):
        raw_path = str(match.group(1) or "").strip()
        if not raw_path:
            continue

        resolved = None
        if raw_path.startswith("."):
            resolved = (Path(vue_path).parent / raw_path).resolve()
        elif raw_path.startswith("@/"):
            resolved = (frontend_src / raw_path[2:]).resolve()

        if not resolved or not resolved.exists():
            continue
        try:
            resolved.relative_to(app_root_path)
        except Exception:
            continue

        rel = resolved.as_posix()
        if "/frontend/src/components/" not in rel:
            continue
        if rel in seen:
            continue
        seen.add(rel)
        files.append(resolved)
        if len(files) >= max_files:
            break

    return files


def _resolve_route_frontend_file(route, app_root):
    frontend_root = Path(app_root) / "frontend" / "src"
    app_vue_file = frontend_root / "App.vue"
    if not app_vue_file.exists():
        return None

    for row in _extract_frontend_routes(app_vue_file, app_root):
        route_guess = row.get("route_guess")
        if route_guess == "default-route-fallback":
            continue
        normalized = _normalize_tracked_path(route_guess)
        if normalized != route:
            continue
        rel = str(row.get("file") or "").strip()
        if not rel:
            continue
        path = (Path(app_root) / rel).resolve()
        if path.exists():
            return path
    return None


def _resolve_route_website_html_file(route, app_root):
    website_pages = _scan_website_pages(app_root)
    website_map = {row.get("route"): row for row in website_pages if row.get("route")}
    row = website_map.get(route) or {}
    rel = str(row.get("html_file") or "").strip()
    if not rel:
        return None
    path = (Path(app_root) / rel).resolve()
    return path if path.exists() else None


def _scan_route_content_catalog(route, app_root):
    route = _normalize_tracked_path(route)
    if not route:
        return {"route": "", "items": [], "sources": []}

    items = []
    sources = []
    seen = set()

    def append_rows(rows):
        for row in rows or []:
            key = str(row.get("key") or "").strip()
            if not key or key in seen:
                continue
            seen.add(key)
            items.append(row)

    page_vue_path = _resolve_route_frontend_file(route, app_root)
    if page_vue_path:
        page_rows = _scan_content_candidates_from_vue_file(page_vue_path, app_root, scope="page")
        append_rows(page_rows)
        sources.append(
            {
                "scope": "page",
                "scope_label": "صفحه",
                "file": _relative_path(page_vue_path, Path(app_root)),
                "count": len(page_rows),
            }
        )

        for component_file in _extract_local_vue_component_files(page_vue_path, app_root):
            component_rows = _scan_content_candidates_from_vue_file(component_file, app_root, scope="component")
            append_rows(component_rows)
            sources.append(
                {
                    "scope": "component",
                    "scope_label": "کامپوننت",
                    "file": _relative_path(component_file, Path(app_root)),
                    "count": len(component_rows),
                }
            )

    html_path = _resolve_route_website_html_file(route, app_root)
    if html_path:
        html_rows = _scan_content_candidates_from_html_file(html_path, app_root)
        append_rows(html_rows)
        sources.append(
            {
                "scope": "template",
                "scope_label": "قالب",
                "file": _relative_path(html_path, Path(app_root)),
                "count": len(html_rows),
            }
        )

    items = items[:1200]
    return {"route": route, "items": items, "sources": sources}


def _clean_content_override_rows(rows):
    payload = rows
    if isinstance(payload, str):
        try:
            payload = frappe.parse_json(payload)
        except Exception:
            payload = json.loads(payload or "[]")

    if isinstance(payload, dict):
        payload = payload.get("items") or payload.get("content_overrides") or []
    if not isinstance(payload, (list, tuple)):
        return []

    result = []
    seen = set()
    for row in payload:
        if not isinstance(row, dict):
            continue
        source_text = _normalize_content_text(row.get("source_text") or row.get("source"))
        if not _is_meaningful_content_text(source_text):
            continue
        replacement_text = _normalize_content_text(row.get("replacement_text") or row.get("target"))
        scope = str(row.get("scope") or "").strip() or "page"
        source_file = str(row.get("source_file") or "").strip()

        key = str(row.get("key") or "").strip()
        if not key:
            key_seed = f"{scope}|{source_file}|{source_text}"
            key = hashlib.md5(key_seed.encode("utf-8")).hexdigest()[:16]

        if key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "key": key,
                "scope": scope,
                "scope_label": str(row.get("scope_label") or "").strip(),
                "source_file": source_file,
                "source_text": source_text,
                "replacement_text": replacement_text,
                "enabled": _to_bool(row.get("enabled"), bool(replacement_text and replacement_text != source_text)),
            }
        )
        if len(result) >= 1200:
            break
    return result


_VISUAL_ALLOWED_STYLE_KEYS = {
    "color",
    "backgroundColor",
    "fontSize",
    "fontWeight",
    "lineHeight",
    "letterSpacing",
    "textAlign",
    "fontFamily",
    "fontFeatureSettings",
    "fontVariantLigatures",
    "textIndent",
    "listStyleType",
    "listStylePosition",
    "whiteSpace",
    "wordSpacing",
    "textTransform",
    "textDecoration",
    "borderRadius",
    "borderColor",
    "borderWidth",
    "padding",
    "margin",
    "width",
    "minWidth",
    "height",
    "maxHeight",
    "maxWidth",
    "minHeight",
    "display",
    "flexDirection",
    "flexWrap",
    "flexGrow",
    "flexShrink",
    "justifyContent",
    "alignItems",
    "gap",
    "gridTemplateColumns",
    "border",
    "boxShadow",
    "opacity",
    "zIndex",
    "overflowX",
    "overflowY",
    "transitionDuration",
    "position",
    "top",
    "right",
    "bottom",
    "left",
}
_VISUAL_TRANSIENT_SELECTOR_CLASS_PATTERN = re.compile(r"\.mysite-visual-(?:selected|hover|layer-highlight)\b")
_VISUAL_MAX_HTML_CONTENT_LEN = 50000


def _normalize_visual_selector(selector):
    value = str(selector or "").strip()
    if not value:
        return ""
    value = _VISUAL_TRANSIENT_SELECTOR_CLASS_PATTERN.sub("", value)
    value = re.sub(r"\s*([>+~])\s*", r" \1 ", value)
    value = re.sub(r"\s+", " ", value).strip().strip(",")
    value = value.rstrip(".>+~ ").strip()
    if not value:
        return ""
    if "mysite-visual-" in value:
        return ""
    return value


def _clean_visual_override_rows(rows):
    payload = rows
    if isinstance(payload, str):
        try:
            payload = frappe.parse_json(payload)
        except Exception:
            payload = json.loads(payload or "[]")

    if isinstance(payload, dict):
        payload = payload.get("items") or payload.get("visual_overrides") or []
    if not isinstance(payload, (list, tuple)):
        return []

    result = []
    seen = set()

    def _clean_visual_html_content(content):
        text = str(content or "")
        if not text:
            return ""
        text = text[:_VISUAL_MAX_HTML_CONTENT_LEN]
        text = re.sub(r"<\s*(script|iframe|object|embed|meta|link|base)\b[^>]*>[\s\S]*?<\s*/\s*\1\s*>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*(script|iframe|object|embed|meta|link|base)\b[^>]*\/?>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"""\s+on[a-z0-9_-]+\s*=\s*(".*?"|'.*?'|[^\s>]+)""", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"""(href|src)\s*=\s*(['"])\s*javascript:[\s\S]*?\2""", r"\1=\2\2", text, flags=re.IGNORECASE)
        text = re.sub(r"""\s+(contenteditable|data-mysite-inline-text)\s*=\s*(".*?"|'.*?'|[^\s>]+)""", "", text, flags=re.IGNORECASE | re.DOTALL)
        return text.strip()

    for row in payload:
        if not isinstance(row, dict):
            continue

        selector = _normalize_visual_selector(row.get("selector") or "")
        if not selector or len(selector) > 420:
            continue
        if selector in seen:
            continue

        styles = {}
        raw_styles = row.get("styles")
        if isinstance(raw_styles, dict):
            for raw_key, raw_value in raw_styles.items():
                key = str(raw_key or "").strip()
                value = str(raw_value or "").strip()
                if not key or key not in _VISUAL_ALLOWED_STYLE_KEYS:
                    continue
                if not value or len(value) > 120:
                    continue
                styles[key] = value

        text_content = str(row.get("text_content") or "")
        apply_text = _to_bool(row.get("apply_text"), False)
        html_content = _clean_visual_html_content(
            row.get("html_content") or row.get("rich_text_html") or row.get("html")
        )
        apply_html = _to_bool(row.get("apply_html"), False) and bool(html_content)
        selector_lower = selector.lower()
        is_root_selector = selector_lower in {"body", "html", "#app", ":root"} or bool(
            re.match(r"^(body|html|#app)\b", selector_lower)
        )
        if is_root_selector and (apply_text or apply_html):
            continue
        enabled = _to_bool(row.get("enabled"), True)
        if not enabled:
            continue
        if not styles and not apply_text and not apply_html:
            continue

        seen.add(selector)
        result.append(
            {
                "selector": selector,
                "tag": str(row.get("tag") or "").strip(),
                "label": str(row.get("label") or "").strip(),
                "styles": styles,
                "apply_text": apply_text,
                "text_content": text_content if apply_text else "",
                "apply_html": apply_html,
                "html_content": html_content if apply_html else "",
            }
        )
        if len(result) >= 1200:
            break
    return result


_VISUAL_MANAGED_CSS_START = "/* MYSITE-MANAGEMENT-VISUAL-STYLES:START */"
_VISUAL_MANAGED_CSS_END = "/* MYSITE-MANAGEMENT-VISUAL-STYLES:END */"


def _management_visual_editor_history_path():
    return Path(frappe.get_site_path("private", "mysite_management_visual_editor_history.json"))


def _load_management_visual_editor_history():
    path = _management_visual_editor_history_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _save_management_visual_editor_history(payload):
    path = _management_visual_editor_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {}, ensure_ascii=False, indent=2), encoding="utf-8")


def _camel_to_kebab(name):
    text = str(name or "").strip()
    if not text:
        return ""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
    text = text.replace("_", "-")
    return text.lower()


def _visual_rows_to_css(rows):
    lines = []
    for row in rows or []:
        selector = str(row.get("selector") or "").strip()
        if not selector:
            continue
        styles = row.get("styles") if isinstance(row.get("styles"), dict) else {}
        declarations = []
        for raw_key, raw_value in styles.items():
            key = _camel_to_kebab(raw_key)
            value = str(raw_value or "").strip()
            if not key or not value:
                continue
            declarations.append(f"  {key}: {value};")
        if not declarations:
            continue
        lines.append(f"{selector} {{")
        lines.extend(declarations)
        lines.append("}")
        lines.append("")
    return "\n".join(lines).strip()


def _extract_first_style_block(source):
    source_text = str(source or "")
    match = re.search(r"<style\b[^>]*>([\s\S]*?)</style>", source_text, flags=re.IGNORECASE)
    if not match:
        return ""
    return str(match.group(1) or "").strip()


def _extract_managed_visual_css(source):
    source_text = str(source or "")
    pattern = re.compile(
        re.escape(_VISUAL_MANAGED_CSS_START) + r"([\s\S]*?)" + re.escape(_VISUAL_MANAGED_CSS_END),
        flags=re.IGNORECASE,
    )
    match = pattern.search(source_text)
    if not match:
        return ""
    return str(match.group(1) or "").strip()


def _replace_first_style_block(source, style_content):
    source_text = str(source or "")
    new_content = str(style_content or "").strip()
    pattern = re.compile(r"(<style\b[^>]*>)([\s\S]*?)(</style>)", flags=re.IGNORECASE)
    if pattern.search(source_text):
        return pattern.sub(rf"\1\n{new_content}\n\3", source_text, count=1)
    return f"{source_text}\n\n<style scoped>\n{new_content}\n</style>\n"


def _upsert_managed_visual_css(source, css_content):
    source_text = str(source or "")
    css_text = str(css_content or "").strip()
    managed_block = f"{_VISUAL_MANAGED_CSS_START}\n{css_text}\n{_VISUAL_MANAGED_CSS_END}"

    pattern = re.compile(
        re.escape(_VISUAL_MANAGED_CSS_START) + r"[\s\S]*?" + re.escape(_VISUAL_MANAGED_CSS_END),
        flags=re.IGNORECASE,
    )
    if pattern.search(source_text):
        return pattern.sub(managed_block, source_text, count=1)

    style_match = re.search(r"<style\b[^>]*>", source_text, flags=re.IGNORECASE)
    if style_match:
        close_match = re.search(r"</style>", source_text[style_match.end():], flags=re.IGNORECASE)
        if close_match:
            close_index = style_match.end() + close_match.start()
            before = source_text[:close_index]
            after = source_text[close_index:]
            insert = f"\n\n{managed_block}\n"
            return f"{before}{insert}{after}"

    return f"{source_text}\n\n<style scoped>\n{managed_block}\n</style>\n"


def _backup_visual_editor_version(route, file_rel_path, current_source, note=""):
    history = _load_management_visual_editor_history()
    route_key = _normalize_tracked_path(route)
    if not route_key:
        return {}

    route_payload = history.get(route_key) if isinstance(history.get(route_key), dict) else {}
    versions = route_payload.get("versions") if isinstance(route_payload.get("versions"), list) else []
    version_id = frappe.generate_hash(length=12)
    versions.append(
        {
            "id": version_id,
            "saved_at": now_datetime().isoformat(),
            "saved_by": frappe.session.user,
            "note": str(note or "").strip(),
            "file": str(file_rel_path or "").strip(),
            "sha1": hashlib.sha1(str(current_source or "").encode("utf-8")).hexdigest(),
            "content": str(current_source or ""),
        }
    )
    versions = versions[-60:]
    history[route_key] = {
        "route": route_key,
        "file": str(file_rel_path or "").strip(),
        "versions": versions,
    }
    _save_management_visual_editor_history(history)
    return versions[-1]


def _resolve_visual_editor_file_candidate(spec, base_path, app_root):
    spec_text = str(spec or "").strip()
    if not spec_text:
        return None
    app_root_resolved = app_root.resolve()

    if spec_text.startswith("."):
        candidate = (base_path.parent / spec_text).resolve()
    elif spec_text.startswith("@/"):
        candidate = (app_root / "frontend" / "src" / spec_text[2:]).resolve()
    else:
        return None

    try:
        candidate.relative_to(app_root_resolved)
    except Exception:
        return None

    candidates = []
    if candidate.suffix:
        candidates.append(candidate)
    else:
        candidates.extend(
            [
                candidate.with_suffix(".vue"),
                candidate.with_suffix(".html"),
            ]
        )

    for item in candidates:
        if item.suffix.lower() not in {".vue", ".html"}:
            continue
        if item.exists():
            return item
    return None


def _extract_local_import_specs(source):
    text = str(source or "")
    specs = set()
    pattern = re.compile(r"""import\s+[^;\n]*?\s+from\s+['"]([^'"]+)['"]""")
    for match in pattern.finditer(text):
        spec = str(match.group(1) or "").strip()
        if spec:
            specs.add(spec)
    return sorted(specs)


def _collect_visual_editor_editable_files(primary_file_path, app_root, max_files=60):
    app_root_resolved = app_root.resolve()
    queue = [primary_file_path.resolve()]
    visited = set()
    resolved_files = []

    while queue and len(resolved_files) < max_files:
        file_path = queue.pop(0)
        file_key = str(file_path)
        if file_key in visited:
            continue
        visited.add(file_key)

        try:
            file_path.relative_to(app_root_resolved)
        except Exception:
            continue
        if not file_path.exists():
            continue
        if file_path.suffix.lower() not in {".vue", ".html"}:
            continue

        resolved_files.append(file_path)

        if file_path.suffix.lower() != ".vue":
            continue
        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception:
            source = ""
        for spec in _extract_local_import_specs(source):
            next_file = _resolve_visual_editor_file_candidate(spec, file_path, app_root)
            if not next_file:
                continue
            if str(next_file) in visited:
                continue
            queue.append(next_file)

    files = []
    for idx, file_path in enumerate(resolved_files):
        rel = _relative_path(file_path, app_root)
        file_type = "vue" if file_path.suffix.lower() == ".vue" else "html"
        files.append(
            {
                "file": rel,
                "file_type": file_type,
                "name": file_path.stem,
                "is_primary": idx == 0,
                "label": f"{file_path.stem} ({file_type.upper()})",
            }
        )
    return files


def _collect_frontend_component_usage(frontend_routes, app_root, max_routes=260):
    app_root = Path(app_root)
    usage_map = {}

    for route_row in list(frontend_routes or [])[:max_routes]:
        raw_route_guess = str(route_row.get("route_guess") or "").strip()
        if raw_route_guess == "default-route-fallback":
            continue
        route_key = _normalize_tracked_path(raw_route_guess)
        if not route_key or not route_key.startswith("/mysite") or route_key.startswith("/management"):
            continue
        page_rel = str(route_row.get("file") or "").strip()
        if not page_rel:
            continue

        page_path = (app_root / page_rel).resolve()
        try:
            page_path.relative_to(app_root.resolve())
        except Exception:
            continue
        if not page_path.exists() or page_path.suffix.lower() != ".vue":
            continue

        try:
            source = page_path.read_text(encoding="utf-8")
        except Exception:
            source = ""

        for spec in _extract_local_import_specs(source):
            component_path = _resolve_visual_editor_file_candidate(spec, page_path, app_root)
            if not component_path:
                continue
            component_rel = _relative_path(component_path, app_root)
            if "/frontend/src/components/" not in f"/{component_rel}":
                continue
            usage_map.setdefault(component_rel, set()).add(route_key)

    return {key: sorted(values) for key, values in usage_map.items()}


def _is_frontend_component_file(file_rel):
    value = str(file_rel or "").strip().replace("\\", "/").lstrip("/")
    if not value:
        return False
    return "/frontend/src/components/" in f"/{value}"


def _resolve_component_usage_routes(component_file_rel, app_root):
    component_file = str(component_file_rel or "").strip().replace("\\", "/").lstrip("/")
    if not component_file or not _is_frontend_component_file(component_file):
        return []

    app_root = Path(app_root)
    app_vue_file = app_root / "frontend" / "src" / "App.vue"
    frontend_routes = _extract_frontend_routes(app_vue_file, app_root)
    usage_map = _collect_frontend_component_usage(frontend_routes, app_root)
    return list(usage_map.get(component_file, []))


def _resolve_visual_editor_scope_key(route, file_rel=None):
    file_value = str(file_rel or "").strip().replace("\\", "/").lstrip("/")
    if _is_frontend_component_file(file_value):
        return _normalize_tracked_path(f"component::{file_value}")
    return _normalize_tracked_path(route)


def _resolve_direct_visual_editor_file(target_file, app_root):
    app_root = Path(app_root)
    app_root_resolved = app_root.resolve()
    file_rel = str(target_file or "").strip().replace("\\", "/").lstrip("/")
    if not file_rel:
        return None
    file_path = (app_root / file_rel).resolve()
    try:
        file_path.relative_to(app_root_resolved)
    except Exception:
        return None
    if not file_path.exists():
        return None
    if file_path.suffix.lower() not in {".vue", ".html"}:
        return None

    allowed_roots = [
        (app_root / "frontend" / "src" / "components").resolve(),
        (app_root / "frontend" / "src" / "pages").resolve(),
        (app_root / "mysite" / "www" / "mysite").resolve(),
    ]
    allowed = False
    for root in allowed_roots:
        try:
            file_path.relative_to(root)
            allowed = True
            break
        except Exception:
            continue
    if not allowed:
        return None

    file_type = "vue" if file_path.suffix.lower() == ".vue" else "html"
    return {
        "file_rel": file_rel,
        "file_path": file_path,
        "file_type": file_type,
        "component": file_path.stem,
    }


def _resolve_management_visual_editor_target(route, target_file=None):
    app_root = Path(frappe.get_app_path("mysite")).parent
    app_root_resolved = app_root.resolve()
    route_key = _normalize_tracked_path(route)
    target_file_value = str(target_file or "").strip()

    # When editing a file directly, ignore management routes as preview roots.
    if route_key.startswith("/management") and target_file_value:
        route_key = ""

    if (not route_key or not route_key.startswith("/mysite")) and target_file_value:
        direct_target = _resolve_direct_visual_editor_file(target_file_value, app_root)
        if not direct_target:
            frappe.throw("مسیر صفحه یا فایل انتخابی معتبر نیست.")
        resolved_route = route_key if route_key.startswith("/mysite") and not route_key.startswith("/management") else ""
        if not resolved_route and _is_frontend_component_file(direct_target.get("file_rel")):
            usage_routes = _resolve_component_usage_routes(direct_target.get("file_rel"), app_root)
            for usage_route in usage_routes:
                normalized_usage_route = _normalize_tracked_path(usage_route)
                if not normalized_usage_route or not normalized_usage_route.startswith("/mysite"):
                    continue
                if normalized_usage_route.startswith("/management"):
                    continue
                resolved_route = normalized_usage_route
                break
        if not resolved_route:
            resolved_route = "/mysite"
        return {
            "route": resolved_route,
            "app_root": app_root,
            "file_rel": direct_target.get("file_rel"),
            "primary_file_rel": direct_target.get("file_rel"),
            "file_path": direct_target.get("file_path"),
            "component": direct_target.get("component"),
            "file_type": direct_target.get("file_type"),
            "editable_files": [
                {
                    "file": direct_target.get("file_rel"),
                    "file_type": direct_target.get("file_type"),
                    "name": direct_target.get("component"),
                    "is_primary": True,
                    "label": f"{direct_target.get('component')} ({str(direct_target.get('file_type') or '').upper()})",
                }
            ],
        }

    if not route_key or not route_key.startswith("/mysite"):
        frappe.throw("مسیر صفحه معتبر نیست.")

    app_vue_file = app_root / "frontend" / "src" / "App.vue"

    frontend_routes = _extract_frontend_routes(app_vue_file, app_root)
    frontend_match = next(
        (
            row
            for row in (frontend_routes or [])
            if _normalize_tracked_path(row.get("route_guess")) == route_key and str(row.get("file") or "").strip()
        ),
        None,
    )

    file_rel = str((frontend_match or {}).get("file") or "").strip()
    component = str((frontend_match or {}).get("component") or "").strip()
    if not file_rel:
        website_pages = _scan_website_pages(app_root)
        website_map = {row.get("route"): row for row in website_pages if row.get("route")}
        file_rel = str((website_map.get(route_key) or {}).get("html_file") or "").strip()

    if not file_rel:
        frappe.throw("برای این مسیر فایل قابل‌ویرایش پیدا نشد.")

    primary_file_path = (app_root / file_rel).resolve()
    try:
        primary_file_path.relative_to(app_root_resolved)
    except Exception:
        frappe.throw("مسیر فایل صفحه معتبر نیست.")

    if primary_file_path.suffix.lower() not in {".vue", ".html"}:
        frappe.throw("فقط فایل‌های Vue/HTML قابل ویرایش هستند.")
    if not primary_file_path.exists():
        frappe.throw("فایل صفحه پیدا نشد.")

    editable_files = _collect_visual_editor_editable_files(primary_file_path, app_root)
    editable_rel_map = {str(row.get("file") or "").strip(): row for row in editable_files}
    selected_rel = str(target_file or "").strip() or file_rel
    if selected_rel not in editable_rel_map:
        direct_target = _resolve_direct_visual_editor_file(selected_rel, app_root)
        if not direct_target:
            frappe.throw("فایل انتخابی برای این مسیر قابل ویرایش نیست.")
        selected_rel = str(direct_target.get("file_rel") or "").strip()
        selected_meta = {
            "file": selected_rel,
            "file_type": direct_target.get("file_type"),
            "name": direct_target.get("component"),
            "is_primary": False,
            "label": f"{direct_target.get('component')} ({str(direct_target.get('file_type') or '').upper()})",
        }
        editable_files.append(selected_meta)
        editable_rel_map[selected_rel] = selected_meta

    file_path = (app_root / selected_rel).resolve()
    try:
        file_path.relative_to(app_root_resolved)
    except Exception:
        frappe.throw("مسیر فایل صفحه معتبر نیست.")
    if not file_path.exists():
        frappe.throw("فایل انتخابی پیدا نشد.")

    selected_meta = editable_rel_map.get(selected_rel) or {}
    selected_component = component if selected_rel == file_rel else str(selected_meta.get("name") or Path(selected_rel).stem)

    return {
        "route": route_key,
        "app_root": app_root,
        "file_rel": selected_rel,
        "primary_file_rel": file_rel,
        "file_path": file_path,
        "component": selected_component,
        "file_type": "vue" if file_path.suffix.lower() == ".vue" else "html",
        "editable_files": editable_files,
    }


def _resolve_management_visual_editor_preview_route(route_key, raw_route=None):
    normalized_route = _normalize_tracked_path(route_key)
    if not normalized_route:
        return "/mysite"
    if (
        normalized_route == "/default-route-fallback"
        or not normalized_route.startswith("/mysite")
        or normalized_route.startswith("/management")
    ):
        return "/mysite"

    raw_value = str(raw_route or "").strip()
    if raw_value:
        try:
            parsed = urlsplit(raw_value)
            raw_path = _normalize_tracked_path(parsed.path or raw_value)
            if raw_path == normalized_route and parsed.query:
                return f"{normalized_route}?{parsed.query}"
        except Exception:
            pass

    # Product detail route requires a model name; pick a sample model for preview.
    if normalized_route == "/product":
        sample_model = ""
        try:
            sample_model = frappe.db.get_value(
                "Item Variant Attribute",
                {"attribute": "مدل محصول", "attribute_value": ["!=", ""]},
                "attribute_value",
            )
        except Exception:
            sample_model = ""
        sample_model = str(sample_model or "").strip()
        if sample_model:
            return f"/product/{quote(sample_model)}"
        return "/sofas"

    return normalized_route


def _serialize_visual_editor_history(route, target_file=None):
    route_key = _normalize_tracked_path(route)
    history = _load_management_visual_editor_history()
    route_payload = history.get(route_key) if isinstance(history.get(route_key), dict) else {}
    versions = route_payload.get("versions") if isinstance(route_payload.get("versions"), list) else []
    target_file_value = str(target_file or "").strip()
    items = []
    for row in reversed(versions):
        if not isinstance(row, dict):
            continue
        row_file = str(row.get("file") or "").strip()
        if target_file_value and row_file != target_file_value:
            continue
        items.append(
            {
                "id": str(row.get("id") or "").strip(),
                "saved_at": str(row.get("saved_at") or ""),
                "saved_by": str(row.get("saved_by") or ""),
                "note": str(row.get("note") or ""),
                "file": row_file,
                "sha1": str(row.get("sha1") or ""),
            }
        )
    return items


def _build_managed_visual_css(rows, raw_css):
    css_from_rows = _visual_rows_to_css(rows or [])
    css_parts = []
    if css_from_rows:
        css_parts.append(css_from_rows)
    raw_css_text = str(raw_css or "").strip()
    if raw_css_text:
        css_parts.append(raw_css_text)
    return "\n\n".join(css_parts).strip()


def _infer_route_title(route, fallback="صفحه"):
    path = _normalize_tracked_path(route)
    if path == "/mysite":
        return "صفحه اصلی"
    slug = path.replace("/", "").strip("/") if path else ""
    slug = slug or fallback
    slug = slug.replace("-", " ").replace("_", " ").strip()
    return slug or fallback


def _management_page_overrides_path():
    return Path(frappe.get_site_path("private", "mysite_management_page_overrides.json"))


def _load_management_page_overrides():
    path = _management_page_overrides_path()
    if not path.exists():
        return {}
    raw_text = ""
    try:
        raw_text = path.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        try:
            decoder = json.JSONDecoder()
            payload, _ = decoder.raw_decode((raw_text or "").lstrip())
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}


def _save_management_page_overrides(payload):
    path = _management_page_overrides_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload or {}, ensure_ascii=False, indent=2)
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _replace_or_insert_head_tag(source, pattern, new_tag):
    flags = re.IGNORECASE | re.DOTALL
    if re.search(pattern, source, flags=flags):
        if new_tag:
            return re.sub(pattern, new_tag, source, count=1, flags=flags)
        return re.sub(pattern, "", source, flags=flags)

    if not new_tag:
        return source

    close_head = re.search(r"</head\s*>", source, flags=re.IGNORECASE)
    insertion = f"    {new_tag}\n"
    if close_head:
        return f"{source[:close_head.start()]}{insertion}{source[close_head.start():]}"
    return f"{insertion}{source}"


def _contains_jinja_syntax(value):
    text = str(value or "")
    if not text:
        return False
    return ("{{" in text and "}}" in text) or ("{%" in text and "%}" in text) or ("{#" in text and "#}" in text)


def _prepare_head_meta_value(value):
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = html_unescape(text)
    if _contains_jinja_syntax(normalized):
        return normalized
    return html_escape(normalized)


def _apply_meta_to_html(source, title, meta_description, canonical_url, meta_image, noindex):
    result = source
    title_text = _prepare_head_meta_value(title)
    if title_text:
        result = _replace_or_insert_head_tag(result, r"<title>.*?</title>", f"<title>{title_text}</title>")

    desc_text = _prepare_head_meta_value(meta_description)
    desc_tag = f'<meta name="description" content="{desc_text}" />' if desc_text else ""
    result = _replace_or_insert_head_tag(result, r'<meta[^>]*name=["\']description["\'][^>]*>', desc_tag)

    canonical_text = _prepare_head_meta_value(canonical_url)
    canonical_tag = f'<link rel="canonical" href="{canonical_text}" />' if canonical_text else ""
    result = _replace_or_insert_head_tag(result, r'<link[^>]*rel=["\']canonical["\'][^>]*>', canonical_tag)

    image_text = _prepare_head_meta_value(meta_image)
    image_tag = f'<meta property="og:image" content="{image_text}" />' if image_text else ""
    result = _replace_or_insert_head_tag(result, r'<meta[^>]*property=["\']og:image["\'][^>]*>', image_tag)

    robots_value = "noindex,nofollow" if _to_bool(noindex, False) else "index,follow"
    robots_tag = f'<meta name="robots" content="{robots_value}" />'
    result = _replace_or_insert_head_tag(result, r'<meta[^>]*name=["\']robots["\'][^>]*>', robots_tag)
    return result


def _validate_jinja_template_source(source, file_rel=""):
    source_text = str(source or "")
    if not source_text.strip():
        frappe.throw("محتوای فایل قابل ویرایش خالی است.")
    try:
        get_jenv().parse(source_text)
    except TemplateSyntaxError as exc:
        line_no = int(exc.lineno or 0) if getattr(exc, "lineno", None) else 0
        file_hint = f" ({file_rel})" if file_rel else ""
        message = str(exc.message or str(exc)).strip() or "خطای سینتکس Jinja"
        if line_no > 0:
            frappe.throw(f"خطای سینتکس Jinja در فایل{file_hint}، خط {line_no}: {message}")
        frappe.throw(f"خطای سینتکس Jinja در فایل{file_hint}: {message}")


def _clean_page_override_payload(payload, fallback=None):
    fallback = fallback or {}
    raw_content_rows = payload.get("content_overrides") if "content_overrides" in payload else fallback.get("content_overrides", [])
    raw_visual_rows = payload.get("visual_overrides") if "visual_overrides" in payload else fallback.get("visual_overrides", [])
    raw_visual_css = payload.get("visual_raw_css") if "visual_raw_css" in payload else fallback.get("visual_raw_css", "")
    visual_css_text = str(raw_visual_css or "")
    if len(visual_css_text) > 120000:
        visual_css_text = visual_css_text[:120000]
    token_collections = payload.get("token_collections") if isinstance(payload.get("token_collections"), dict) else fallback.get("token_collections", {})
    token_active_collection = str(payload.get("token_active_collection") or fallback.get("token_active_collection") or "").strip()
    token_active_mode = str(payload.get("token_active_mode") or fallback.get("token_active_mode") or "light").strip().lower() or "light"
    return {
        "title": str(payload.get("title") or fallback.get("title") or "").strip(),
        "meta_description": str(payload.get("meta_description") or fallback.get("meta_description") or "").strip(),
        "canonical_url": str(payload.get("canonical_url") or fallback.get("canonical_url") or "").strip(),
        "meta_image": str(payload.get("meta_image") or fallback.get("meta_image") or "").strip(),
        "noindex": _to_bool(payload.get("noindex"), fallback.get("noindex", False)),
        "protected_page": _to_bool(payload.get("protected_page"), fallback.get("protected_page", False)),
        "status_key": str(payload.get("status_key") or fallback.get("status_key") or "published").strip() or "published",
        "content_overrides": _clean_content_override_rows(raw_content_rows),
        "visual_overrides": _clean_visual_override_rows(raw_visual_rows),
        "visual_raw_css": visual_css_text,
        "token_collections": token_collections,
        "token_active_collection": token_active_collection,
        "token_active_mode": token_active_mode,
        "content_updated_at": str(payload.get("content_updated_at") or fallback.get("content_updated_at") or "").strip(),
        "content_updated_by": str(payload.get("content_updated_by") or fallback.get("content_updated_by") or "").strip(),
        "visual_updated_at": str(payload.get("visual_updated_at") or fallback.get("visual_updated_at") or "").strip(),
        "visual_updated_by": str(payload.get("visual_updated_by") or fallback.get("visual_updated_by") or "").strip(),
    }


def _infer_meta_description(route, title):
    route = _normalize_tracked_path(route)
    title = str(title or "").strip()
    short_title = re.sub(r"\s*\|.*$", "", title).strip() or "این صفحه"

    if route == "/mysite":
        return "فروشگاه دن‌روم؛ مشاهده مدل‌های مبلمان، صندلی، میز و پروژه‌های اجراشده با امکان مقایسه، انتخاب پارچه و ثبت سفارش."
    if route.startswith("/blog"):
        return f"{short_title} در مجله دن‌روم؛ راهنمای انتخاب، نگهداری و چیدمان مبلمان با نکات کاربردی و مقایسه مدل‌ها."
    if route.startswith("/product") or route.startswith("/sofa") or route.startswith("/sofas"):
        return f"{short_title} در دن‌روم؛ بررسی مشخصات، ابعاد، رنگ‌بندی و متریال محصول همراه با تصاویر و اطلاعات خرید."
    if route.startswith("/projects") or route.startswith("/project") or route.startswith("/gallery") or route.startswith("/shop-by-look"):
        return f"{short_title} در دن‌روم؛ مشاهده نمونه پروژه‌ها، ایده‌های چیدمان و تصاویر اجراشده برای انتخاب بهتر مبلمان."
    if route.startswith("/fabrics") or route.startswith("/cushions"):
        return f"{short_title} در دن‌روم؛ بررسی رنگ، بافت و مشخصات پارچه‌ها و اکسسوری‌ها برای ست‌کردن با فضای منزل."
    if route.startswith("/dealers") or route.startswith("/consultation") or route.startswith("/cooperation") or route.startswith("/downloads"):
        return f"{short_title} در دن‌روم؛ اطلاعات تماس، خدمات مشاوره و منابع موردنیاز برای ارتباط و دریافت خدمات بهتر."
    if route.startswith("/management") or route.startswith("/dashboard"):
        return f"{short_title}؛ پنل مدیریت دن‌روم برای مشاهده گزارش‌ها، تنظیمات صفحات و کنترل بخش‌های مدیریتی سایت."
    if route.startswith("/login"):
        return "ورود به پنل دن‌روم برای دسترسی به امکانات مدیریت، گزارش‌های تحلیلی و تنظیمات پیشرفته سایت."
    if route.startswith("/cart") or route.startswith("/saved"):
        return f"{short_title} در دن‌روم؛ مدیریت اقلام انتخابی، بررسی قیمت‌ها و نهایی‌سازی سفارش محصولات."
    return f"{short_title} در دن‌روم؛ اطلاعات کامل این صفحه، معرفی محتوا و دسترسی سریع به بخش‌های مرتبط سایت."


def _apply_page_payload_to_html(route, clean_payload, app_root, website_map):
    html_updated = False
    website_row = website_map.get(route) or {}
    html_rel = str(website_row.get("html_file") or "").strip()
    if not html_rel:
        return False

    html_path = (Path(app_root) / html_rel).resolve()
    try:
        html_path.relative_to(Path(app_root).resolve())
    except Exception:
        return False

    if not html_path.exists():
        return False

    source = html_path.read_text(encoding="utf-8")
    updated = _apply_meta_to_html(
        source=source,
        title=clean_payload.get("title"),
        meta_description=clean_payload.get("meta_description"),
        canonical_url=clean_payload.get("canonical_url"),
        meta_image=clean_payload.get("meta_image"),
        noindex=clean_payload.get("noindex"),
    )
    if updated != source:
        html_path.write_text(updated, encoding="utf-8")
        html_updated = True
    return html_updated


def _collect_page_traffic(days=30, limit=20):
    days = min(max(cint(days or 30), 1), 365)
    limit = min(max(cint(limit or 20), 1), 200)
    to_dt = now_datetime()
    from_dt = add_days(to_dt, -(days - 1))
    from_date = from_dt.strftime("%Y-%m-%d")
    to_date = to_dt.strftime("%Y-%m-%d")

    base_payload = {
        "range": {"days": days, "from_date": from_date, "to_date": to_date},
        "totals": {
            "views": 0,
            "unique_sessions": 0,
            "avg_time_spent_seconds": 0,
            "avg_scroll_depth": 0,
        },
        "daily_views": [],
        "top_pages": [],
        "route_stats": [],
    }
    if not frappe.db.exists("DocType", "Page View"):
        return base_payload

    params = {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59", "limit": limit}

    totals = frappe.db.sql(
        """
        SELECT
            COUNT(*) AS views,
            COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS unique_sessions,
            AVG(IFNULL(time_spent_seconds, 0)) AS avg_time_spent_seconds,
            AVG(IFNULL(scroll_depth, 0)) AS avg_scroll_depth
        FROM `tabPage View`
        WHERE entered_at >= %(from_dt)s
          AND entered_at <= %(to_dt)s
        """,
        params,
        as_dict=True,
    )
    totals_row = (totals or [{}])[0]
    base_payload["totals"] = {
        "views": cint(totals_row.get("views") or 0),
        "unique_sessions": cint(totals_row.get("unique_sessions") or 0),
        "avg_time_spent_seconds": round(flt(totals_row.get("avg_time_spent_seconds") or 0), 2),
        "avg_scroll_depth": round(flt(totals_row.get("avg_scroll_depth") or 0), 2),
    }

    route_rows = frappe.db.sql(
        """
        SELECT
            SUBSTRING_INDEX(IFNULL(url, ''), '?', 1) AS raw_path,
            COUNT(*) AS views,
            COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS unique_sessions,
            AVG(IFNULL(time_spent_seconds, 0)) AS avg_time_spent_seconds,
            AVG(IFNULL(scroll_depth, 0)) AS avg_scroll_depth
        FROM `tabPage View`
        WHERE entered_at >= %(from_dt)s
          AND entered_at <= %(to_dt)s
          AND IFNULL(url, '') != ''
        GROUP BY SUBSTRING_INDEX(IFNULL(url, ''), '?', 1)
        """,
        params,
        as_dict=True,
    )

    exit_rows = frappe.db.sql(
        """
        SELECT
            SUBSTRING_INDEX(IFNULL(pv.url, ''), '?', 1) AS raw_path,
            COUNT(*) AS exits
        FROM `tabPage View` pv
        INNER JOIN (
            SELECT
                session_id,
                MAX(IFNULL(left_at, entered_at)) AS max_ts
            FROM `tabPage View`
            WHERE entered_at >= %(from_dt)s
              AND entered_at <= %(to_dt)s
              AND IFNULL(session_id, '') != ''
            GROUP BY session_id
        ) ranked
          ON ranked.session_id = pv.session_id
         AND IFNULL(pv.left_at, pv.entered_at) = ranked.max_ts
        WHERE IFNULL(pv.url, '') != ''
        GROUP BY SUBSTRING_INDEX(IFNULL(pv.url, ''), '?', 1)
        """,
        params,
        as_dict=True,
    )
    exit_map = {}
    for row in exit_rows:
        path = _normalize_tracked_path(row.get("raw_path"))
        if not path:
            continue
        exit_map[path] = exit_map.get(path, 0) + cint(row.get("exits") or 0)

    merged = {}
    for row in route_rows:
        path = _normalize_tracked_path(row.get("raw_path"))
        if not path:
            continue
        views = cint(row.get("views") or 0)
        bucket = merged.setdefault(
            path,
            {
                "path": path,
                "views": 0,
                "unique_sessions": 0,
                "_time_weighted": 0,
                "_scroll_weighted": 0,
            },
        )
        bucket["views"] += views
        bucket["unique_sessions"] += cint(row.get("unique_sessions") or 0)
        bucket["_time_weighted"] += flt(row.get("avg_time_spent_seconds") or 0) * views
        bucket["_scroll_weighted"] += flt(row.get("avg_scroll_depth") or 0) * views

    stats = []
    for path, row in merged.items():
        views = max(cint(row.get("views") or 0), 1)
        exits = exit_map.get(path, 0)
        stats.append(
            {
                "path": path,
                "views": row.get("views") or 0,
                "unique_sessions": row.get("unique_sessions") or 0,
                "avg_time_spent_seconds": round((row.get("_time_weighted") or 0) / views, 2),
                "avg_scroll_depth": round((row.get("_scroll_weighted") or 0) / views, 2),
                "exits": exits,
                "exit_rate": round((exits / views) * 100, 2),
            }
        )
    stats = sorted(stats, key=lambda item: (-(item.get("views") or 0), item.get("path") or ""))

    daily_rows = frappe.db.sql(
        """
        SELECT DATE(entered_at) AS day_key, COUNT(*) AS views
        FROM `tabPage View`
        WHERE entered_at >= %(from_dt)s
          AND entered_at <= %(to_dt)s
        GROUP BY DATE(entered_at)
        ORDER BY day_key ASC
        """,
        params,
        as_dict=True,
    )
    base_payload["daily_views"] = [{"date": str(row.get("day_key")), "views": cint(row.get("views") or 0)} for row in daily_rows]
    base_payload["route_stats"] = stats
    base_payload["top_pages"] = stats[:limit]
    return base_payload


def _build_url_settings(frontend_routes, website_pages, route_stats):
    routes_index = {}

    def ensure(route):
        if route not in routes_index:
            routes_index[route] = {
                "route": route,
                "title": "",
                "source": "",
                "component": "",
                "file": "",
                "views": 0,
                "unique_sessions": 0,
                "avg_time_spent_seconds": 0,
                "avg_scroll_depth": 0,
                "exits": 0,
            }
        return routes_index[route]

    for row in website_pages or []:
        route = _normalize_tracked_path(row.get("route"))
        if not route:
            continue
        item = ensure(route)
        item["source"] = "صفحات وب‌سایت فرپ"
        item["title"] = row.get("title") or item.get("title") or ""
        item["file"] = row.get("html_file") or item.get("file") or ""

    for row in frontend_routes or []:
        route_guess = row.get("route_guess")
        if route_guess == "default-route-fallback":
            continue
        route = _normalize_tracked_path(route_guess)
        if not route:
            continue
        item = ensure(route)
        if not item.get("source"):
            item["source"] = "مسیر فرانت ویو"
        elif "مسیر فرانت ویو" not in item.get("source"):
            item["source"] = f"{item['source']} + مسیر فرانت ویو"
        item["component"] = row.get("component") or item.get("component") or ""
        if not item.get("file"):
            item["file"] = row.get("file") or ""

    traffic_map = {row.get("path"): row for row in (route_stats or []) if row.get("path")}
    tracked_in_known = 0
    for route, item in routes_index.items():
        stats = traffic_map.get(route)
        if not stats:
            continue
        item["views"] = cint(stats.get("views") or 0)
        item["unique_sessions"] = cint(stats.get("unique_sessions") or 0)
        item["avg_time_spent_seconds"] = round(flt(stats.get("avg_time_spent_seconds") or 0), 2)
        item["avg_scroll_depth"] = round(flt(stats.get("avg_scroll_depth") or 0), 2)
        item["exits"] = cint(stats.get("exits") or 0)
        if item["views"] > 0:
            tracked_in_known += 1

    routes = sorted(routes_index.values(), key=lambda item: (-(item.get("views") or 0), item.get("route") or ""))
    unmapped_routes = [
        {
            "route": row.get("path"),
            "views": cint(row.get("views") or 0),
            "unique_sessions": cint(row.get("unique_sessions") or 0),
        }
        for row in (route_stats or [])
        if row.get("path") and row.get("path") not in routes_index
    ][:15]

    base_url = (get_url() or "").rstrip("/")
    return {
        "base_url": base_url,
        "host_name": frappe.conf.get("host_name") or "",
        "api_base_url": f"{base_url}/api/method" if base_url else "/api/method",
        "frontend_base_path": "/mysite",
        "key_paths": [
            {"label": "صفحه اصلی", "path": "/mysite"},
            {"label": "پنل مدیریت", "path": "/management"},
            {"label": "مدیریت محصولات", "path": "/management-products"},
            {"label": "مدیریت بلاگ", "path": "/management-blog"},
            {"label": "آنالیتیکس مدیریت", "path": "/management-analytics"},
            {"label": "ورود", "path": "/login"},
            {"label": "نشانی متد مدیریت", "path": "/api/method/mysite.api.get_management_panel_data"},
        ],
        "stats": {
            "configured_routes": len(routes),
            "tracked_routes": len(route_stats or []),
            "tracked_known_routes": tracked_in_known,
            "coverage_percent": round((tracked_in_known / len(routes)) * 100, 2) if routes else 0,
        },
        "routes": routes,
        "unmapped_routes": unmapped_routes,
    }


@frappe.whitelist()
def save_management_page_config(route=None, payload=None):
    _require_management_access("content.edit")

    if isinstance(payload, str):
        try:
            payload = frappe.parse_json(payload)
        except Exception:
            payload = json.loads(payload or "{}")

    if payload is None:
        payload = {}
        if getattr(frappe, "request", None) and frappe.request.data:
            try:
                raw_payload = frappe.parse_json(frappe.request.data)
            except Exception:
                raw_payload = {}
            if isinstance(raw_payload, dict):
                route = route or raw_payload.get("route")
                payload = raw_payload.get("payload") if isinstance(raw_payload.get("payload"), dict) else raw_payload

    if not isinstance(payload, dict):
        payload = {}
    workflow_bypass = _workflow_bypass_enabled(payload)

    route = _normalize_tracked_path(route or payload.get("route"))
    if not route or not route.startswith("/mysite"):
        frappe.throw("مسیر صفحه معتبر نیست.")

    if not workflow_bypass and should_enforce("content"):
        current = _load_management_page_overrides().get(route) or {}
        return _workflow_create_response(
            module_key="content",
            target_type="page_config",
            target_key=route,
            payload=payload,
            current_snapshot=current if isinstance(current, dict) else {},
            source_endpoint="save_management_page_config",
        )

    app_root = Path(frappe.get_app_path("mysite")).parent
    website_pages = _scan_website_pages(app_root)
    website_map = {row.get("route"): row for row in website_pages if row.get("route")}

    overrides = _load_management_page_overrides()
    current_override = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
    clean_payload = _clean_page_override_payload(payload, fallback=current_override)
    if not clean_payload.get("title"):
        clean_payload["title"] = str((website_map.get(route) or {}).get("title") or route.replace("/", "") or "صفحه").strip()

    clean_payload["status_label"] = "منتشر شده" if clean_payload.get("status_key") == "published" else "غیرفعال"
    clean_payload["updated_at"] = now_datetime().isoformat()
    clean_payload["updated_by"] = frappe.session.user

    html_updated = _apply_page_payload_to_html(route, clean_payload, app_root, website_map)

    overrides[route] = clean_payload
    _save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()

    response = {
        "ok": True,
        "route": route,
        "config": clean_payload,
        "html_updated": html_updated,
    }
    _workflow_shadow_record(
        module_key="content",
        target_type="page_config",
        target_key=route,
        payload=payload,
        current_snapshot=current_override,
        source_endpoint="save_management_page_config",
        publish_result=response,
    )
    return response


@frappe.whitelist()
def get_management_page_content_schema(route=None):
    _require_management_access("content.edit")
    route = _normalize_tracked_path(route or frappe.form_dict.get("route"))
    if not route or not route.startswith("/mysite"):
        frappe.throw("مسیر صفحه معتبر نیست.")

    app_root = Path(frappe.get_app_path("mysite")).parent
    catalog = _scan_route_content_catalog(route, app_root)

    overrides = _load_management_page_overrides()
    route_override = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
    existing_rows = _clean_content_override_rows(route_override.get("content_overrides") if isinstance(route_override, dict) else [])

    existing_by_key = {}
    existing_by_source = {}
    for row in existing_rows:
        key = str(row.get("key") or "").strip()
        source_text = _normalize_content_text(row.get("source_text"))
        if key and key not in existing_by_key:
            existing_by_key[key] = row
        if source_text and source_text not in existing_by_source:
            existing_by_source[source_text] = row

    merged_items = []
    seen_keys = set()
    for item in catalog.get("items") or []:
        key = str(item.get("key") or "").strip()
        source_text = _normalize_content_text(item.get("source_text"))
        matched = existing_by_key.get(key) or existing_by_source.get(source_text) or {}
        replacement_text = _normalize_content_text(matched.get("replacement_text"))
        row = {
            **item,
            "replacement_text": replacement_text,
            "has_override": bool(replacement_text and replacement_text != source_text),
        }
        merged_items.append(row)
        if key:
            seen_keys.add(key)

    stale_items = []
    for row in existing_rows:
        key = str(row.get("key") or "").strip()
        replacement_text = _normalize_content_text(row.get("replacement_text"))
        source_text = _normalize_content_text(row.get("source_text"))
        if not key or key in seen_keys:
            continue
        if not replacement_text or replacement_text == source_text:
            continue
        stale_items.append({**row, "stale": True})

    return {
        "route": route,
        "items": merged_items,
        "stale_items": stale_items,
        "sources": catalog.get("sources") or [],
        "total_items": len(merged_items),
        "override_items": len([row for row in merged_items if row.get("has_override")]),
    }


@frappe.whitelist()
def save_management_page_content_overrides(route=None, items=None, payload=None):
    _require_management_access("content.edit")
    request_payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(request_payload)

    if items is None:
        items = request_payload.get("items")
    if items is None:
        items = request_payload.get("content_overrides")

    route = _normalize_tracked_path(route or request_payload.get("route"))
    if not route or not route.startswith("/mysite"):
        frappe.throw("مسیر صفحه معتبر نیست.")

    if not workflow_bypass and should_enforce("content"):
        current = _load_management_page_overrides().get(route) or {}
        return _workflow_create_response(
            module_key="content",
            target_type="page_content_override",
            target_key=route,
            payload={"route": route, "items": items},
            current_snapshot=current if isinstance(current, dict) else {},
            source_endpoint="save_management_page_content_overrides",
        )

    app_root = Path(frappe.get_app_path("mysite")).parent
    website_pages = _scan_website_pages(app_root)
    website_map = {row.get("route"): row for row in website_pages if row.get("route")}

    overrides = _load_management_page_overrides()
    current_override = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
    clean_payload = _clean_page_override_payload({"content_overrides": items}, fallback=current_override)
    if not clean_payload.get("title"):
        clean_payload["title"] = str((website_map.get(route) or {}).get("title") or route.replace("/", "") or "صفحه").strip()

    clean_payload["status_label"] = "منتشر شده" if clean_payload.get("status_key") == "published" else "غیرفعال"
    clean_payload["updated_at"] = now_datetime().isoformat()
    clean_payload["updated_by"] = frappe.session.user
    clean_payload["content_updated_at"] = now_datetime().isoformat()
    clean_payload["content_updated_by"] = frappe.session.user

    overrides[route] = clean_payload
    _save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()

    content_rows = clean_payload.get("content_overrides") or []
    active_rows = [
        row
        for row in content_rows
        if _normalize_content_text(row.get("replacement_text")) and _normalize_content_text(row.get("replacement_text")) != _normalize_content_text(row.get("source_text"))
    ]
    response = {
        "ok": True,
        "route": route,
        "saved_items": len(content_rows),
        "active_items": len(active_rows),
    }
    _workflow_shadow_record(
        module_key="content",
        target_type="page_content_override",
        target_key=route,
        payload={"route": route, "items": items},
        current_snapshot=current_override,
        source_endpoint="save_management_page_content_overrides",
        publish_result=response,
    )
    return response


@frappe.whitelist()
def get_management_page_visual_overrides(route=None):
    _require_management_access("content.edit")
    route = _normalize_tracked_path(route or frappe.form_dict.get("route"))
    if not route or not route.startswith("/mysite"):
        frappe.throw("مسیر صفحه معتبر نیست.")

    overrides = _load_management_page_overrides()
    route_override = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
    rows = _clean_visual_override_rows(route_override.get("visual_overrides") if isinstance(route_override, dict) else [])
    return {
        "route": route,
        "items": rows,
        "count": len(rows),
        "updated_at": str(route_override.get("visual_updated_at") or ""),
        "updated_by": str(route_override.get("visual_updated_by") or ""),
    }


@frappe.whitelist()
def save_management_page_visual_overrides(route=None, items=None, payload=None):
    _require_management_access("content.edit")
    request_payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(request_payload)

    if items is None:
        items = request_payload.get("items")
    if items is None:
        items = request_payload.get("visual_overrides")

    route = _normalize_tracked_path(route or request_payload.get("route"))
    if not route or not route.startswith("/mysite"):
        frappe.throw("مسیر صفحه معتبر نیست.")

    if not workflow_bypass and should_enforce("content"):
        current = _load_management_page_overrides().get(route) or {}
        return _workflow_create_response(
            module_key="content",
            target_type="page_visual_override",
            target_key=route,
            payload={"route": route, "items": items},
            current_snapshot=current if isinstance(current, dict) else {},
            source_endpoint="save_management_page_visual_overrides",
        )

    app_root = Path(frappe.get_app_path("mysite")).parent
    website_pages = _scan_website_pages(app_root)
    website_map = {row.get("route"): row for row in website_pages if row.get("route")}

    overrides = _load_management_page_overrides()
    current_override = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
    clean_payload = _clean_page_override_payload({"visual_overrides": items}, fallback=current_override)
    if not clean_payload.get("title"):
        clean_payload["title"] = str((website_map.get(route) or {}).get("title") or route.replace("/", "") or "صفحه").strip()

    clean_payload["status_label"] = "منتشر شده" if clean_payload.get("status_key") == "published" else "غیرفعال"
    clean_payload["updated_at"] = now_datetime().isoformat()
    clean_payload["updated_by"] = frappe.session.user
    clean_payload["visual_updated_at"] = now_datetime().isoformat()
    clean_payload["visual_updated_by"] = frappe.session.user

    overrides[route] = clean_payload
    _save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()

    visual_rows = clean_payload.get("visual_overrides") or []
    active_rows = [
        row for row in visual_rows
        if row.get("styles") or row.get("apply_text") or row.get("apply_html")
    ]
    response = {
        "ok": True,
        "route": route,
        "saved_items": len(visual_rows),
        "active_items": len(active_rows),
    }
    _workflow_shadow_record(
        module_key="content",
        target_type="page_visual_override",
        target_key=route,
        payload={"route": route, "items": items},
        current_snapshot=current_override,
        source_endpoint="save_management_page_visual_overrides",
        publish_result=response,
    )
    return response


@frappe.whitelist()
def get_management_visual_editor_payload(route=None, target_file=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.get_management_visual_editor_payload(route=route, target_file=target_file)

@frappe.whitelist(allow_guest=True)
def save_management_visual_editor_changes(
    route=None, items=None, raw_css=None, full_source=None,
    note=None, target_file=None, payload=None
):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.save_management_visual_editor_changes(
        route=route,
        items=items,
        raw_css=raw_css,
        full_source=full_source,
        note=note,
        target_file=target_file,
        payload=payload,
    )


def _save_management_visual_editor_changes_impl(
    route=None, items=None, raw_css=None, full_source=None,
    note=None, target_file=None, payload=None
):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api._save_management_visual_editor_changes_impl(
        route=route,
        items=items,
        raw_css=raw_css,
        full_source=full_source,
        note=note,
        target_file=target_file,
        payload=payload,
    )

@frappe.whitelist()
def get_management_visual_editor_history(route=None, target_file=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.get_management_visual_editor_history(route=route, target_file=target_file)


@frappe.whitelist()
def restore_management_visual_editor_history(route=None, version_id=None, target_file=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.restore_management_visual_editor_history(
        route=route,
        version_id=version_id,
        target_file=target_file,
        payload=payload,
    )


@frappe.whitelist()
def get_management_visual_editor_versioning(route=None, target_file=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.get_management_visual_editor_versioning(
        route=route,
        target_file=target_file,
        payload=payload,
    )


@frappe.whitelist()
def create_management_visual_editor_branch(route=None, branch_name=None, from_branch=None, target_file=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.create_management_visual_editor_branch(
        route=route,
        branch_name=branch_name,
        from_branch=from_branch,
        target_file=target_file,
        payload=payload,
    )


@frappe.whitelist()
def set_management_visual_editor_active_branch(route=None, branch_name=None, target_file=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.set_management_visual_editor_active_branch(
        route=route,
        branch_name=branch_name,
        target_file=target_file,
        payload=payload,
    )


@frappe.whitelist()
def create_management_visual_editor_milestone(route=None, title=None, note=None, branch_name=None, target_file=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.create_management_visual_editor_milestone(
        route=route,
        title=title,
        note=note,
        branch_name=branch_name,
        target_file=target_file,
        payload=payload,
    )


@frappe.whitelist()
def merge_management_visual_editor_branch(route=None, source_branch=None, target_branch=None, target_file=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.merge_management_visual_editor_branch(
        route=route,
        source_branch=source_branch,
        target_branch=target_branch,
        target_file=target_file,
        payload=payload,
    )


@frappe.whitelist()
def get_management_component_library(library_name=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.get_management_component_library(
        library_name=library_name,
    )


@frappe.whitelist()
def publish_management_component_library(library_name=None, components=None, note=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.publish_management_component_library(
        library_name=library_name,
        components=components,
        note=note,
        payload=payload,
    )


@frappe.whitelist()
def consume_management_component_library(library_name=None, version_id=None, payload=None):
    from mysite.management_editor import api as management_editor_api

    return management_editor_api.consume_management_component_library(
        library_name=library_name,
        version_id=version_id,
        payload=payload,
    )


@frappe.whitelist(allow_guest=True)
def get_route_content_overrides(route=None):
    request_path = ""
    try:
        request_path = str(getattr(getattr(frappe, "request", None), "path", "") or "").strip()
    except Exception:
        request_path = ""

    route = _normalize_tracked_path(route or frappe.form_dict.get("route") or request_path)
    if not route or not route.startswith("/mysite"):
        return {"route": route or "", "items": [], "count": 0}

    overrides = _load_management_page_overrides()
    route_override = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
    rows = _clean_content_override_rows(route_override.get("content_overrides") if isinstance(route_override, dict) else [])

    result = []
    for row in rows:
        source_text = _normalize_content_text(row.get("source_text"))
        replacement_text = _normalize_content_text(row.get("replacement_text"))
        if not source_text or not replacement_text or replacement_text == source_text:
            continue
        result.append(
            {
                "key": str(row.get("key") or "").strip(),
                "source_text": source_text,
                "replacement_text": replacement_text,
            }
        )

    return {"route": route, "items": result, "count": len(result)}


@frappe.whitelist(allow_guest=True)
def get_route_visual_overrides(route=None):
    request_path = ""
    try:
        request_path = str(getattr(getattr(frappe, "request", None), "path", "") or "").strip()
    except Exception:
        request_path = ""

    route = _normalize_tracked_path(route or frappe.form_dict.get("route") or request_path)
    if not route or not route.startswith("/mysite"):
        return {"route": route or "", "items": [], "count": 0}

    overrides = _load_management_page_overrides()
    route_override = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
    rows = _clean_visual_override_rows(route_override.get("visual_overrides") if isinstance(route_override, dict) else [])
    token_collections = route_override.get("token_collections") if isinstance(route_override.get("token_collections"), dict) else {}
    token_active_collection = str(route_override.get("token_active_collection") or "") if isinstance(route_override, dict) else ""
    token_active_mode = str(route_override.get("token_active_mode") or "light") if isinstance(route_override, dict) else "light"

    result = []
    for row in rows:
        styles = row.get("styles") if isinstance(row.get("styles"), dict) else {}
        selector = str(row.get("selector") or "").strip()
        if not selector:
            continue
        payload = {
            "selector": selector,
            "styles": styles,
        }
        if _to_bool(row.get("apply_text"), False):
            payload["text_content"] = str(row.get("text_content") or "")
        if _to_bool(row.get("apply_html"), False):
            payload["html_content"] = str(row.get("html_content") or "")
        result.append(payload)

    return {
        "route": route,
        "items": result,
        "count": len(result),
        "token_collections": token_collections,
        "token_active_collection": token_active_collection,
        "token_active_mode": token_active_mode,
    }


@frappe.whitelist()
def generate_management_meta_descriptions(overwrite=False):
    _require_management_access()
    overwrite = _to_bool(overwrite, False)

    app_root = Path(frappe.get_app_path("mysite")).parent
    frontend_root = app_root / "frontend" / "src"
    app_vue_file = frontend_root / "App.vue"

    frontend_routes = _extract_frontend_routes(app_vue_file, app_root)
    website_pages = _scan_website_pages(app_root)
    website_map = {row.get("route"): row for row in website_pages if row.get("route")}
    route_rows = _build_url_settings(frontend_routes, website_pages, []).get("routes") or []
    route_title_map = {row.get("route"): str(row.get("title") or "").strip() for row in route_rows if row.get("route")}

    overrides = _load_management_page_overrides()
    updated_routes = []
    skipped_routes = []

    for row in route_rows:
        route = _normalize_tracked_path(row.get("route"))
        if not route or not route.startswith("/mysite"):
            continue

        existing = overrides.get(route) if isinstance(overrides.get(route), dict) else {}
        current_description = str(existing.get("meta_description") or (website_map.get(route) or {}).get("meta_description") or "").strip()
        if current_description and not overwrite:
            skipped_routes.append(route)
            continue

        title = str(existing.get("title") or route_title_map.get(route) or (website_map.get(route) or {}).get("title") or "").strip()
        if not title:
            page_guess = Path(str(row.get("file") or "")).stem
            title = page_guess or route.replace("/", "") or "صفحه"
        description = _infer_meta_description(route, title)
        if not description:
            skipped_routes.append(route)
            continue

        payload = _clean_page_override_payload(
            {
                **existing,
                "title": title,
                "meta_description": description,
            },
            fallback=existing,
        )
        payload["status_label"] = "منتشر شده" if payload.get("status_key") == "published" else "غیرفعال"
        payload["updated_at"] = now_datetime().isoformat()
        payload["updated_by"] = frappe.session.user

        _apply_page_payload_to_html(route, payload, app_root, website_map)
        overrides[route] = payload
        updated_routes.append(route)

    _save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()

    return {
        "ok": True,
        "total_routes": len(route_rows),
        "updated_count": len(updated_routes),
        "skipped_count": len(skipped_routes),
        "updated_routes": updated_routes,
    }


def _normalize_external_image_url(raw_url):
    value = str(raw_url or "").strip()
    if value.startswith("//"):
        value = f"https:{value}"
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        return ""
    if not parsed.netloc:
        return ""
    return value


def _is_private_or_local_host(hostname):
    host = str(hostname or "").strip().strip(".").lower()
    if not host:
        return True
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        resolved = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except Exception:
        return True
    for info in resolved:
        addr = str((info[4] or [""])[0]).strip()
        if not addr:
            continue
        try:
            ip = ipaddress.ip_address(addr)
        except Exception:
            continue
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            return True
    return False


def _infer_image_content_type(url_value):
    lower = str(url_value or "").lower().split("?")[0]
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".gif"):
        return "image/gif"
    if lower.endswith(".svg"):
        return "image/svg+xml"
    if lower.endswith(".avif"):
        return "image/avif"
    if lower.endswith(".jpeg") or lower.endswith(".jpg"):
        return "image/jpeg"
    return ""


@frappe.whitelist()
def management_image_proxy(url=None):
    _require_management_access("product.edit")
    target_url = _normalize_external_image_url(url or frappe.form_dict.get("url"))
    if not target_url:
        frappe.throw("نشانی تصویر معتبر نیست.")

    parsed = urlsplit(target_url)
    if _is_private_or_local_host(parsed.hostname):
        frappe.throw("دسترسی به این میزبان مجاز نیست.")

    max_bytes = 8 * 1024 * 1024
    try:
        req = Request(
            target_url,
            headers={
                "User-Agent": "mysite-management-image-proxy/1.0",
                "Accept": "image/*,*/*;q=0.8",
            },
        )
        with urlopen(req, timeout=10) as response:
            content_type = str(response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            payload = response.read(max_bytes + 1)
    except Exception:
        frappe.throw("دریافت تصویر خارجی ممکن نشد.")

    if len(payload) > max_bytes:
        frappe.throw("حجم تصویر بیشتر از حد مجاز است.")

    if content_type and not content_type.startswith("image/"):
        inferred = _infer_image_content_type(target_url)
        if not inferred:
            frappe.throw("فایل مقصد تصویر نیست.")
        content_type = inferred
    if not content_type:
        content_type = _infer_image_content_type(target_url) or "application/octet-stream"

    filename = Path(parsed.path or "").name or "image"
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = payload
    frappe.local.response.type = "binary"
    frappe.local.response.headers["Content-Type"] = content_type
    frappe.local.response.headers["Cache-Control"] = "public, max-age=3600"


@frappe.whitelist()
def list_management_media_images(search=None, limit=80):
    _require_management_access("product.edit")
    limit = min(max(cint(limit or 80), 1), 200)
    search_term = str(search or "").strip().lower()

    rows = frappe.get_all(
        "File",
        filters={"is_folder": 0},
        fields=["name", "file_name", "file_url", "is_private", "folder", "modified"],
        order_by="modified desc",
        limit_page_length=600,
    )

    result = []
    for row in rows:
        file_url = str(row.get("file_url") or "").strip()
        if not file_url:
            continue
        file_url_lower = file_url.lower()
        file_name = str(row.get("file_name") or "")
        is_external = file_url_lower.startswith("http://") or file_url_lower.startswith("https://") or file_url_lower.startswith("//")
        if not _is_image_file_url(file_url) and not _is_image_file_url(file_name) and not is_external:
            continue
        hay = f"{file_name} {file_url}".lower()
        if search_term and search_term not in hay:
            continue
        result.append(
            {
                "name": row.get("name"),
                "file_name": row.get("file_name"),
                "file_url": file_url,
                "is_private": bool(row.get("is_private")),
                "folder": row.get("folder") or "",
                "modified": row.get("modified"),
            }
        )
        if len(result) >= limit:
            break

    return {"items": result, "count": len(result)}


def _is_image_file_url(file_url):
    raw = str(file_url or "").strip().lower().split("?")[0]
    return raw.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"))


def _normalize_media_url(file_url):
    return str(file_url or "").strip().replace("/private/files/", "/files/")


def _resolve_request_payload(payload=None):
    if isinstance(payload, (bytes, bytearray)):
        try:
            payload = payload.decode("utf-8")
        except Exception:
            payload = payload.decode("utf-8", errors="ignore")

    if isinstance(payload, str):
        payload_text = payload.strip()
        if not payload_text:
            payload = {}
        else:
            try:
                payload = frappe.parse_json(payload_text)
            except Exception:
                try:
                    payload = json.loads(payload_text)
                except Exception:
                    payload = {}

    if isinstance(payload, dict):
        return payload

    resolved = {}
    form_dict = getattr(frappe, "form_dict", None)
    if form_dict:
        try:
            form_payload = form_dict.as_dict() if hasattr(form_dict, "as_dict") else dict(form_dict)
        except Exception:
            form_payload = {}
        if isinstance(form_payload, dict):
            for key, value in form_payload.items():
                if key == "cmd":
                    continue
                resolved[key] = value

    raw_payload_text = ""
    if getattr(frappe, "request", None):
        try:
            raw_payload_text = frappe.request.get_data(as_text=True) or ""
        except Exception:
            try:
                raw_data = frappe.request.data
                if isinstance(raw_data, (bytes, bytearray)):
                    raw_payload_text = raw_data.decode("utf-8", errors="ignore")
                else:
                    raw_payload_text = str(raw_data or "")
            except Exception:
                raw_payload_text = ""

    raw_payload_text = str(raw_payload_text or "").strip()
    if raw_payload_text:
        try:
            raw_payload = frappe.parse_json(raw_payload_text)
        except Exception:
            try:
                raw_payload = json.loads(raw_payload_text)
            except Exception:
                raw_payload = {}
        if isinstance(raw_payload, dict):
            resolved.update(raw_payload)

    nested_payload = resolved.get("payload")
    if isinstance(nested_payload, (bytes, bytearray)):
        try:
            nested_payload = nested_payload.decode("utf-8")
        except Exception:
            nested_payload = nested_payload.decode("utf-8", errors="ignore")
    if isinstance(nested_payload, str):
        nested_text = nested_payload.strip()
        if nested_text:
            try:
                nested_payload = frappe.parse_json(nested_text)
            except Exception:
                try:
                    nested_payload = json.loads(nested_text)
                except Exception:
                    nested_payload = {}
        else:
            nested_payload = {}
    if isinstance(nested_payload, dict):
        resolved.update(nested_payload)

    return resolved if isinstance(resolved, dict) else {}


def _fetch_item_image_rows(item_codes):
    item_codes = [str(code or "").strip() for code in (item_codes or []) if str(code or "").strip()]
    if not item_codes or not frappe.db.exists("DocType", "File"):
        return {}

    file_fields = _available_fields("File")
    fields = ["name", "file_name", "file_url", "attached_to_name", "modified"]
    for optional in ["custom_tag", "custom_alt_text", "custom_yindex", "is_private"]:
        if optional in file_fields:
            fields.append(optional)

    order_by = "modified desc"
    if "custom_yindex" in file_fields:
        order_by = "custom_yindex asc, modified desc"

    rows = frappe.get_all(
        "File",
        filters={
            "is_folder": 0,
            "attached_to_doctype": "Item",
            "attached_to_name": ["in", item_codes],
        },
        fields=fields,
        order_by=order_by,
        limit_page_length=5000,
    )

    result = {}
    for row in rows:
        file_url = str(row.get("file_url") or "").strip()
        if not file_url or not _is_image_file_url(file_url):
            continue
        item_code = str(row.get("attached_to_name") or "").strip()
        if not item_code:
            continue
        result.setdefault(item_code, []).append(
            {
                "name": row.get("name"),
                "file_name": row.get("file_name") or "",
                "file_url": _normalize_media_url(file_url),
                "custom_tag": str(row.get("custom_tag") or "").strip(),
                "custom_alt_text": str(row.get("custom_alt_text") or "").strip(),
                "custom_yindex": flt(row.get("custom_yindex") or 0),
                "modified": row.get("modified"),
            }
        )
    return result


def _serialize_management_product_row(item_row, image_map, price_map=None, default_price_list="", feature_field=""):
    item_code = str(item_row.get("name") or "").strip()
    images = list(image_map.get(item_code) or [])
    price_rows = list((price_map or {}).get(item_code) or [])
    default_price_row = next((row for row in price_rows if str(row.get("price_list") or "").strip() == default_price_list), None)
    if not default_price_row and price_rows:
        default_price_row = price_rows[0]
    default_price_rate = flt((default_price_row or {}).get("rate") or 0)
    feature_rows = _normalize_management_feature_rows(item_row.get(feature_field)) if feature_field else []
    cover = next((img.get("file_url") for img in images if str(img.get("custom_tag") or "").strip() == "کاور"), "")
    primary_image = _normalize_media_url(item_row.get("image") or "") or cover or (images[0].get("file_url") if images else "")
    disabled = bool(cint(item_row.get("disabled") or 0))
    show_on_site = bool(cint(item_row.get("show_on_site") if item_row.get("show_on_site") is not None else 1))
    status_key = "active"
    status_label = "فعال"
    if disabled:
        status_key = "disabled"
        status_label = "غیرفعال"
    elif not show_on_site:
        status_key = "hidden"
        status_label = "مخفی در سایت"

    return {
        "item_code": item_code,
        "item_name": str(item_row.get("item_name") or "").strip(),
        "item_group": str(item_row.get("item_group") or "").strip(),
        "variant_of": str(item_row.get("variant_of") or "").strip(),
        "description": str(item_row.get("description") or "").strip(),
        "short_description": _clean_excerpt(item_row.get("description")),
        "image": primary_image,
        "show_on_site": show_on_site,
        "disabled": disabled,
        "status_key": status_key,
        "status_label": status_label,
        "modified": item_row.get("modified"),
        "images": images,
        "images_count": len(images),
        "feature_rows": feature_rows,
        "price_rows": price_rows,
        "prices_count": len(price_rows),
        "default_price_list": default_price_list or "",
        "default_price": default_price_rate,
        "default_price_toman": _to_toman(default_price_rate),
        "default_price_currency": str((default_price_row or {}).get("currency") or "IRR").strip() or "IRR",
    }


def _get_management_product_snapshot(item_code):
    item_code = str(item_code or "").strip()
    if not item_code or not frappe.db.exists("Item", item_code):
        return None

    default_price_list = _default_price_list() or ""
    item_fields = _available_fields("Item")
    feature_field = MANAGEMENT_PRODUCT_FEATURES_FIELD if MANAGEMENT_PRODUCT_FEATURES_FIELD in item_fields else ""
    fields = ["name", "item_name", "item_group", "description", "image", "modified", "variant_of"]
    for optional in ["show_on_site", "disabled"]:
        if optional in item_fields:
            fields.append(optional)
    if feature_field:
        fields.append(feature_field)

    row = frappe.get_all(
        "Item",
        filters={"name": item_code},
        fields=fields,
        limit_page_length=1,
    )
    if not row:
        return None
    image_map = _fetch_item_image_rows([item_code])
    price_map = _fetch_item_price_rows([item_code])
    return _serialize_management_product_row(
        row[0],
        image_map,
        price_map=price_map,
        default_price_list=default_price_list,
        feature_field=feature_field,
    )


@frappe.whitelist()
def get_management_products(search=None, item_group=None, status="all", limit=60, offset=0):
    _require_management_access("product.edit")

    if not frappe.db.exists("DocType", "Item"):
        return {"items": [], "total": 0, "limit": 0, "offset": 0, "item_groups": [], "price_lists": [], "default_price_list": ""}

    limit = min(max(cint(limit or 60), 1), 300)
    offset = max(cint(offset or 0), 0)
    search_term = str(search or "").strip()
    item_group = str(item_group or "").strip()
    status = str(status or "all").strip().lower()
    default_price_list = _default_price_list() or ""
    item_fields = _available_fields("Item")
    feature_field = MANAGEMENT_PRODUCT_FEATURES_FIELD if MANAGEMENT_PRODUCT_FEATURES_FIELD in item_fields else ""

    where = ["i.is_stock_item = 1"]
    params = {"limit": limit, "offset": offset}

    if item_group:
        where.append("i.item_group = %(item_group)s")
        params["item_group"] = item_group

    if status == "active":
        where.append("IFNULL(i.disabled, 0) = 0 AND IFNULL(i.show_on_site, 1) = 1")
    elif status == "hidden":
        where.append("IFNULL(i.disabled, 0) = 0 AND IFNULL(i.show_on_site, 1) = 0")
    elif status == "disabled":
        where.append("IFNULL(i.disabled, 0) = 1")

    if search_term:
        params["query"] = f"%{search_term}%"
        where.append(
            "(i.name LIKE %(query)s OR i.item_code LIKE %(query)s OR i.item_name LIKE %(query)s OR IFNULL(i.variant_of, '') LIKE %(query)s)"
        )

    where_sql = " AND ".join(where)
    feature_select_sql = f", i.{feature_field} as {feature_field}" if feature_field else ""
    rows = frappe.db.sql(
        f"""
        SELECT
            i.name,
            i.item_name,
            i.item_group,
            i.variant_of,
            i.description,
            i.image,
            i.show_on_site,
            i.disabled,
            i.modified
            {feature_select_sql}
        FROM `tabItem` i
        WHERE {where_sql}
        ORDER BY i.modified DESC
        LIMIT %(limit)s OFFSET %(offset)s
        """,
        params,
        as_dict=True,
    )
    count_rows = frappe.db.sql(
        f"""
        SELECT COUNT(*) AS total
        FROM `tabItem` i
        WHERE {where_sql}
        """,
        params,
        as_dict=True,
    )
    total = cint((count_rows or [{}])[0].get("total") or 0)

    item_codes = [str(row.get("name") or "").strip() for row in rows if str(row.get("name") or "").strip()]
    image_map = _fetch_item_image_rows(item_codes)
    price_map = _fetch_item_price_rows(item_codes)
    items = [
        _serialize_management_product_row(
            row,
            image_map,
            price_map=price_map,
            default_price_list=default_price_list,
            feature_field=feature_field,
        )
        for row in rows
    ]

    groups = frappe.db.sql(
        """
        SELECT item_group, COUNT(*) AS count
        FROM `tabItem`
        WHERE is_stock_item = 1
          AND IFNULL(item_group, '') != ''
        GROUP BY item_group
        ORDER BY item_group ASC
        """,
        as_dict=True,
    )

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "item_groups": [{"item_group": row.get("item_group"), "count": cint(row.get("count") or 0)} for row in groups],
        "price_lists": _list_management_price_lists(default_price_list=default_price_list),
        "default_price_list": default_price_list,
    }


@frappe.whitelist()
def save_management_product(item_code=None, payload=None):
    _require_management_access("product.edit")
    payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(payload)
    item_code = str(item_code or payload.get("item_code") or payload.get("name") or "").strip()
    if not item_code or not frappe.db.exists("Item", item_code):
        frappe.throw("محصول معتبر انتخاب نشده است.")

    if not workflow_bypass and should_enforce("product"):
        return _workflow_create_response(
            module_key="product",
            target_type="product_update",
            target_key=item_code,
            payload=payload,
            current_snapshot=_get_management_product_snapshot(item_code) or {},
            source_endpoint="save_management_product",
        )

    if "feature_rows" in payload:
        ensure_management_product_custom_fields()

    item_fields = _available_fields("Item")
    feature_field = MANAGEMENT_PRODUCT_FEATURES_FIELD if MANAGEMENT_PRODUCT_FEATURES_FIELD in item_fields else ""
    doc = frappe.get_doc("Item", item_code)

    if "item_name" in payload and "item_name" in item_fields:
        doc.item_name = str(payload.get("item_name") or "").strip()
    if "item_group" in payload and "item_group" in item_fields:
        doc.item_group = str(payload.get("item_group") or "").strip()
    if "description" in payload and "description" in item_fields:
        doc.description = str(payload.get("description") or "").strip()
    if "show_on_site" in payload and "show_on_site" in item_fields:
        doc.show_on_site = 1 if _to_bool(payload.get("show_on_site"), True) else 0
    if "disabled" in payload and "disabled" in item_fields:
        doc.disabled = 1 if _to_bool(payload.get("disabled"), False) else 0
    if "image" in payload and "image" in item_fields:
        doc.image = _normalize_media_url(payload.get("image")) if payload.get("image") else ""
    if "feature_rows" in payload and feature_field:
        feature_rows = _normalize_management_feature_rows(payload.get("feature_rows"))
        setattr(doc, feature_field, json.dumps(feature_rows, ensure_ascii=False) if feature_rows else "")

    doc.save(ignore_permissions=True)
    if "price_rows" in payload or "deleted_price_names" in payload:
        _upsert_management_item_prices(
            item_code=item_code,
            raw_price_rows=payload.get("price_rows"),
            raw_deleted_names=payload.get("deleted_price_names"),
        )
    frappe.clear_cache(doctype="Item")
    frappe.db.commit()

    response = {"ok": True, "product": _get_management_product_snapshot(item_code)}
    _workflow_shadow_record(
        module_key="product",
        target_type="product_update",
        target_key=item_code,
        payload=payload,
        current_snapshot={"item_code": item_code},
        source_endpoint="save_management_product",
        publish_result=response,
    )
    return response


@frappe.whitelist()
def attach_management_product_image(item_code=None, file_url=None, is_primary=False, tag=None, alt_text=None, yindex=None, payload=None):
    _require_management_access("product.edit")
    payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(payload)
    item_code = str(item_code or payload.get("item_code") or payload.get("name") or "").strip()
    file_url = _normalize_media_url(file_url or payload.get("file_url"))
    is_primary = _to_bool(payload.get("is_primary") if "is_primary" in payload else is_primary, False)
    tag = str(payload.get("tag") if "tag" in payload else tag or "").strip()
    alt_text = str(payload.get("alt_text") if "alt_text" in payload else alt_text or "").strip()
    yindex = payload.get("yindex") if "yindex" in payload else yindex

    if not item_code or not frappe.db.exists("Item", item_code):
        frappe.throw("محصول معتبر انتخاب نشده است.")
    if not file_url:
        frappe.throw("نشانی تصویر ارسال نشده است.")
    if not _is_image_file_url(file_url):
        frappe.throw("فایل انتخاب‌شده تصویر معتبر نیست.")

    if not workflow_bypass and should_enforce("product"):
        return _workflow_create_response(
            module_key="product",
            target_type="product_media_attach",
            target_key=item_code,
            payload={
                "item_code": item_code,
                "file_url": file_url,
                "is_primary": is_primary,
                "tag": tag,
                "alt_text": alt_text,
                "yindex": yindex,
            },
            current_snapshot=_get_management_product_snapshot(item_code) or {},
            source_endpoint="attach_management_product_image",
        )

    existing = frappe.get_all(
        "File",
        filters={
            "is_folder": 0,
            "attached_to_doctype": "Item",
            "attached_to_name": item_code,
            "file_url": file_url,
        },
        fields=["name"],
        limit_page_length=1,
    )

    if existing:
        file_doc = frappe.get_doc("File", existing[0].get("name"))
    else:
        source = frappe.get_all(
            "File",
            filters={"is_folder": 0, "file_url": file_url},
            fields=["file_name", "is_private", "folder", "file_type"],
            order_by="modified desc",
            limit_page_length=1,
        )
        source_row = source[0] if source else {}
        fallback_name = Path(urlsplit(file_url).path).name or f"{item_code}-image"
        file_doc = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": source_row.get("file_name") or fallback_name,
                "file_url": file_url,
                "is_private": cint(source_row.get("is_private") or 0),
                "folder": source_row.get("folder") or "Home/Attachments",
                "attached_to_doctype": "Item",
                "attached_to_name": item_code,
            }
        )
        file_doc.insert(ignore_permissions=True)

    file_fields = _available_fields("File")
    touched = False
    if tag and "custom_tag" in file_fields:
        file_doc.custom_tag = tag
        touched = True
    if alt_text and "custom_alt_text" in file_fields:
        file_doc.custom_alt_text = alt_text
        touched = True
    if yindex is not None and "custom_yindex" in file_fields:
        file_doc.custom_yindex = flt(yindex or 0)
        touched = True
    if touched:
        file_doc.save(ignore_permissions=True)

    if is_primary:
        item_doc = frappe.get_doc("Item", item_code)
        if "image" in _available_fields("Item"):
            item_doc.image = file_url
            item_doc.save(ignore_permissions=True)

    frappe.clear_cache(doctype="Item")
    frappe.db.commit()
    response = {"ok": True, "product": _get_management_product_snapshot(item_code)}
    _workflow_shadow_record(
        module_key="product",
        target_type="product_media_attach",
        target_key=item_code,
        payload={
            "item_code": item_code,
            "file_url": file_url,
            "is_primary": is_primary,
            "tag": tag,
            "alt_text": alt_text,
            "yindex": yindex,
        },
        current_snapshot={"item_code": item_code},
        source_endpoint="attach_management_product_image",
        publish_result=response,
    )
    return response


@frappe.whitelist()
def remove_management_product_image(item_code=None, file_name=None, file_url=None, payload=None):
    _require_management_access("product.edit")
    payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(payload)
    item_code = str(item_code or payload.get("item_code") or payload.get("name") or "").strip()
    file_name = str(file_name or payload.get("file_name") or "").strip()
    file_url = _normalize_media_url(file_url or payload.get("file_url"))

    if not item_code or not frappe.db.exists("Item", item_code):
        frappe.throw("محصول معتبر انتخاب نشده است.")

    if not workflow_bypass and should_enforce("product"):
        return _workflow_create_response(
            module_key="product",
            target_type="product_media_remove",
            target_key=item_code,
            payload={
                "item_code": item_code,
                "file_name": file_name,
                "file_url": file_url,
            },
            current_snapshot=_get_management_product_snapshot(item_code) or {},
            source_endpoint="remove_management_product_image",
        )

    filters = {
        "is_folder": 0,
        "attached_to_doctype": "Item",
        "attached_to_name": item_code,
    }
    if file_name:
        filters["name"] = file_name
    elif file_url:
        filters["file_url"] = file_url
    else:
        frappe.throw("تصویر موردنظر برای حذف مشخص نشده است.")

    rows = frappe.get_all("File", filters=filters, fields=["name", "file_url"], limit_page_length=1)
    if not rows:
        frappe.throw("تصویر انتخاب‌شده پیدا نشد.")

    target = rows[0]
    deleted_url = _normalize_media_url(target.get("file_url"))
    frappe.delete_doc("File", target.get("name"), ignore_permissions=True, force=1)

    item_doc = frappe.get_doc("Item", item_code)
    if _normalize_media_url(item_doc.image) == deleted_url:
        remaining = frappe.get_all(
            "File",
            filters={
                "is_folder": 0,
                "attached_to_doctype": "Item",
                "attached_to_name": item_code,
            },
            fields=["file_url"],
            order_by="modified desc",
            limit_page_length=20,
        )
        next_image = ""
        for row in remaining:
            candidate = _normalize_media_url(row.get("file_url"))
            if _is_image_file_url(candidate):
                next_image = candidate
                break
        item_doc.image = next_image
        item_doc.save(ignore_permissions=True)

    frappe.clear_cache(doctype="Item")
    frappe.db.commit()
    response = {"ok": True, "product": _get_management_product_snapshot(item_code)}
    _workflow_shadow_record(
        module_key="product",
        target_type="product_media_remove",
        target_key=item_code,
        payload={
            "item_code": item_code,
            "file_name": file_name,
            "file_url": file_url,
        },
        current_snapshot={"item_code": item_code},
        source_endpoint="remove_management_product_image",
        publish_result=response,
    )
    return response


@frappe.whitelist()
def set_management_product_primary_image(item_code=None, file_url=None, payload=None):
    _require_management_access("product.edit")
    payload = _resolve_request_payload(payload=payload)
    workflow_bypass = _workflow_bypass_enabled(payload)

    item_code = str(item_code or payload.get("item_code") or payload.get("name") or "").strip()
    file_url = _normalize_media_url(file_url or payload.get("file_url"))

    if not item_code or not frappe.db.exists("Item", item_code):
        frappe.throw("محصول معتبر انتخاب نشده است.")
    if not file_url:
        frappe.throw("تصویر انتخاب نشده است.")
    if not _is_image_file_url(file_url):
        frappe.throw("تصویر انتخاب‌شده معتبر نیست.")

    if not workflow_bypass and should_enforce("product"):
        return _workflow_create_response(
            module_key="product",
            target_type="product_media_primary",
            target_key=item_code,
            payload={"item_code": item_code, "file_url": file_url},
            current_snapshot=_get_management_product_snapshot(item_code) or {},
            source_endpoint="set_management_product_primary_image",
        )

    item_doc = frappe.get_doc("Item", item_code)
    if "image" in _available_fields("Item"):
        item_doc.image = file_url
        item_doc.save(ignore_permissions=True)

    frappe.clear_cache(doctype="Item")
    frappe.db.commit()
    response = {"ok": True, "product": _get_management_product_snapshot(item_code)}
    _workflow_shadow_record(
        module_key="product",
        target_type="product_media_primary",
        target_key=item_code,
        payload={"item_code": item_code, "file_url": file_url},
        current_snapshot={"item_code": item_code},
        source_endpoint="set_management_product_primary_image",
        publish_result=response,
    )
    return response


@frappe.whitelist(allow_guest=True)
def can_access_management():
    ctx = permission_context()
    return {
        "allowed": can_access_management_permission(),
        "roles": sorted(ctx.roles),
        "capabilities": sorted(ctx.capabilities),
    }


def _serialize_change_request_doc(doc):
    return {
        "name": doc.name,
        "module_key": doc.module_key,
        "target_type": doc.target_type,
        "target_key": doc.target_key,
        "state": doc.state,
        "requested_by": doc.requested_by,
        "requested_at": doc.requested_at,
        "reviewed_by": doc.reviewed_by,
        "reviewed_at": doc.reviewed_at,
        "approved_by": doc.approved_by,
        "approved_at": doc.approved_at,
        "published_by": doc.published_by,
        "published_at": doc.published_at,
        "latest_comment": doc.latest_comment,
        "source_endpoint": doc.source_endpoint,
        "is_shadow_record": cint(doc.is_shadow_record or 0),
        "error_message": doc.error_message or "",
        "request_payload_json": doc.request_payload_json or "{}",
        "current_snapshot_json": doc.current_snapshot_json or "{}",
        "diff_summary_json": doc.diff_summary_json or "{}",
        "publish_result_json": doc.publish_result_json or "{}",
        "events": [
            {
                "action": row.action,
                "from_state": row.from_state,
                "to_state": row.to_state,
                "actor": row.actor,
                "comment": row.comment,
                "action_at": row.action_at,
            }
            for row in (doc.get("events") or [])
        ],
    }


def _apply_change_request_publish(doc):
    payload = parse_request_payload(doc)
    payload["__workflow_bypass"] = 1
    target_type = str(doc.target_type or "").strip()
    target_key = str(doc.target_key or "").strip()

    if target_type == "page_config":
        return save_management_page_config(route=target_key or payload.get("route"), payload=payload)
    if target_type == "page_content_override":
        return save_management_page_content_overrides(route=target_key or payload.get("route"), payload=payload)
    if target_type == "page_visual_override":
        return save_management_page_visual_overrides(route=target_key or payload.get("route"), payload=payload)
    if target_type == "visual_source":
        return save_management_visual_editor_changes(
            route=target_key or payload.get("route"),
            items=payload.get("items"),
            raw_css=payload.get("raw_css"),
            full_source=payload.get("full_source"),
            note=payload.get("note"),
            target_file=payload.get("target_file"),
            payload=payload,
        )
    if target_type == "blog_post":
        return save_management_blog_post(name=payload.get("name"), payload=payload)
    if target_type == "blog_delete":
        return delete_management_blog_post(name=target_key or payload.get("name"), payload=payload)
    if target_type == "product_update":
        return save_management_product(item_code=target_key or payload.get("item_code"), payload=payload)
    if target_type == "product_media_attach":
        return attach_management_product_image(
            item_code=target_key or payload.get("item_code"),
            file_url=payload.get("file_url"),
            is_primary=payload.get("is_primary"),
            tag=payload.get("tag"),
            alt_text=payload.get("alt_text"),
            yindex=payload.get("yindex"),
            payload=payload,
        )
    if target_type == "product_media_remove":
        return remove_management_product_image(
            item_code=target_key or payload.get("item_code"),
            file_name=payload.get("file_name"),
            file_url=payload.get("file_url"),
            payload=payload,
        )
    if target_type == "product_media_primary":
        return set_management_product_primary_image(
            item_code=target_key or payload.get("item_code"),
            file_url=payload.get("file_url"),
            payload=payload,
        )
    frappe.throw("نوع هدف برای انتشار پشتیبانی نمی‌شود.")


@frappe.whitelist()
def create_management_change_request(target_type=None, target_key=None, module_key=None, payload=None, source_endpoint=None):
    request_payload = _resolve_request_payload(payload=payload)
    target_type = str(target_type or request_payload.get("target_type") or "").strip()
    target_key = str(target_key or request_payload.get("target_key") or request_payload.get("route") or request_payload.get("name") or "").strip()
    module_key = str(module_key or request_payload.get("module_key") or module_for_target_type(target_type)).strip()
    source_endpoint = str(source_endpoint or request_payload.get("source_endpoint") or "").strip()

    if not target_type:
        frappe.throw("target_type الزامی است.")
    _require_management_access(default_capability_for_target(target_type, "create_draft"))

    info = create_change_request(
        module_key=module_key,
        target_type=target_type,
        target_key=target_key,
        request_payload=request_payload.get("request_payload") or request_payload,
        current_snapshot=request_payload.get("current_snapshot") or {},
        diff_summary=request_payload.get("diff_summary") or {},
        source_endpoint=source_endpoint,
        initial_state="Draft",
        is_shadow_record=False,
    )
    audit_log_event(
        module_key=module_key,
        action_key="workflow.create_request",
        target_type=target_type,
        target_key=target_key,
        change_request=info.get("name") or "",
        result="success",
        details={"source_endpoint": source_endpoint},
    )
    return {"ok": True, "change_request": info.get("name"), "state": info.get("state")}


@frappe.whitelist()
def list_management_change_requests(module_key=None, state=None, limit=50, offset=0):
    _require_management_access("management.access")
    module_key = str(module_key or "").strip()
    state = str(state or "").strip()
    rows = list_change_requests(module_key=module_key or None, state=state or None, limit=limit, offset=offset)

    if not is_super_admin():
        allowed_modules = set()
        if has_capability("content.edit") or has_capability("content.review") or has_capability("content.publish"):
            allowed_modules.add("content")
        if has_capability("product.edit") or has_capability("product.review") or has_capability("product.publish"):
            allowed_modules.add("product")
        rows["items"] = [row for row in (rows.get("items") or []) if str(row.get("module_key") or "") in allowed_modules]
        rows["total"] = len(rows["items"])
    return rows


@frappe.whitelist()
def get_management_change_request_detail(name=None):
    _require_management_access("management.access")
    doc = get_change_request(str(name or frappe.form_dict.get("name") or "").strip())
    if not doc:
        return {"change_request": None}

    required = _module_action_capability(doc.module_key, "edit")
    _require_management_access(required)
    return {"change_request": _serialize_change_request_doc(doc)}


@frappe.whitelist()
def transition_management_change_request(name=None, action=None, comment=None, payload=None):
    request_payload = _resolve_request_payload(payload=payload)
    name = str(name or request_payload.get("name") or "").strip()
    action = str(action or request_payload.get("action") or "").strip()
    comment = str(comment or request_payload.get("comment") or "").strip()

    if not name:
        frappe.throw("نام درخواست تغییر الزامی است.")

    doc = get_change_request(name)
    if not doc:
        frappe.throw("درخواست تغییر پیدا نشد.")

    required = _module_action_capability(doc.module_key, "review" if action in {"approve", "reject", "return_to_draft"} else "publish" if action == "publish" else "edit")
    _require_management_access(required)

    try:
        updated = transition_change_request(name, action, comment=comment)
    except Exception:
        audit_log_event(
            module_key=doc.module_key,
            action_key=f"workflow.{action}",
            target_type=doc.target_type,
            target_key=doc.target_key,
            change_request=doc.name,
            result="failed",
            details={"comment": comment},
        )
        raise

    publish_result = None
    if action == "publish":
        try:
            publish_result = _apply_change_request_publish(updated)
            updated.publish_result_json = json.dumps(publish_result or {}, ensure_ascii=False)
            updated.error_message = ""
            updated.save(ignore_permissions=True)
        except Exception as exc:
            updated.error_message = str(exc)
            updated.save(ignore_permissions=True)
            audit_log_event(
                module_key=updated.module_key,
                action_key="workflow.publish",
                target_type=updated.target_type,
                target_key=updated.target_key,
                change_request=updated.name,
                result="failed",
                details={"error": str(exc)},
            )
            raise

    frappe.db.commit()
    audit_log_event(
        module_key=updated.module_key,
        action_key=f"workflow.{action}",
        target_type=updated.target_type,
        target_key=updated.target_key,
        change_request=updated.name,
        result="success",
        details={"state": updated.state},
    )
    return {
        "ok": True,
        "change_request": _serialize_change_request_doc(updated),
        "publish_result": publish_result,
    }


@frappe.whitelist()
def publish_management_change_request(name=None, payload=None):
    request_payload = _resolve_request_payload(payload=payload)
    return transition_management_change_request(name=name or request_payload.get("name"), action="publish", payload=request_payload)


@frappe.whitelist()
def get_management_audit_logs(module_key=None, action_key=None, target_type=None, target_key=None, result=None, limit=100, offset=0):
    allowed_modules = _audit_allowed_modules()
    if allowed_modules is not None and not allowed_modules:
        _require_management_access("audit.view")
    if not frappe.db.exists("DocType", "MS Management Audit Log"):
        return {"items": [], "total": 0, "limit": 0, "offset": 0}

    filters = {}
    if module_key:
        requested_module = str(module_key).strip()
        if allowed_modules is not None and requested_module not in allowed_modules:
            return {"items": [], "total": 0, "limit": 0, "offset": 0}
        filters["module_key"] = requested_module
    elif allowed_modules is not None:
        filters["module_key"] = ["in", sorted(allowed_modules)]
    if action_key:
        filters["action_key"] = str(action_key).strip()
    if target_type:
        filters["target_type"] = str(target_type).strip()
    if target_key:
        filters["target_key"] = str(target_key).strip()
    if result:
        filters["result"] = str(result).strip()

    limit = min(max(cint(limit or 100), 1), 500)
    offset = max(cint(offset or 0), 0)
    rows = frappe.get_all(
        "MS Management Audit Log",
        filters=filters,
        fields=[
            "name",
            "module_key",
            "action_key",
            "target_type",
            "target_key",
            "change_request",
            "actor",
            "actor_roles",
            "result",
            "request_id",
            "ip_address",
            "user_agent",
            "details_json",
            "occurred_at",
        ],
        order_by="occurred_at desc",
        start=offset,
        limit_page_length=limit,
    )
    total = frappe.db.count("MS Management Audit Log", filters=filters)
    return {"items": rows, "total": total, "limit": limit, "offset": offset}


@frappe.whitelist()
def get_management_audit_timeline(target_type=None, target_key=None, limit=150):
    allowed_modules = _audit_allowed_modules()
    if allowed_modules is not None and not allowed_modules:
        _require_management_access("audit.view")
    if not frappe.db.exists("DocType", "MS Management Audit Log"):
        return {"items": [], "count": 0}
    target_type = str(target_type or frappe.form_dict.get("target_type") or "").strip()
    target_key = str(target_key or frappe.form_dict.get("target_key") or "").strip()
    if not target_type or not target_key:
        frappe.throw("target_type و target_key الزامی است.")
    limit = min(max(cint(limit or 150), 1), 500)
    rows = frappe.get_all(
        "MS Management Audit Log",
        filters={"target_type": target_type, "target_key": target_key},
        fields=[
            "name",
            "module_key",
            "action_key",
            "change_request",
            "actor",
            "result",
            "details_json",
            "occurred_at",
        ],
        order_by="occurred_at desc",
        limit_page_length=limit,
    )
    if allowed_modules is not None:
        rows = [row for row in rows if str(row.get("module_key") or "") in allowed_modules]
    return {"items": rows, "count": len(rows)}


@frappe.whitelist()
def get_management_panel_data():
    _require_management_access()

    app_root = Path(frappe.get_app_path("mysite")).parent
    frontend_root = app_root / "frontend" / "src"
    pages_dir = frontend_root / "pages"
    components_dir = frontend_root / "components"
    app_vue_file = frontend_root / "App.vue"

    frontend_pages = _scan_vue_files(pages_dir, app_root)
    frontend_components = _scan_vue_files(components_dir, app_root)
    frontend_routes = _extract_frontend_routes(app_vue_file, app_root)
    component_usage_map = _collect_frontend_component_usage(frontend_routes, app_root)
    enriched_components = []
    for row in frontend_components:
        component_file = str(row.get("file") or "").strip()
        usage_routes = component_usage_map.get(component_file, [])
        enriched_components.append(
            {
                **row,
                "routes": usage_routes,
                "usage_count": len(usage_routes),
                "primary_route": usage_routes[0] if usage_routes else "",
            }
        )
    website_pages = _scan_website_pages(app_root)
    page_overrides = _load_management_page_overrides()
    clean_overrides = {}
    for raw_route, raw_payload in (page_overrides or {}).items():
        route_key = _normalize_tracked_path(raw_route)
        if not route_key or not route_key.startswith("/mysite"):
            continue
        clean_override = _clean_page_override_payload(raw_payload if isinstance(raw_payload, dict) else {})
        clean_override["status_label"] = "منتشر شده" if clean_override.get("status_key") == "published" else "غیرفعال"
        content_rows = clean_override.get("content_overrides") or []
        clean_override["content_override_count"] = len(
            [
                row
                for row in content_rows
                if _normalize_content_text(row.get("replacement_text")) and _normalize_content_text(row.get("replacement_text")) != _normalize_content_text(row.get("source_text"))
            ]
        )
        visual_rows = clean_override.get("visual_overrides") or []
        clean_override["visual_override_count"] = len(
            [
                row
                for row in visual_rows
                if (
                    (isinstance(row.get("styles"), dict) and row.get("styles"))
                    or _to_bool(row.get("apply_text"), False)
                    or _to_bool(row.get("apply_html"), False)
                )
            ]
        )
        clean_override.pop("content_overrides", None)
        clean_override.pop("visual_overrides", None)
        clean_overrides[route_key] = clean_override

    for row in website_pages:
        route = row.get("route")
        if not route:
            continue
        override = clean_overrides.get(route) or {}
        if override.get("title"):
            row["title"] = override.get("title")
        if override.get("meta_description") is not None:
            row["meta_description"] = override.get("meta_description") or ""
        if override.get("canonical_url") is not None:
            row["canonical_url"] = override.get("canonical_url") or ""
        if override.get("meta_image") is not None:
            row["meta_image"] = override.get("meta_image") or ""
        if "noindex" in override:
            row["noindex"] = bool(override.get("noindex"))
            row["robots"] = "noindex,nofollow" if row["noindex"] else "index,follow"

    whitelisted_methods = _scan_whitelisted_methods(app_root)
    traffic = _collect_page_traffic(days=30, limit=20)
    url_settings = _build_url_settings(frontend_routes, website_pages, traffic.get("route_stats") or [])

    return {
        "meta": {
            "generated_at": now_datetime().isoformat(),
            "site": frappe.local.site,
            "app": "mysite",
            "user": frappe.session.user,
            "roles": sorted(_management_roles()),
            "capabilities": sorted(permission_context().capabilities),
        },
        "counts": _collect_management_counts(),
        "frontend": {
            "pages": frontend_pages,
            "components": enriched_components,
            "routes": frontend_routes,
        },
        "backend": {
            "website_pages": website_pages,
            "whitelisted_methods": whitelisted_methods,
            "page_overrides": clean_overrides,
        },
        "traffic": traffic,
        "url_settings": url_settings,
        "totals": {
            "frontend_pages": len(frontend_pages),
            "frontend_components": len(frontend_components),
            "frontend_routes": len(frontend_routes),
            "website_pages": len(website_pages),
            "api_methods": len(whitelisted_methods),
            "tracked_pages_30d": len(traffic.get("route_stats") or []),
            "tracked_views_30d": cint((traffic.get("totals") or {}).get("views") or 0),
        },
    }


def run_setup_script():
    print("Creating custom fields and DocTypes...")
    ensure_blog_custom_fields()

    print("Creating sample dealer data...")
    dealers = [
        {"dealer_name": "نمایندگی مرکزی تهران", "province": "تهران", "city": "تهران", "phone": "021-88776655", "work_hours": "۹ تا ۱۸", "badge": "Gold"},
        {"dealer_name": "نمایندگی اصفهان", "province": "اصفهان", "city": "اصفهان", "phone": "031-32123456", "work_hours": "۹ تا ۱۷", "badge": "Gold"},
        {"dealer_name": "نمایندگی شیراز", "province": "فارس", "city": "شیراز", "phone": "071-32567890", "work_hours": "۹ تا ۱۸", "badge": "Silver"},
    ]

    for dealer in dealers:
        if not frappe.db.exists("MySite Dealer", dealer["dealer_name"]):
            doc = frappe.get_doc({"doctype": "MySite Dealer", **dealer})
            doc.insert()


def cleanup_unwanted_fields():
    print("Cleaning up unwanted Item custom fields...")
    fieldnames = [
        "custom_technical_shape",
        "custom_technical_length",
        "custom_technical_width",
        "custom_technical_height",
        "custom_technical_diameter",
    ]
    for fieldname in fieldnames:
        frappe.db.sql(f"DELETE FROM `tabCustom Field` WHERE dt = 'Item' AND fieldname = '{fieldname}'")
        try:
            frappe.db.sql(f"ALTER TABLE `tabItem` DROP COLUMN `{fieldname}`")
        except Exception:
            pass
    frappe.clear_cache(doctype="Item")
    frappe.db.commit()
    print("Cleanup complete.")


def _clean_support_message(value):
    text = frappe.utils.strip_html(str(value or "")).strip()
    return " ".join(text.split())


def _support_guard(include_phase2=False):
    from mysite import support_service

    return support_service.ensure_support_runtime_ready(include_phase2=include_phase2, throw=True)


@frappe.whitelist()
def get_support_runtime_health(include_phase2=0):
    _require_management_access("support.manage")
    from mysite import support_service

    return support_service.support_runtime_health(include_phase2=_to_bool(include_phase2, False))


@frappe.whitelist()
def get_management_support_dashboard(from_date=None, to_date=None):
    _require_management_access("support.manage")
    _support_guard()
    from mysite import support_service

    return support_service.management_dashboard_payload(from_date=from_date, to_date=to_date)


@frappe.whitelist()
def get_management_support_tickets(page=1, page_size=20, status=None, priority=None, search=None, customer=None):
    _require_management_access("support.manage")
    _support_guard()
    from mysite import support_service

    return support_service.list_tickets_for_management(
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        search=search,
        customer=customer,
    )


@frappe.whitelist()
def get_management_support_ticket_detail(name=None):
    _require_management_access("support.manage")
    _support_guard()
    from mysite import support_service

    if not name:
        frappe.throw("نام تیکت الزامی است.")
    return support_service.get_ticket_detail(name, for_management=True)


@frappe.whitelist()
def reply_management_support_ticket(name=None, message=None, status_after_reply=None, notify=True, payload=None):
    _require_management_access("support.manage")
    _support_guard()
    from mysite import support_service

    payload = _resolve_request_payload(payload=payload)
    ticket_name = str(name or payload.get("name") or "").strip()
    reply_message = payload.get("message", message)
    status_key = str(status_after_reply or payload.get("status_after_reply") or "").strip() or None
    send_email = _to_bool(payload.get("notify", notify), True)
    to = payload.get("to")
    cc = payload.get("cc")
    bcc = payload.get("bcc")

    if not ticket_name:
        frappe.throw("نام تیکت الزامی است.")

    result = support_service.add_agent_reply(
        ticket_name,
        reply_message,
        status_after_reply=status_key,
        to=to,
        cc=cc,
        bcc=bcc,
        send_email=send_email,
    )
    audit_log_event(
        module_key="support",
        action_key="reply_management_support_ticket",
        target_type="support_ticket",
        target_key=ticket_name,
        result="success",
        details={"status_after_reply": status_key},
    )
    return result


@frappe.whitelist()
def update_management_support_ticket_status(name=None, status=None, resolution_details=None, payload=None):
    _require_management_access("support.manage")
    _support_guard()
    from mysite import support_service

    payload = _resolve_request_payload(payload=payload)
    ticket_name = str(name or payload.get("name") or "").strip()
    next_status = str(status or payload.get("status") or "").strip()
    resolution_text = payload.get("resolution_details", resolution_details)

    if not ticket_name or not frappe.db.exists("MS Support Ticket", ticket_name):
        frappe.throw("تیکت انتخاب‌شده معتبر نیست.")
    if not next_status or not frappe.db.exists("MS Support Ticket Status", next_status):
        frappe.throw("وضعیت انتخاب‌شده معتبر نیست.")

    ticket_doc = frappe.get_doc("MS Support Ticket", ticket_name)
    ticket_doc.status = next_status
    if resolution_text is not None:
        ticket_doc.resolution_details = str(resolution_text or "").strip()
    ticket_doc.save(ignore_permissions=True)
    support_service.create_ticket_activity(ticket_doc.name, f"تغییر وضعیت به {next_status}")
    support_service.run_support_automation(
        ticket_doc,
        trigger_event="Status Changed",
        context={"status": next_status},
    )
    next_status_label = (
        frappe.db.get_value("MS Support Ticket Status", next_status, "label_agent")
        if frappe.db.exists("MS Support Ticket Status", next_status)
        else ""
    ) or next_status
    support_service.notify_users(
        [ticket_doc.raised_by],
        event_key="ticket_status_changed",
        title=f"وضعیت تیکت {ticket_doc.name} تغییر کرد",
        body=f"وضعیت جدید: {next_status_label}",
        ticket_name=ticket_doc.name,
        route=f"/dashboard?tab=support_tickets&ticket={ticket_doc.name}",
    )
    frappe.db.commit()
    audit_log_event(
        module_key="support",
        action_key="update_management_support_ticket_status",
        target_type="support_ticket",
        target_key=ticket_doc.name,
        result="success",
        details={"status": ticket_doc.status},
    )

    return {"ok": True, "ticket": ticket_doc.name, "status": ticket_doc.status}


@frappe.whitelist()
def get_management_support_macros():
    _require_management_access("support.manage")
    _support_guard(include_phase2=True)
    from mysite import support_service

    return {"items": support_service.list_macros()}


@frappe.whitelist()
def apply_management_support_macro(name=None, macro=None, notify=True, payload=None):
    _require_management_access("support.manage")
    _support_guard(include_phase2=True)
    from mysite import support_service

    payload = _resolve_request_payload(payload=payload)
    ticket_name = str(name or payload.get("name") or "").strip()
    macro_name = str(macro or payload.get("macro") or "").strip()
    if not ticket_name:
        frappe.throw("نام تیکت الزامی است.")
    if not macro_name:
        frappe.throw("نام ماکرو الزامی است.")

    result = support_service.apply_macro(ticket_name=ticket_name, macro_name=macro_name, notify=notify)
    audit_log_event(
        module_key="support",
        action_key="apply_management_support_macro",
        target_type="support_ticket",
        target_key=ticket_name,
        result="success",
        details={"macro": macro_name},
    )
    return result


@frappe.whitelist()
def management_list_support_live_chats(page=1, page_size=100, status=None, search=None):
    _require_management_access("support.manage")
    _support_guard(include_phase2=True)
    from mysite import support_service

    return support_service.management_list_support_live_chats(
        page=page,
        page_size=page_size,
        status=status,
        search=search,
    )


@frappe.whitelist()
def management_reply_support_chat(chat_link_name=None, channel_id=None, ticket_name=None, message=None, payload=None):
    _require_management_access("support.manage")
    _support_guard(include_phase2=True)
    from mysite import support_service

    payload = _resolve_request_payload(payload=payload)
    result = support_service.management_reply_support_chat(
        chat_link_name=str(chat_link_name or payload.get("chat_link_name") or payload.get("chat_link") or "").strip() or None,
        channel_id=str(channel_id or payload.get("channel_id") or "").strip() or None,
        ticket_name=str(ticket_name or payload.get("ticket_name") or payload.get("ticket") or "").strip() or None,
        message=payload.get("message", message),
    )
    audit_log_event(
        module_key="support",
        action_key="management_reply_support_chat",
        target_type="support_chat",
        target_key=str(result.get("channel_id") or result.get("chat_link") or ""),
        result="success",
        details={"ticket_name": str(ticket_name or payload.get("ticket_name") or payload.get("ticket") or "")},
    )
    return result


@frappe.whitelist()
def get_support_shift_status(team=None):
    _require_management_access("support.manage")
    _support_guard(include_phase2=True)
    from mysite import support_service

    return support_service.get_shift_status(team=team)


@frappe.whitelist()
def get_support_online_agents(team=None):
    _require_management_access("support.manage")
    _support_guard(include_phase2=True)
    from mysite import support_service

    return {"items": support_service.get_online_agents(team=team)}


@frappe.whitelist()
def set_support_shift_assignment(ticket_name=None, agent_user=None, team=None, payload=None):
    _require_management_access("support.manage")
    _support_guard(include_phase2=True)
    from mysite import support_service

    payload = _resolve_request_payload(payload=payload)
    target_ticket = str(ticket_name or payload.get("ticket_name") or payload.get("ticket") or "").strip()
    if not target_ticket:
        frappe.throw("نام تیکت الزامی است.")

    result = support_service.set_shift_assignment(
        ticket_name=target_ticket,
        agent_user=str(agent_user or payload.get("agent_user") or "").strip() or None,
        team=str(team or payload.get("team") or "").strip() or None,
    )
    audit_log_event(
        module_key="support",
        action_key="set_support_shift_assignment",
        target_type="support_ticket",
        target_key=target_ticket,
        result="success",
        details={
            "agent_user": str(agent_user or payload.get("agent_user") or ""),
            "team": str(team or payload.get("team") or ""),
        },
    )
    return result


@frappe.whitelist()
def get_support_notification_preferences():
    from mysite import support_service

    return support_service.get_notification_preferences(user=frappe.session.user, ensure_doc=True)


@frappe.whitelist()
def set_support_notification_preferences(payload=None):
    from mysite import support_service

    payload = _resolve_request_payload(payload=payload)
    return support_service.set_notification_preferences(payload=payload, user=frappe.session.user)


@frappe.whitelist()
def mark_support_notifications_seen():
    from mysite import support_service

    return support_service.mark_support_notifications_seen(user=frappe.session.user)


@frappe.whitelist()
def portal_open_support_chat(customer=None, ticket_name=None, subject=None, initial_message=None, source_page=None, payload=None):
    from mysite import portal_api

    return portal_api.portal_open_support_chat(
        customer=customer,
        ticket_name=ticket_name,
        subject=subject,
        initial_message=initial_message,
        source_page=source_page,
        payload=payload,
    )


@frappe.whitelist()
def portal_send_support_chat_message(channel_id=None, ticket_name=None, message=None, payload=None):
    from mysite import portal_api

    return portal_api.portal_send_support_chat_message(
        channel_id=channel_id,
        ticket_name=ticket_name,
        message=message,
        payload=payload,
    )


@frappe.whitelist()
def portal_list_support_chats(page=1, page_size=20):
    from mysite import portal_api

    return portal_api.portal_list_support_chats(page=page, page_size=page_size)


def _feedback_answer_map(question_ids):
    if not question_ids:
        return {}
    from mysite.www.product import FEEDBACK_ANSWER_PREFIX

    answer_subjects = [f"{FEEDBACK_ANSWER_PREFIX}{qid}" for qid in question_ids if qid]
    if not answer_subjects:
        return {}

    rows = frappe.get_all(
        "Comment",
        filters={
            "comment_type": "Comment",
            "subject": ["in", answer_subjects],
        },
        fields=["name", "subject", "content", "comment_by", "comment_email", "creation", "published"],
        order_by="creation desc",
        ignore_permissions=True,
        limit_page_length=0,
    )
    by_question = {}
    for row in rows or []:
        subject = str(row.get("subject") or "")
        qid = subject.replace(FEEDBACK_ANSWER_PREFIX, "", 1).strip()
        if not qid or qid in by_question:
            continue
        by_question[qid] = row
    return by_question


@frappe.whitelist()
def get_management_feedback_queue(limit=80, offset=0, only_unanswered=0, search=None, item_code=None):
    _require_management_access("content.edit")
    from mysite.www.product import FEEDBACK_QUESTION_PREFIX

    limit = min(max(cint(limit or 80), 1), 300)
    offset = max(cint(offset or 0), 0)

    filters = {
        "comment_type": "Comment",
        "reference_doctype": "Item",
        "subject": ["like", f"{FEEDBACK_QUESTION_PREFIX}%"],
    }
    if item_code:
        filters["reference_name"] = str(item_code).strip()

    rows = frappe.get_all(
        "Comment",
        filters=filters,
        fields=["name", "reference_name", "content", "comment_by", "comment_email", "creation", "published"],
        order_by="creation desc",
        start=offset,
        page_length=limit,
        ignore_permissions=True,
    )

    question_ids = [row.get("name") for row in rows if row.get("name")]
    answers_by_question = _feedback_answer_map(question_ids)

    result = []
    term = _clean_support_message(search).lower() if search else ""
    unanswered_only = _to_bool(only_unanswered, False)
    for row in rows:
        question_id = row.get("name")
        answer_row = answers_by_question.get(question_id)
        question_text = _clean_support_message(row.get("content"))
        payload = {
            "question_id": question_id,
            "item_code": row.get("reference_name"),
            "question": question_text,
            "question_author": row.get("comment_by") or row.get("comment_email") or "Unknown",
            "question_email": row.get("comment_email") or "",
            "question_created_at": row.get("creation"),
            "question_published": cint(row.get("published") or 0),
            "answer_id": answer_row.get("name") if answer_row else "",
            "answer": _clean_support_message(answer_row.get("content")) if answer_row else "",
            "answer_author": answer_row.get("comment_by") if answer_row else "",
            "answer_created_at": answer_row.get("creation") if answer_row else "",
            "answer_published": cint(answer_row.get("published") or 0) if answer_row else 0,
        }
        if unanswered_only and payload["answer"]:
            continue
        if term:
            stack = " ".join(
                [
                    str(payload.get("item_code") or ""),
                    str(payload.get("question_author") or ""),
                    str(payload.get("question") or ""),
                    str(payload.get("answer") or ""),
                ]
            ).lower()
            if term not in stack:
                continue
        result.append(payload)

    return {"items": result, "count": len(result)}


@frappe.whitelist()
def reply_management_product_question(question_id=None, answer=None, notify=True, payload=None):
    _require_management_access("content.edit")
    from mysite.www.product import FEEDBACK_ANSWER_PREFIX, FEEDBACK_QUESTION_PREFIX

    payload = _resolve_request_payload(payload=payload)
    qid = str(question_id or payload.get("question_id") or "").strip()
    answer_text = _clean_support_message(payload.get("answer", answer))
    send_email = _to_bool(payload.get("notify", notify), True)

    if not qid:
        frappe.throw("شناسه پرسش الزامی است.")
    if not answer_text:
        frappe.throw("متن پاسخ نمی‌تواند خالی باشد.")
    if len(answer_text) > 1200:
        frappe.throw("متن پاسخ بیش از حد طولانی است.")

    question_doc = frappe.get_doc("Comment", qid)
    if str(question_doc.subject or "").strip() != FEEDBACK_QUESTION_PREFIX:
        frappe.throw("پرسش انتخاب‌شده معتبر نیست.")

    answer_subject = f"{FEEDBACK_ANSWER_PREFIX}{qid}"
    existing = frappe.get_all(
        "Comment",
        filters={
            "comment_type": "Comment",
            "reference_doctype": question_doc.reference_doctype,
            "reference_name": question_doc.reference_name,
            "subject": answer_subject,
        },
        fields=["name"],
        order_by="creation desc",
        limit_page_length=1,
        ignore_permissions=True,
    )

    if existing:
        answer_doc = frappe.get_doc("Comment", existing[0]["name"])
        answer_doc.content = answer_text
        answer_doc.comment_by = frappe.session.user_fullname or frappe.session.user
        answer_doc.comment_email = frappe.db.get_value("User", frappe.session.user, "email") or ""
        answer_doc.published = 1
        answer_doc.save(ignore_permissions=True)
    else:
        answer_doc = frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": question_doc.reference_doctype,
                "reference_name": question_doc.reference_name,
                "subject": answer_subject,
                "content": answer_text,
                "comment_by": frappe.session.user_fullname or frappe.session.user,
                "comment_email": frappe.db.get_value("User", frappe.session.user, "email") or "",
                "published": 1,
            }
        ).insert(ignore_permissions=True)

    notification = {"sent": False, "reason": "disabled"}
    recipient = str(question_doc.comment_email or "").strip()
    if send_email and recipient:
        try:
            frappe.sendmail(
                recipients=[recipient],
                subject="پاسخ پرسش شما",
                message=answer_text,
                reference_doctype="Comment",
                reference_name=question_doc.name,
                now=True,
            )
            notification = {"sent": True}
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Question Answer Email Send Failed")
            notification = {"sent": False, "reason": "send_failed"}

    frappe.db.commit()
    return {
        "ok": True,
        "question_id": qid,
        "answer_id": answer_doc.name,
        "notification": notification,
    }


@frappe.whitelist()
def set_feedback_visibility(comment_id=None, published=1, payload=None):
    _require_management_access("content.edit")
    payload = _resolve_request_payload(payload=payload)
    target_comment = str(comment_id or payload.get("comment_id") or "").strip()
    target_state = 1 if _to_bool(payload.get("published", published), True) else 0

    if not target_comment or not frappe.db.exists("Comment", target_comment):
        frappe.throw("شناسه کامنت معتبر نیست.")

    comment_doc = frappe.get_doc("Comment", target_comment)
    comment_doc.published = target_state
    comment_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"ok": True, "comment_id": comment_doc.name, "published": comment_doc.published}
