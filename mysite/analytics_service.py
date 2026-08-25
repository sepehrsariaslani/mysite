import csv
import hashlib
import io
import ipaddress
import json
import os
import re
from collections import defaultdict
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, get_datetime, getdate, now, now_datetime, nowdate

from mysite.management_audit import log_event as audit_log_event
from mysite.management_permissions import has_capability, require_capability

TEHRAN_TIMEZONE = "Asia/Tehran"
DEFAULT_FUNNEL_STEPS = ["product_view", "add_to_cart", "checkout_start", "order_submit"]
DEFAULT_GOAL_STEPS = ["visit", "add_to_cart", "checkout", "order"]
TRACKABLE_EVENTS = {
    "product_view",
    "product_images_open",
    "product_reviews_open",
    "category_filter_apply",
    "site_search",
    "add_to_cart",
    "remove_from_cart",
    "cart_open",
    "checkout_start",
    "coupon_click",
    "order_submit",
    "page_view",
    "page_performance",
    "call_click",
    "whatsapp_click",
    "email_click",
    "form_submit",
}
DEFAULT_EVENT_TOGGLES = [
    ("product_view", "Product details viewed"),
    ("product_images_open", "Product image gallery opened"),
    ("product_reviews_open", "Product reviews/questions tab opened"),
    ("category_filter_apply", "Category page filters applied"),
    ("site_search", "Site search submitted"),
    ("add_to_cart", "Added to cart"),
    ("remove_from_cart", "Removed from cart"),
    ("cart_open", "Cart sidebar/page opened"),
    ("checkout_start", "Checkout flow started"),
    ("coupon_click", "Coupon interaction"),
    ("order_submit", "Order or quotation submitted"),
    ("page_view", "Page view timing payload"),
    ("page_performance", "Core Web Vitals and page performance payload"),
    ("call_click", "Click to call CTA"),
    ("whatsapp_click", "WhatsApp CTA"),
    ("email_click", "Email CTA"),
    ("form_submit", "Form submission CTA"),
]
DEFAULT_SEGMENT_KEY = "__all__"
SAVED_SEGMENTS_FILE = "analytics_saved_segments.json"
EXTERNAL_ANALYTICS_SETTINGS_FILE = "analytics_external_sources.json"
GOAL_STEP_ALIASES = {
    "visit": {"page_view", "product_view"},
    "page_view": {"page_view", "product_view"},
    "product_view": {"product_view", "page_view"},
    "add_to_cart": {"add_to_cart"},
    "checkout": {"checkout_start"},
    "checkout_start": {"checkout_start"},
    "order": {"order_submit"},
    "purchase": {"order_submit"},
    "order_submit": {"order_submit"},
    "بازدید": {"page_view", "product_view"},
    "افزودن_به_سبد": {"add_to_cart"},
    "افزودن به سبد": {"add_to_cart"},
    "شروع_تسویه": {"checkout_start"},
    "شروع تسویه": {"checkout_start"},
    "ثبت_سفارش": {"order_submit"},
    "ثبت سفارش": {"order_submit"},
}
BOT_UA_REGEX = re.compile(r"(bot|spider|crawl|headless|python-requests|curl|wget|scrapy)", re.I)
SOCIAL_CHANNELS = {
    "instagram",
    "telegram",
    "facebook",
    "pinterest",
    "linkedin",
    "x",
    "youtube",
    "tiktok",
    "whatsapp",
}
SEARCH_ENGINES = {"google", "bing", "yahoo"}
ALERT_METRIC_DEFINITIONS = {
    "conversion_rate": {
        "label": "نرخ تبدیل",
        "description": "درصد تبدیل بازدید به سفارش/ثبت سفارش.",
        "default_operator": "<",
        "default_threshold": 1,
        "default_window_days": 7,
    },
    "revenue_drop_percent": {
        "label": "افت درآمد",
        "description": "درصد افت درآمد نسبت به بازه قبلی هم‌طول.",
        "default_operator": ">=",
        "default_threshold": 25,
        "default_window_days": 7,
    },
    "sla_failed_ratio": {
        "label": "نسبت نقض SLA",
        "description": "درصد تیکت‌هایی که وضعیت SLA آن‌ها Failed شده است.",
        "default_operator": ">=",
        "default_threshold": 15,
        "default_window_days": 7,
    },
}


def _doctype_exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def _get_roles(user=None):
    target = user or frappe.session.user
    if not target or target == "Guest":
        return set()
    return set(frappe.get_roles(target) or [])


def has_management_access(user=None):
    return has_capability("analytics.view", user=user)


def require_management_access():
    require_capability("analytics.view", message=_("دسترسی لازم برای مشاهده داشبورد آنالیتیکس را ندارید."))


def require_analytics_manage_access():
    require_capability("analytics.manage", message=_("دسترسی لازم برای مدیریت تنظیمات آنالیتیکس را ندارید."))


def _safe_json(value):
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _to_float(value, default=0):
    try:
        return float(value or 0)
    except Exception:
        return default


def _to_int(value, default=0):
    try:
        return int(value or 0)
    except Exception:
        return default


def _safe_str(value):
    return str(value or "").strip()


def _safe_identifier(value):
    raw = _safe_str(value)
    return raw[:140]


def _normalize_path(raw_url):
    value = _safe_str(raw_url)
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


def _path_group_meta(path):
    normalized = _normalize_path(path)

    mapping = [
        ("home", "صفحه اصلی", "/mysite", lambda p: p == "/mysite"),
        (
            "sofas",
            "مبلمان و مدل‌ها",
            "/mysite/sofas",
            lambda p: p.startswith("/mysite/sofas")
            or p.startswith("/mysite/product")
            or p.startswith("/mysite/sofa"),
        ),
        (
            "blog",
            "بلاگ و محتوا",
            "/mysite/blog",
            lambda p: p.startswith("/mysite/blog") or p.startswith("/mysite/special-edition") or p.startswith("/mysite/outlet"),
        ),
        (
            "catalog",
            "دسته‌بندی و لیست محصولات",
            "/mysite/categories",
            lambda p: p.startswith("/mysite/categories")
            or p.startswith("/mysite/tables")
            or p.startswith("/mysite/dining-chairs")
            or p.startswith("/mysite/barstools")
            or p.startswith("/mysite/coffee-tables")
            or p.startswith("/mysite/benches")
            or p.startswith("/mysite/beds")
            or p.startswith("/mysite/cushions")
            or p.startswith("/mysite/fabrics"),
        ),
        (
            "projects",
            "پروژه‌ها و الهام",
            "/mysite/projects",
            lambda p: p.startswith("/mysite/projects")
            or p.startswith("/mysite/project")
            or p.startswith("/mysite/gallery")
            or p.startswith("/mysite/shop-by-look"),
        ),
        (
            "support",
            "خدمات و اطلاعات",
            "/mysite/consultation",
            lambda p: p.startswith("/mysite/consultation")
            or p.startswith("/mysite/faq")
            or p.startswith("/mysite/about")
            or p.startswith("/mysite/dealers")
            or p.startswith("/mysite/cooperation")
            or p.startswith("/mysite/downloads"),
        ),
        (
            "account",
            "حساب کاربری و سبد",
            "/mysite/dashboard",
            lambda p: p.startswith("/mysite/dashboard")
            or p.startswith("/mysite/login")
            or p.startswith("/mysite/cart")
            or p.startswith("/mysite/saved"),
        ),
    ]

    for key, label, root_path, matcher in mapping:
        if matcher(normalized):
            return {
                "group_key": key,
                "label": label,
                "root_path": root_path,
            }

    return {
        "group_key": "other",
        "label": "سایر صفحات",
        "root_path": "/mysite",
    }


def _safe_list(value):
    if isinstance(value, (list, tuple, set)):
        return [_safe_str(item) for item in value if _safe_str(item)]
    if isinstance(value, str):
        tokens = re.split(r"[,\n؛;]+", value)
        return [_safe_str(item) for item in tokens if _safe_str(item)]
    return []


def _safe_slug(value, fallback="segment"):
    raw = _safe_str(value).lower()
    if not raw:
        raw = fallback
    raw = raw.replace(" ", "-").replace("_", "-")
    raw = re.sub(r"[^a-z0-9\u0600-\u06ff\-]+", "", raw)
    raw = re.sub(r"-{2,}", "-", raw).strip("-")
    return raw or fallback


def _saved_segments_path():
    return frappe.get_site_path("private", SAVED_SEGMENTS_FILE)


def _normalize_segment_payload(row, index=0):
    row = row or {}
    title = _safe_str(row.get("title") or row.get("name") or f"Segment {index + 1}")
    key = _safe_slug(row.get("key") or title, fallback=f"segment-{index + 1}")
    source_channels = [item.lower() for item in _safe_list(row.get("source_channels"))]
    device_types = [item.lower() for item in _safe_list(row.get("device_types"))]
    cities = [item.lower() for item in _safe_list(row.get("cities"))]
    page_groups = [item.lower() for item in _safe_list(row.get("page_groups"))]
    campaigns = [item.lower() for item in _safe_list(row.get("campaigns"))]
    return {
        "key": key,
        "title": title,
        "is_active": 1 if cint(row.get("is_active", 1)) else 0,
        "source_channels": source_channels,
        "device_types": device_types,
        "cities": cities,
        "page_groups": page_groups,
        "campaigns": campaigns,
        "note": _safe_str(row.get("note")),
    }


def _default_saved_segments():
    return [
        {
            "key": DEFAULT_SEGMENT_KEY,
            "title": "مشاهده همه",
            "is_active": 1,
            "source_channels": [],
            "device_types": [],
            "cities": [],
            "page_groups": [],
            "campaigns": [],
            "note": "بدون فیلتر",
        }
    ]


def _load_saved_segments():
    path = _saved_segments_path()
    if not os.path.exists(path):
        return _default_saved_segments()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle) or {}
    except Exception:
        return _default_saved_segments()

    rows = payload.get("segments") if isinstance(payload, dict) else payload
    rows = rows if isinstance(rows, list) else []
    normalized = [_normalize_segment_payload(row, index=idx) for idx, row in enumerate(rows)]
    deduped = {}
    for row in normalized:
        deduped[row["key"]] = row
    results = list(deduped.values())
    if not any(row.get("key") == DEFAULT_SEGMENT_KEY for row in results):
        results = _default_saved_segments() + results
    return results


def _save_saved_segments(rows):
    unique = {}
    for idx, row in enumerate(rows or []):
        normalized = _normalize_segment_payload(row, index=idx)
        unique[normalized["key"]] = normalized
    if DEFAULT_SEGMENT_KEY not in unique:
        unique[DEFAULT_SEGMENT_KEY] = _default_saved_segments()[0]

    payload = {
        "updated_at": now_datetime().isoformat(),
        "segments": list(unique.values()),
    }
    path = _saved_segments_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return payload["segments"]


def _resolve_active_segment(segment_key=None):
    key = _safe_slug(segment_key or DEFAULT_SEGMENT_KEY, fallback=DEFAULT_SEGMENT_KEY)
    segments = _load_saved_segments()
    selected = next((row for row in segments if row.get("key") == key and cint(row.get("is_active", 1))), None)
    if not selected:
        selected = next((row for row in segments if row.get("key") == DEFAULT_SEGMENT_KEY), None) or _default_saved_segments()[0]
    return selected, segments


def _external_settings_path():
    return frappe.get_site_path("private", EXTERNAL_ANALYTICS_SETTINGS_FILE)


def _default_external_settings():
    return {
        "ga4": {
            "enabled": 0,
            "property_id": "",
            "service_account_path": "",
            "service_account_json": "",
        },
        "gsc": {
            "enabled": 0,
            "site_url": "",
            "service_account_path": "",
            "service_account_json": "",
        },
    }


def _normalize_external_settings(payload):
    payload = payload or {}
    base = _default_external_settings()
    for key in ["ga4", "gsc"]:
        raw = payload.get(key) if isinstance(payload, dict) else {}
        raw = raw if isinstance(raw, dict) else {}
        target = base[key]
        target["enabled"] = 1 if cint(raw.get("enabled", target["enabled"])) else 0
        if key == "ga4":
            target["property_id"] = _safe_str(raw.get("property_id"))
        if key == "gsc":
            target["site_url"] = _safe_str(raw.get("site_url"))
        target["service_account_path"] = _safe_str(raw.get("service_account_path"))
        target["service_account_json"] = _safe_str(raw.get("service_account_json"))
    return base


def _load_external_settings():
    path = _external_settings_path()
    if not os.path.exists(path):
        return _default_external_settings()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle) or {}
    except Exception:
        return _default_external_settings()
    return _normalize_external_settings(payload)


def _save_external_settings(payload):
    normalized = _normalize_external_settings(payload)
    path = _external_settings_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(normalized, handle, ensure_ascii=False, indent=2)
    return normalized


def _query_param(url, key):
    value = _safe_str(url)
    if not value:
        return ""
    try:
        parsed = parse_qs(urlsplit(value).query)
    except Exception:
        return ""
    return _safe_str((parsed.get(key) or [""])[0])


def _normalize_goal_step_key(step):
    return _safe_str(step).lower().replace("-", "_").replace(" ", "_")


def _goal_step_aliases(step):
    key = _normalize_goal_step_key(step)
    aliases = GOAL_STEP_ALIASES.get(key)
    if aliases:
        return set(aliases)
    return {key}


def _parse_goal_steps(steps_json):
    if isinstance(steps_json, list):
        rows = steps_json
    else:
        rows = _safe_json(steps_json) if steps_json else []
    if not isinstance(rows, list):
        return list(DEFAULT_GOAL_STEPS)

    steps = [_safe_str(item) for item in rows if _safe_str(item)]
    return steps or list(DEFAULT_GOAL_STEPS)


def _normalize_goal_definition_payload(row, index=0):
    row = row or {}
    title = _safe_str(row.get("title") or row.get("name") or f"Goal {index + 1}")
    raw_steps = row.get("steps")
    if raw_steps is None:
        raw_steps = row.get("steps_json")
    steps = _parse_goal_steps(raw_steps) or list(DEFAULT_GOAL_STEPS)
    return {
        "name": _safe_str(row.get("name")),
        "title": title,
        "is_active": 1 if cint(row.get("is_active", 1)) else 0,
        "is_default": 1 if cint(row.get("is_default", 0)) else 0,
        "steps_json": json.dumps(steps, ensure_ascii=False),
        "steps": steps,
    }


def _normalize_goal_rows(rows, ensure_default=True):
    rows = rows if isinstance(rows, list) else []
    normalized = [_normalize_goal_definition_payload(row, index=idx) for idx, row in enumerate(rows)]
    if ensure_default and not normalized:
        normalized = [
            _normalize_goal_definition_payload(
                {
                    "name": "default-goal",
                    "title": "قیف اصلی",
                    "is_active": 1,
                    "is_default": 1,
                    "steps": list(DEFAULT_GOAL_STEPS),
                }
            )
        ]
    default_index = next((idx for idx, row in enumerate(normalized) if cint(row.get("is_default") or 0)), None)
    if default_index is None and normalized:
        normalized[0]["is_default"] = 1
    elif default_index is not None:
        for idx, row in enumerate(normalized):
            row["is_default"] = 1 if idx == default_index else 0
    return normalized


def _event_rows_for_range(from_date, to_date):
    if not _event_table_available():
        return []

    rows = frappe.db.sql(
        """
        SELECT
            name,
            occurred_at,
            session_id,
            user_id,
            event_type,
            page_url,
            referrer_url,
            source_channel,
            device_type,
            amount,
            dedupe_key,
            properties_json
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
        ORDER BY occurred_at ASC, name ASC
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )

    normalized = []
    for row in rows:
        props = _safe_json(row.get("properties_json"))
        page_url = _safe_str(row.get("page_url"))
        referrer_url = _safe_str(row.get("referrer_url"))
        utm_source = _safe_str(props.get("utm_source") or _query_param(page_url, "utm_source") or _query_param(referrer_url, "utm_source")).lower()
        utm_medium = _safe_str(props.get("utm_medium") or _query_param(page_url, "utm_medium") or _query_param(referrer_url, "utm_medium")).lower()
        utm_campaign = _safe_str(props.get("utm_campaign") or _query_param(page_url, "utm_campaign") or _query_param(referrer_url, "utm_campaign")).lower()
        utm_term = _safe_str(props.get("utm_term") or _query_param(page_url, "utm_term")).lower()
        utm_content = _safe_str(props.get("utm_content") or _query_param(page_url, "utm_content")).lower()
        city = _safe_str(props.get("city") or props.get("geo_city") or props.get("location_city")).lower()
        language = _normalize_language_code(props.get("language") or props.get("lang"))
        user_agent = _safe_str(props.get("user_agent"))
        browser_name = _safe_str(props.get("browser_name") or _browser_from_user_agent(user_agent)).lower()
        os_name = _safe_str(props.get("os_name") or _os_from_user_agent(user_agent)).lower()
        user_id = _safe_identifier(row.get("user_id"))
        session_id = _safe_identifier(row.get("session_id"))
        visitor_key = user_id or session_id or f"anon::{row.get('name')}"
        journey_key = session_id or visitor_key

        normalized.append(
            {
                "name": row.get("name"),
                "occurred_at": get_datetime(row.get("occurred_at")),
                "event_type": _safe_identifier(row.get("event_type")).lower(),
                "session_id": session_id,
                "user_id": user_id,
                "visitor_key": visitor_key,
                "journey_key": journey_key,
                "page_url": page_url,
                "source_channel": _safe_identifier(row.get("source_channel")).lower() or "other",
                "device_type": _safe_identifier(row.get("device_type")).lower() or "other",
                "amount": flt(row.get("amount") or 0),
                "dedupe_key": _safe_str(row.get("dedupe_key")),
                "properties": props if isinstance(props, dict) else {},
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_term": utm_term,
                "utm_content": utm_content,
                "city": city,
                "request_ip": _safe_str(props.get("request_ip")),
                "user_agent": user_agent,
                "browser_name": browser_name or "other",
                "os_name": os_name or "other",
                "language": language or "",
                "page_group": _path_group_meta(page_url).get("group_key"),
            }
        )
    return normalized


def _event_matches_segment(row, segment):
    if not segment:
        return True
    if segment.get("key") == DEFAULT_SEGMENT_KEY:
        return True

    if segment.get("source_channels"):
        if row.get("source_channel") not in set(segment.get("source_channels") or []):
            return False
    if segment.get("device_types"):
        if row.get("device_type") not in set(segment.get("device_types") or []):
            return False
    if segment.get("cities"):
        if row.get("city") not in set(segment.get("cities") or []):
            return False
    if segment.get("page_groups"):
        if _safe_str(row.get("page_group")).lower() not in set(segment.get("page_groups") or []):
            return False
    if segment.get("campaigns"):
        if _safe_str(row.get("utm_campaign")).lower() not in set(segment.get("campaigns") or []):
            return False
    return True


def _filter_events_by_segment(rows, segment):
    return [row for row in rows if _event_matches_segment(row, segment)]


def _load_ip_exclusion_rules():
    if not _doctype_exists("Analytics IP Exclusion"):
        return []
    rules = []
    rows = frappe.get_all(
        "Analytics IP Exclusion",
        filters={"is_active": 1},
        fields=["ip_or_cidr"],
        limit_page_length=0,
    )
    for row in rows:
        raw = _safe_str(row.get("ip_or_cidr"))
        if not raw:
            continue
        try:
            if "/" in raw:
                rules.append(ipaddress.ip_network(raw, strict=False))
            else:
                rules.append(ipaddress.ip_address(raw))
        except Exception:
            continue
    return rules


def _ip_in_rules(ip_value, rules):
    raw = _safe_str(ip_value)
    if not raw:
        return False
    try:
        ip_obj = ipaddress.ip_address(raw)
    except Exception:
        return False
    for rule in rules:
        try:
            if isinstance(rule, (ipaddress.IPv4Network, ipaddress.IPv6Network)):
                if ip_obj in rule:
                    return True
            elif ip_obj == rule:
                return True
        except Exception:
            continue
    return False


def _resolve_range(range_key=None, from_date=None, to_date=None, days=None):
    today = getdate(nowdate())

    if days:
        day_count = min(max(_to_int(days, 30), 1), 365)
        start = add_days(today, -1 * (day_count - 1))
        return str(start), str(today), day_count

    key = _safe_str(range_key).lower()
    if key in {"today", "امروز"}:
        return str(today), str(today), 1
    if key in {"yesterday", "دیروز"}:
        y = add_days(today, -1)
        return str(y), str(y), 1
    if key in {"7d", "7days", "7"}:
        start = add_days(today, -6)
        return str(start), str(today), 7
    if key in {"30d", "30days", "30", ""}:
        start = add_days(today, -29)
        return str(start), str(today), 30
    if key in {"90d", "90days", "90", "3m", "3mo", "3month", "3months"}:
        start = add_days(today, -89)
        return str(start), str(today), 90
    if key in {"180d", "180days", "180", "6m", "6mo", "6month", "6months"}:
        start = add_days(today, -179)
        return str(start), str(today), 180
    if key in {"365d", "365days", "365", "1y", "1yr", "1year", "yearly"}:
        start = add_days(today, -364)
        return str(start), str(today), 365

    if from_date or to_date:
        start = getdate(from_date) if from_date else add_days(today, -29)
        end = getdate(to_date) if to_date else today
        if start > end:
            start, end = end, start
        return str(start), str(end), (end - start).days + 1

    start = add_days(today, -29)
    return str(start), str(today), 30


def _resolve_compare_range(from_date, to_date):
    start = getdate(from_date)
    end = getdate(to_date)
    days = (end - start).days + 1
    prev_end = add_days(start, -1)
    prev_start = add_days(prev_end, -1 * (days - 1))
    return str(prev_start), str(prev_end)


def _request_ip():
    headers = getattr(frappe.local, "request", None)
    if headers:
        forwarded_for = headers.headers.get("X-Forwarded-For") if getattr(headers, "headers", None) else None
        if forwarded_for:
            return _safe_str(forwarded_for.split(",")[0])
    return _safe_str(getattr(frappe.local, "request_ip", ""))


def _user_agent():
    request_obj = getattr(frappe.local, "request", None)
    if not request_obj or not getattr(request_obj, "headers", None):
        return ""
    return _safe_str(request_obj.headers.get("User-Agent"))


def _request_language():
    request_obj = getattr(frappe.local, "request", None)
    if not request_obj or not getattr(request_obj, "headers", None):
        return ""
    raw = _safe_str(request_obj.headers.get("Accept-Language"))
    if not raw:
        return ""
    return _safe_str(raw.split(",")[0]).lower()


def _normalize_language_code(value):
    raw = _safe_str(value).lower().replace("_", "-")
    if not raw:
        return ""
    return raw.split(",")[0].split(";")[0][:20]


def _device_type_from_user_agent(user_agent):
    raw = _safe_str(user_agent).lower()
    if not raw:
        return "other"
    if "ipad" in raw or "tablet" in raw:
        return "tablet"
    if any(token in raw for token in ["iphone", "android", "mobile"]):
        return "mobile"
    if any(token in raw for token in ["windows", "macintosh", "linux"]):
        return "desktop"
    return "other"


def _browser_from_user_agent(user_agent):
    raw = _safe_str(user_agent).lower()
    if not raw:
        return "other"
    if "edg/" in raw or "edge/" in raw:
        return "edge"
    if "opr/" in raw or "opera" in raw:
        return "opera"
    if "samsungbrowser/" in raw:
        return "samsung"
    if "chrome/" in raw and "edg/" not in raw and "opr/" not in raw:
        return "chrome"
    if "firefox/" in raw:
        return "firefox"
    if "safari/" in raw and "chrome/" not in raw:
        return "safari"
    if "trident/" in raw or "msie" in raw:
        return "ie"
    return "other"


def _os_from_user_agent(user_agent):
    raw = _safe_str(user_agent).lower()
    if not raw:
        return "other"
    if "android" in raw:
        return "android"
    if "iphone" in raw or "ipad" in raw or "ios" in raw:
        return "ios"
    if "windows" in raw:
        return "windows"
    if "mac os x" in raw or "macintosh" in raw:
        return "macos"
    if "linux" in raw:
        return "linux"
    if "cros" in raw:
        return "chromeos"
    return "other"


def _source_from_referrer_and_utm(referrer_url, utm_source):
    utm = _safe_str(utm_source).lower()
    ref = _safe_str(referrer_url).lower()

    probe = utm or ref
    if any(token in probe for token in ["facebook", "fb.com", "fb.me"]):
        return "facebook"
    if any(token in probe for token in ["pinterest", "pin.it"]):
        return "pinterest"
    if "linkedin" in probe:
        return "linkedin"
    if any(token in probe for token in ["twitter", "x.com"]):
        return "x"
    if any(token in probe for token in ["youtube", "youtu.be"]):
        return "youtube"
    if "tiktok" in probe:
        return "tiktok"
    if any(token in probe for token in ["whatsapp", "wa.me"]):
        return "whatsapp"
    if "bing" in probe:
        return "bing"
    if "yahoo" in probe:
        return "yahoo"
    if any(token in probe for token in ["mail", "email", "newsletter"]):
        return "email"
    if "google" in probe:
        return "google"
    if any(token in probe for token in ["instagram", "instagr.am"]):
        return "instagram"
    if any(token in probe for token in ["telegram", "t.me"]):
        return "telegram"
    if not probe:
        return "direct"
    return "other"


def _host_from_url(url_value):
    raw = _safe_str(url_value)
    if not raw:
        return ""
    try:
        host = _safe_str(urlsplit(raw).hostname).lower()
    except Exception:
        host = ""
    return host


def _source_channel_group(row):
    row = row or {}
    source = _safe_str(row.get("source_channel")).lower()
    utm_medium = _safe_str(row.get("utm_medium")).lower()
    utm_source = _safe_str(row.get("utm_source")).lower()
    referrer = _safe_str(row.get("referrer_url")).lower()

    if any(token in utm_medium for token in ["cpc", "ppc", "paid", "ads", "display", "retarget"]):
        return "paid"
    if any(token in utm_medium for token in ["email", "newsletter"]) or any(token in utm_source for token in ["email", "newsletter"]):
        return "email"
    if utm_medium == "organic" or source in SEARCH_ENGINES or utm_source in SEARCH_ENGINES:
        return "organic"
    if utm_medium in {"social", "social_paid"} or source in SOCIAL_CHANNELS:
        return "social"

    ref_host = _host_from_url(referrer)
    if ref_host and not any(token in ref_host for token in ["denroom", "localhost", "127.0.0.1"]):
        return "referral"
    if source == "direct" and not referrer:
        return "direct"
    if source == "other" and referrer:
        return "referral"
    return source or "other"


def _get_toggle_map():
    if not _doctype_exists("Analytics Event Toggle"):
        return {name: True for name, _ in DEFAULT_EVENT_TOGGLES}

    rows = frappe.get_all(
        "Analytics Event Toggle",
        fields=["event_key", "is_active"],
        limit_page_length=0,
    )
    mapping = {name: True for name, _ in DEFAULT_EVENT_TOGGLES}
    for row in rows:
        key = _safe_identifier(row.get("event_key"))
        if key:
            mapping[key] = bool(cint(row.get("is_active") or 0))
    return mapping


def _is_ip_excluded(ip_address):
    if not ip_address or not _doctype_exists("Analytics IP Exclusion"):
        return False

    rows = frappe.get_all(
        "Analytics IP Exclusion",
        filters={"is_active": 1},
        fields=["ip_or_cidr"],
        limit_page_length=0,
    )
    if not rows:
        return False

    try:
        ip_obj = ipaddress.ip_address(ip_address)
    except Exception:
        return False

    for row in rows:
        raw = _safe_str(row.get("ip_or_cidr"))
        if not raw:
            continue
        try:
            if "/" in raw:
                network = ipaddress.ip_network(raw, strict=False)
                if ip_obj in network:
                    return True
            elif ip_obj == ipaddress.ip_address(raw):
                return True
        except Exception:
            continue
    return False


def _rate_limit_ok(ip_address):
    if not ip_address:
        return True
    cache = frappe.cache()
    key = f"analytics:rate:{ip_address}:{now_datetime().strftime('%Y%m%d%H%M')}"
    current = _to_int(cache.get_value(key), 0) + 1
    cache.set_value(key, current, expires_in_sec=70)
    return current <= 320


def _build_dedupe_key(payload):
    explicit = _safe_identifier(payload.get("dedupe_key"))
    if explicit:
        return explicit

    event_id = _safe_identifier(payload.get("event_id"))
    if event_id:
        return f"event::{event_id}"

    segments = [
        _safe_str(payload.get("event_type")),
        _safe_str(payload.get("session_id")),
        _safe_str(payload.get("product_id")),
        _safe_str(payload.get("model_name")),
        _safe_str(payload.get("page_url")),
        str(_to_float(payload.get("qty"), 1)),
        str(_to_float(payload.get("amount"), 0)),
        now_datetime().strftime("%Y%m%d%H%M"),
    ]
    digest = hashlib.sha256("|".join(segments).encode("utf-8")).hexdigest()
    return f"auto::{digest[:48]}"


def _normalize_payload(payload):
    props = payload.get("properties") or payload.get("properties_json") or {}
    if isinstance(props, str):
        props = _safe_json(props)
    if not isinstance(props, dict):
        props = {}

    user_agent = _safe_str(payload.get("user_agent")) or _user_agent()
    referrer_url = _safe_str(payload.get("referrer_url"))
    source_channel = _safe_str(payload.get("source_channel"))
    request_ip = _safe_str(payload.get("request_ip")) or _request_ip()
    page_url = _safe_str(payload.get("page_url"))

    device_type = _safe_str(payload.get("device_type"))
    if not device_type:
        device_type = _device_type_from_user_agent(user_agent)

    utm_source = _safe_str(payload.get("utm_source") or props.get("utm_source") or _query_param(page_url, "utm_source") or _query_param(referrer_url, "utm_source"))
    utm_medium = _safe_str(payload.get("utm_medium") or props.get("utm_medium") or _query_param(page_url, "utm_medium") or _query_param(referrer_url, "utm_medium"))
    utm_campaign = _safe_str(payload.get("utm_campaign") or props.get("utm_campaign") or _query_param(page_url, "utm_campaign") or _query_param(referrer_url, "utm_campaign"))
    utm_term = _safe_str(payload.get("utm_term") or props.get("utm_term") or _query_param(page_url, "utm_term"))
    utm_content = _safe_str(payload.get("utm_content") or props.get("utm_content") or _query_param(page_url, "utm_content"))

    if source_channel not in {
        "direct",
        "google",
        "bing",
        "yahoo",
        "instagram",
        "telegram",
        "facebook",
        "pinterest",
        "linkedin",
        "x",
        "youtube",
        "tiktok",
        "whatsapp",
        "email",
        "referral",
        "paid",
        "other",
    }:
        source_channel = _source_from_referrer_and_utm(referrer_url, utm_source)

    city = _safe_str(payload.get("city") or payload.get("geo_city") or props.get("city") or props.get("geo_city") or props.get("location_city"))
    language = _normalize_language_code(
        payload.get("language") or props.get("language") or props.get("lang") or _request_language()
    )
    if user_agent:
        props["user_agent"] = user_agent
    if request_ip:
        props["request_ip"] = request_ip
    if city:
        props["city"] = city
    if language:
        props["language"] = language
    if not props.get("browser_name"):
        props["browser_name"] = _browser_from_user_agent(user_agent)
    if not props.get("os_name"):
        props["os_name"] = _os_from_user_agent(user_agent)
    if utm_source:
        props["utm_source"] = utm_source
    if utm_medium:
        props["utm_medium"] = utm_medium
    if utm_campaign:
        props["utm_campaign"] = utm_campaign
    if utm_term:
        props["utm_term"] = utm_term
    if utm_content:
        props["utm_content"] = utm_content

    session_id = _safe_identifier(payload.get("session_id"))
    if not session_id:
        session_id = _safe_identifier(frappe.session.sid if frappe.session.user != "Guest" else "")

    event_type = _safe_identifier(payload.get("event_type"))

    occurred_at = payload.get("occurred_at") or now()

    normalized = {
        "event_type": event_type,
        "occurred_at": occurred_at,
        "session_id": session_id,
        "user_id": _safe_identifier(payload.get("user_id")) or (frappe.session.user if frappe.session.user != "Guest" else ""),
        "customer": _safe_identifier(payload.get("customer")),
        "page_url": page_url,
        "referrer_url": referrer_url,
        "source_channel": source_channel,
        "device_type": device_type,
        "product_id": _safe_identifier(payload.get("product_id") or payload.get("item_code")),
        "model_name": _safe_identifier(payload.get("model_name")),
        "item_group": _safe_identifier(payload.get("item_group") or payload.get("category")),
        "qty": _to_float(payload.get("qty"), 1),
        "amount": _to_float(payload.get("amount"), 0),
        "properties": props if isinstance(props, dict) else {},
        "scroll_depth": _to_float(payload.get("scroll_depth"), 0),
        "time_spent_seconds": _to_float(payload.get("time_spent_seconds"), 0),
        "left_at": payload.get("left_at") or "",
        "cart_value": _to_float(payload.get("cart_value"), 0),
        "funnel_step": _safe_identifier(payload.get("funnel_step")),
    }
    normalized["dedupe_key"] = _build_dedupe_key(payload)
    return normalized


def _insert_analytics_event(event):
    if not _doctype_exists("Analytics Event"):
        return ""

    doc = frappe.get_doc(
        {
            "doctype": "Analytics Event",
            "occurred_at": event["occurred_at"],
            "session_id": event["session_id"],
            "user_id": event["user_id"],
            "customer": event["customer"],
            "event_type": event["event_type"],
            "page_url": event["page_url"],
            "referrer_url": event["referrer_url"],
            "source_channel": event["source_channel"],
            "device_type": event["device_type"],
            "product_id": event["product_id"],
            "model_name": event["model_name"],
            "item_group": event["item_group"],
            "qty": event["qty"],
            "amount": event["amount"],
            "properties_json": json.dumps(event["properties"], ensure_ascii=False),
            "dedupe_key": event["dedupe_key"],
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def _insert_page_view(event):
    if not _doctype_exists("Page View"):
        return
    if event["event_type"] not in {"page_view", "product_view"}:
        return

    doc = frappe.get_doc(
        {
            "doctype": "Page View",
            "session_id": event["session_id"],
            "url": event["page_url"] or "/",
            "entered_at": event["occurred_at"],
            "left_at": event["left_at"] or None,
            "time_spent_seconds": event["time_spent_seconds"],
            "scroll_depth": event["scroll_depth"],
            "device_type": event["device_type"],
            "source_channel": event["source_channel"],
            "product_id": event["product_id"],
            "model_name": event["model_name"],
        }
    )
    doc.insert(ignore_permissions=True)


def _insert_cart_event(event):
    if not _doctype_exists("Cart Event"):
        return

    mapping = {
        "add_to_cart": "add",
        "remove_from_cart": "remove",
        "cart_open": "open",
        "checkout_start": "checkout_start",
    }
    action = mapping.get(event["event_type"])
    if not action:
        return

    doc = frappe.get_doc(
        {
            "doctype": "Cart Event",
            "session_id": event["session_id"],
            "product_id": event["product_id"],
            "model_name": event["model_name"],
            "action": action,
            "qty": event["qty"],
            "price": event["amount"],
            "cart_value": event["cart_value"],
            "occurred_at": event["occurred_at"],
            "device_type": event["device_type"],
        }
    )
    doc.insert(ignore_permissions=True)


def _insert_funnel_step(event):
    if not _doctype_exists("Funnel Step"):
        return

    mapping = {
        "product_view": "product_view",
        "add_to_cart": "add_to_cart",
        "checkout_start": "checkout_start",
        "order_submit": "order_submit",
    }
    step_name = event["funnel_step"] or mapping.get(event["event_type"])
    if step_name not in DEFAULT_FUNNEL_STEPS:
        return

    doc = frappe.get_doc(
        {
            "doctype": "Funnel Step",
            "session_id": event["session_id"],
            "step_name": step_name,
            "completed": 1,
            "occurred_at": event["occurred_at"],
            "device_type": event["device_type"],
            "item_group": event["item_group"],
            "model_name": event["model_name"],
            "source_channel": event["source_channel"],
        }
    )
    doc.insert(ignore_permissions=True)


def track_event_payload(payload, from_fallback=False):
    payload = payload or {}
    event = _normalize_payload(payload)

    if event["event_type"] not in TRACKABLE_EVENTS:
        frappe.throw(_("نوع رویداد نامعتبر است."), frappe.ValidationError)

    toggle_map = _get_toggle_map()
    if not toggle_map.get(event["event_type"], True):
        return {"ok": True, "skipped": True, "reason": "event_disabled"}

    request_ip = _request_ip()
    if _is_ip_excluded(request_ip):
        return {"ok": True, "skipped": True, "reason": "ip_excluded"}

    if not from_fallback and not _rate_limit_ok(request_ip):
        frappe.throw(_("تعداد درخواست آنالیتیکس بیش از حد مجاز است."), frappe.ValidationError)

    if _doctype_exists("Analytics Event") and event["dedupe_key"]:
        existing = frappe.db.get_value("Analytics Event", {"dedupe_key": event["dedupe_key"]}, "name")
        if existing:
            return {"ok": True, "duplicate": True, "name": existing}

    try:
        event_name = _insert_analytics_event(event)
        _insert_page_view(event)
        _insert_cart_event(event)
        _insert_funnel_step(event)
        frappe.db.commit()
        return {"ok": True, "name": event_name, "dedupe_key": event["dedupe_key"]}
    except Exception:
        frappe.db.rollback()
        if from_fallback:
            raise
        frappe.enqueue(
            "mysite.analytics_scheduler.process_event_async",
            queue="short",
            payload=event,
            enqueue_after_commit=False,
        )
        return {"ok": True, "queued": True, "dedupe_key": event["dedupe_key"]}


def track_page_view_payload(payload):
    payload = dict(payload or {})
    payload["event_type"] = "page_view"
    return track_event_payload(payload)


def _event_table_available():
    return _doctype_exists("Analytics Event")


def _base_event_filter_sql(from_date, to_date):
    return "occurred_at >= %(from_dt)s AND occurred_at <= %(to_dt)s", {
        "from_dt": f"{from_date} 00:00:00",
        "to_dt": f"{to_date} 23:59:59",
    }


def _funnel_counts(from_date, to_date, filters=None):
    counts = {step: 0 for step in DEFAULT_FUNNEL_STEPS}
    if not _doctype_exists("Funnel Step"):
        return counts

    clauses = ["occurred_at >= %(from_dt)s", "occurred_at <= %(to_dt)s"]
    params = {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"}
    filters = filters or {}

    if filters.get("device_type"):
        clauses.append("device_type = %(device_type)s")
        params["device_type"] = filters["device_type"]
    if filters.get("item_group"):
        clauses.append("item_group = %(item_group)s")
        params["item_group"] = filters["item_group"]
    if filters.get("source_channel"):
        clauses.append("source_channel = %(source_channel)s")
        params["source_channel"] = filters["source_channel"]

    where_sql = " AND ".join(clauses)
    rows = frappe.db.sql(
        f"""
        SELECT
            step_name,
            COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS sessions
        FROM `tabFunnel Step`
        WHERE {where_sql}
        GROUP BY step_name
        """,
        params,
        as_dict=True,
    )
    for row in rows:
        step = _safe_str(row.get("step_name"))
        if step in counts:
            counts[step] = cint(row.get("sessions") or 0)
    return counts


def _top_models(from_date, to_date, event_type):
    if not _event_table_available():
        return []

    rows = frappe.db.sql(
        """
        SELECT model_name, COUNT(*) AS count
        FROM `tabAnalytics Event`
        WHERE event_type = %(event_type)s
          AND occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND IFNULL(model_name, '') != ''
        GROUP BY model_name
        ORDER BY count DESC, model_name ASC
        LIMIT 10
        """,
        {
            "event_type": event_type,
            "from_dt": f"{from_date} 00:00:00",
            "to_dt": f"{to_date} 23:59:59",
        },
        as_dict=True,
    )
    return [{"model_name": row.get("model_name"), "count": cint(row.get("count") or 0)} for row in rows]


def _safe_rate(numerator, denominator):
    if not denominator:
        return 0
    return round((flt(numerator) / flt(denominator)) * 100, 2)


def _engagement_metrics(from_date, to_date):
    from_dt = f"{from_date} 00:00:00"
    to_dt = f"{to_date} 23:59:59"

    page_views = 0
    total_sessions = 0
    bounced_sessions = 0
    new_visitors = 0
    returning_visitors = 0

    if _doctype_exists("Page View"):
        totals = frappe.db.sql(
            """
            SELECT
                COUNT(*) AS views,
                COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS sessions
            FROM `tabPage View`
            WHERE entered_at >= %(from_dt)s
              AND entered_at <= %(to_dt)s
            """,
            {"from_dt": from_dt, "to_dt": to_dt},
            as_dict=True,
        )
        row = (totals or [{}])[0]
        page_views = cint(row.get("views") or 0)
        total_sessions = cint(row.get("sessions") or 0)

        bounce_rows = frappe.db.sql(
            """
            SELECT COUNT(*) AS bounced
            FROM (
                SELECT COALESCE(NULLIF(session_id, ''), name) AS sid, COUNT(*) AS pages
                FROM `tabPage View`
                WHERE entered_at >= %(from_dt)s
                  AND entered_at <= %(to_dt)s
                GROUP BY COALESCE(NULLIF(session_id, ''), name)
            ) seq
            WHERE pages = 1
            """,
            {"from_dt": from_dt, "to_dt": to_dt},
            as_dict=True,
        )
        bounced_sessions = cint((bounce_rows or [{}])[0].get("bounced") or 0)
    elif _event_table_available():
        totals = frappe.db.sql(
            """
            SELECT
                COUNT(*) AS views,
                COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS sessions
            FROM `tabAnalytics Event`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
              AND event_type IN ('page_view', 'product_view')
            """,
            {"from_dt": from_dt, "to_dt": to_dt},
            as_dict=True,
        )
        row = (totals or [{}])[0]
        page_views = cint(row.get("views") or 0)
        total_sessions = cint(row.get("sessions") or 0)

        bounce_rows = frappe.db.sql(
            """
            SELECT COUNT(*) AS bounced
            FROM (
                SELECT COALESCE(NULLIF(session_id, ''), name) AS sid, COUNT(*) AS pages
                FROM `tabAnalytics Event`
                WHERE occurred_at >= %(from_dt)s
                  AND occurred_at <= %(to_dt)s
                  AND event_type IN ('page_view', 'product_view')
                GROUP BY COALESCE(NULLIF(session_id, ''), name)
            ) seq
            WHERE pages = 1
            """,
            {"from_dt": from_dt, "to_dt": to_dt},
            as_dict=True,
        )
        bounced_sessions = cint((bounce_rows or [{}])[0].get("bounced") or 0)

    if _event_table_available():
        new_returning_rows = frappe.db.sql(
            """
            SELECT
                SUM(CASE WHEN first_seen >= %(from_dt)s THEN 1 ELSE 0 END) AS new_visitors,
                SUM(CASE WHEN first_seen < %(from_dt)s THEN 1 ELSE 0 END) AS returning_visitors
            FROM (
                SELECT
                    visitor_key,
                    MIN(occurred_at) AS first_seen,
                    MAX(CASE WHEN occurred_at >= %(from_dt)s AND occurred_at <= %(to_dt)s THEN 1 ELSE 0 END) AS has_in_range
                FROM (
                    SELECT
                        COALESCE(NULLIF(user_id, ''), NULLIF(session_id, ''), name) AS visitor_key,
                        occurred_at
                    FROM `tabAnalytics Event`
                    WHERE occurred_at <= %(to_dt)s
                      AND event_type IN ('page_view', 'product_view')
                ) all_rows
                GROUP BY visitor_key
            ) grouped
            WHERE has_in_range = 1
            """,
            {"from_dt": from_dt, "to_dt": to_dt},
            as_dict=True,
        )
        nr = (new_returning_rows or [{}])[0]
        new_visitors = cint(nr.get("new_visitors") or 0)
        returning_visitors = cint(nr.get("returning_visitors") or 0)

    pages_per_session = round(flt(page_views) / flt(total_sessions), 2) if total_sessions else 0
    return {
        "total_sessions": total_sessions,
        "page_views": page_views,
        "pages_per_session": pages_per_session,
        "bounce_rate": _safe_rate(bounced_sessions, total_sessions),
        "bounced_sessions": bounced_sessions,
        "new_visitors": new_visitors,
        "returning_visitors": returning_visitors,
    }


def _summary_metrics(from_date, to_date):
    if not _event_table_available():
        return {
            "views": 0,
            "orders": 0,
            "revenue": 0,
            "conversion_rate": 0,
            "aov": 0,
            "cart_abandonment_rate": 0,
        }

    rows = frappe.db.sql(
        """
        SELECT
            event_type,
            COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS session_count,
            SUM(IFNULL(amount, 0)) AS amount_sum
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND event_type IN ('product_view', 'add_to_cart', 'order_submit')
        GROUP BY event_type
        """,
        {
            "from_dt": f"{from_date} 00:00:00",
            "to_dt": f"{to_date} 23:59:59",
        },
        as_dict=True,
    )
    metrics = {"product_view": {"session_count": 0, "amount_sum": 0}, "add_to_cart": {"session_count": 0, "amount_sum": 0}, "order_submit": {"session_count": 0, "amount_sum": 0}}
    for row in rows:
        evt = _safe_str(row.get("event_type"))
        metrics[evt] = {
            "session_count": cint(row.get("session_count") or 0),
            "amount_sum": flt(row.get("amount_sum") or 0),
        }

    view_sessions = metrics["product_view"]["session_count"]
    cart_sessions = metrics["add_to_cart"]["session_count"]
    order_sessions = metrics["order_submit"]["session_count"]
    revenue = metrics["order_submit"]["amount_sum"]
    aov = revenue / order_sessions if order_sessions else 0
    cart_abandonment = _safe_rate(cart_sessions - order_sessions if cart_sessions >= order_sessions else 0, cart_sessions)

    return {
        "views": view_sessions,
        "orders": order_sessions,
        "revenue": round(revenue, 2),
        "conversion_rate": _safe_rate(order_sessions, view_sessions),
        "aov": round(aov, 2),
        "cart_abandonment_rate": cart_abandonment,
    }


def get_overview_payload(range_key=None, from_date=None, to_date=None):
    require_management_access()
    from_date, to_date, days = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)

    metrics = _summary_metrics(from_date, to_date)
    engagement = _engagement_metrics(from_date, to_date)
    source_breakdown = []
    channel_group_breakdown = []
    if _event_table_available():
        source_counter = defaultdict(int)
        source_sessions = defaultdict(set)
        group_counter = defaultdict(int)
        group_sessions = defaultdict(set)
        for row in _event_rows_for_range(from_date, to_date):
            if row.get("event_type") not in {"page_view", "product_view"}:
                continue
            source = _safe_str(row.get("source_channel")).lower() or "other"
            source_counter[source] += 1
            session_key = _safe_str(row.get("session_id") or row.get("journey_key"))
            if session_key:
                source_sessions[source].add(session_key)

            group_key = _source_channel_group(row)
            group_counter[group_key] += 1
            if session_key:
                group_sessions[group_key].add(session_key)

        source_breakdown = [
            {
                "source_channel": key,
                "views": value,
                "unique_sessions": len(source_sessions.get(key) or set()),
            }
            for key, value in sorted(source_counter.items(), key=lambda item: -item[1])
        ]
        total_group_views = max(1, sum(group_counter.values()))
        channel_group_breakdown = [
            {
                "channel_group": key,
                "views": value,
                "unique_sessions": len(group_sessions.get(key) or set()),
                "share_percent": round((value / total_group_views) * 100, 2),
            }
            for key, value in sorted(group_counter.items(), key=lambda item: -item[1])
        ]

    if not _event_table_available():
        return {
            "range": {"from_date": from_date, "to_date": to_date, "days": days, "timezone": TEHRAN_TIMEZONE},
            "kpis": {
                "total_views": 0,
                "conversion_rate": 0,
                "total_revenue": 0,
                "total_orders": 0,
                "average_order_value": 0,
                "cart_abandonment_rate": 0,
                "total_sessions": engagement["total_sessions"],
                "pages_per_session": engagement["pages_per_session"],
                "bounce_rate": engagement["bounce_rate"],
                "new_visitors": engagement["new_visitors"],
                "returning_visitors": engagement["returning_visitors"],
            },
            "charts": {
                "daily_views": [],
                "weekly_sales_compare": [],
                "traffic_heatmap": [],
                "source_breakdown": [],
                "channel_group_breakdown": [],
            },
        }

    daily_views = frappe.db.sql(
        """
        SELECT DATE(occurred_at) AS day_key, COUNT(*) AS views
        FROM `tabAnalytics Event`
        WHERE event_type = 'product_view'
          AND occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
        GROUP BY DATE(occurred_at)
        ORDER BY day_key ASC
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )

    weekly_sales = frappe.db.sql(
        """
        SELECT YEARWEEK(occurred_at, 1) AS year_week, SUM(IFNULL(amount, 0)) AS revenue
        FROM `tabAnalytics Event`
        WHERE event_type = 'order_submit'
          AND occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
        GROUP BY YEARWEEK(occurred_at, 1)
        ORDER BY year_week ASC
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )
    weekly_sales_compare = []
    for idx, row in enumerate(weekly_sales):
        previous = flt(weekly_sales[idx - 1].get("revenue") or 0) if idx > 0 else 0
        current = flt(row.get("revenue") or 0)
        weekly_sales_compare.append(
            {
                "label": str(row.get("year_week")),
                "current": round(current, 2),
                "previous": round(previous, 2),
            }
        )

    heatmap = frappe.db.sql(
        """
        SELECT WEEKDAY(occurred_at) AS weekday, HOUR(occurred_at) AS hour_of_day, COUNT(*) AS value
        FROM `tabAnalytics Event`
        WHERE event_type = 'product_view'
          AND occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
        GROUP BY WEEKDAY(occurred_at), HOUR(occurred_at)
        ORDER BY weekday ASC, hour_of_day ASC
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": days, "timezone": TEHRAN_TIMEZONE},
        "kpis": {
            "total_views": metrics["views"],
            "conversion_rate": metrics["conversion_rate"],
            "total_revenue": metrics["revenue"],
            "total_orders": metrics["orders"],
            "average_order_value": metrics["aov"],
            "cart_abandonment_rate": metrics["cart_abandonment_rate"],
            "total_sessions": engagement["total_sessions"],
            "pages_per_session": engagement["pages_per_session"],
            "bounce_rate": engagement["bounce_rate"],
            "new_visitors": engagement["new_visitors"],
            "returning_visitors": engagement["returning_visitors"],
        },
        "charts": {
            "daily_views": [
                {"date": str(row.get("day_key")), "value": cint(row.get("views") or 0)}
                for row in daily_views
            ],
            "weekly_sales_compare": weekly_sales_compare,
            "traffic_heatmap": [
                {
                    "weekday": cint(row.get("weekday") or 0),
                    "hour": cint(row.get("hour_of_day") or 0),
                    "value": cint(row.get("value") or 0),
                }
                for row in heatmap
            ],
            "source_breakdown": source_breakdown,
            "channel_group_breakdown": channel_group_breakdown,
        },
    }


def get_conversion_funnel_payload(range_key=None, from_date=None, to_date=None, category=None, device_type=None, source_channel=None):
    require_management_access()
    from_date, to_date, days = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)
    prev_from, prev_to = _resolve_compare_range(from_date, to_date)

    filters = {
        "item_group": _safe_identifier(category),
        "device_type": _safe_identifier(device_type),
        "source_channel": _safe_identifier(source_channel),
    }
    current = _funnel_counts(from_date, to_date, filters=filters)
    previous = _funnel_counts(prev_from, prev_to, filters=filters)

    steps = []
    for idx, step in enumerate(DEFAULT_FUNNEL_STEPS):
        count = current.get(step, 0)
        next_count = current.get(DEFAULT_FUNNEL_STEPS[idx + 1], 0) if idx + 1 < len(DEFAULT_FUNNEL_STEPS) else 0
        drop_percent = _safe_rate(count - next_count if count >= next_count else 0, count) if idx + 1 < len(DEFAULT_FUNNEL_STEPS) else 0
        steps.append(
            {
                "step": step,
                "count": count,
                "drop_percent": drop_percent,
            }
        )

    top_drop_products = []
    if _event_table_available():
        rows = frappe.db.sql(
            """
            SELECT model_name, add_count, order_count
            FROM (
                SELECT
                    model_name,
                    SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_count,
                    SUM(CASE WHEN event_type = 'order_submit' THEN 1 ELSE 0 END) AS order_count
                FROM `tabAnalytics Event`
                WHERE occurred_at >= %(from_dt)s
                  AND occurred_at <= %(to_dt)s
                  AND event_type IN ('add_to_cart', 'order_submit')
                  AND IFNULL(model_name, '') != ''
                GROUP BY model_name
            ) AS grouped
            WHERE add_count > 0
            ORDER BY (add_count - order_count) DESC, add_count DESC
            LIMIT 10
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
            as_dict=True,
        )
        for row in rows:
            add_count = cint(row.get("add_count") or 0)
            order_count = cint(row.get("order_count") or 0)
            drop_count = max(add_count - order_count, 0)
            top_drop_products.append(
                {
                    "model_name": row.get("model_name"),
                    "add_to_cart": add_count,
                    "order_submit": order_count,
                    "drop_count": drop_count,
                    "drop_percent": _safe_rate(drop_count, add_count),
                }
            )

    by_device = []
    for device in ["mobile", "desktop", "tablet", "other"]:
        device_counts = _funnel_counts(from_date, to_date, filters={**filters, "device_type": device})
        by_device.append({"device_type": device, **device_counts})

    by_category = []
    if _event_table_available():
        categories = frappe.db.sql(
            """
            SELECT DISTINCT item_group
            FROM `tabAnalytics Event`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
              AND IFNULL(item_group, '') != ''
            LIMIT 20
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
            as_dict=True,
        )
        for row in categories:
            item_group = row.get("item_group")
            category_counts = _funnel_counts(from_date, to_date, filters={**filters, "item_group": item_group})
            by_category.append({"item_group": item_group, **category_counts})

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": days},
        "compare_range": {"from_date": prev_from, "to_date": prev_to},
        "steps": steps,
        "sessions": current,
        "previous_sessions": previous,
        "conversion_rate": {
            "view_to_cart_percent": _safe_rate(current.get("add_to_cart", 0), current.get("product_view", 0)),
            "cart_to_order_percent": _safe_rate(current.get("order_submit", 0), current.get("add_to_cart", 0)),
            "view_to_order_percent": _safe_rate(current.get("order_submit", 0), current.get("product_view", 0)),
        },
        "top_drop_products": top_drop_products,
        "by_device": by_device,
        "by_category": by_category,
        "top_models": {
            "product_view": _top_models(from_date, to_date, "product_view"),
            "add_to_cart": _top_models(from_date, to_date, "add_to_cart"),
            "order_submit": _top_models(from_date, to_date, "order_submit"),
        },
    }


def get_user_behavior_payload(range_key=None, from_date=None, to_date=None, limit=10):
    require_management_access()
    from_date, to_date, days = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)
    limit = min(max(_to_int(limit, 10), 1), 50)

    if not _event_table_available():
        return {
            "range": {"from_date": from_date, "to_date": to_date, "days": days},
            "entry_sources": [],
            "exit_pages": [],
            "user_flow": [],
            "product_page_analysis": [],
            "cta_actions": {"summary": [], "by_page": []},
            "form_interactions": {"total_submissions": 0, "unique_sessions": 0, "by_form_type": [], "by_page": []},
            "internal_search_terms": [],
            "cart_analysis": {
                "abandoned_products": [],
                "avg_minutes_add_to_order": 0,
                "avg_cart_open_per_session": 0,
            },
        }

    entry_sources = frappe.db.sql(
        """
        SELECT source_channel, COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS sessions
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND event_type IN ('page_view', 'product_view')
        GROUP BY source_channel
        ORDER BY sessions DESC
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )

    exit_pages = []
    if _doctype_exists("Page View"):
        exit_pages = frappe.db.sql(
            """
            SELECT url, COUNT(*) AS exits
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
            GROUP BY url
            ORDER BY exits DESC
            LIMIT %(limit)s
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59", "limit": limit},
            as_dict=True,
        )

    flow_rows = frappe.db.sql(
        """
        SELECT session_id, page_url, occurred_at
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND IFNULL(session_id, '') != ''
          AND IFNULL(page_url, '') != ''
        ORDER BY session_id ASC, occurred_at ASC
        LIMIT 5000
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )
    sequences = defaultdict(list)
    for row in flow_rows:
        sid = row.get("session_id")
        if not sid:
            continue
        page = _safe_str(row.get("page_url"))
        if not page:
            continue
        if not sequences[sid] or sequences[sid][-1] != page:
            sequences[sid].append(page)

    transition_counter = defaultdict(int)
    for pages in sequences.values():
        for idx in range(len(pages) - 1):
            transition_counter[(pages[idx], pages[idx + 1])] += 1
    user_flow = [
        {"from": pair[0], "to": pair[1], "count": count}
        for pair, count in sorted(transition_counter.items(), key=lambda x: -x[1])[:limit]
    ]

    product_views = frappe.db.sql(
        """
        SELECT model_name, COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS view_sessions
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND event_type = 'product_view'
          AND IFNULL(model_name, '') != ''
        GROUP BY model_name
        ORDER BY view_sessions DESC
        LIMIT %(limit)s
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59", "limit": limit},
        as_dict=True,
    )

    image_open_map = {}
    add_to_cart_map = {}
    for event_name, target in [("product_images_open", image_open_map), ("add_to_cart", add_to_cart_map)]:
        rows = frappe.db.sql(
            """
            SELECT model_name, COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS sessions
            FROM `tabAnalytics Event`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
              AND event_type = %(event_name)s
              AND IFNULL(model_name, '') != ''
            GROUP BY model_name
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59", "event_name": event_name},
            as_dict=True,
        )
        for row in rows:
            target[row.get("model_name")] = cint(row.get("sessions") or 0)

    avg_time_map = {}
    scroll_map = {}
    if _doctype_exists("Page View"):
        time_rows = frappe.db.sql(
            """
            SELECT model_name, AVG(IFNULL(time_spent_seconds, 0)) AS avg_time, AVG(IFNULL(scroll_depth, 0)) AS avg_scroll
            FROM `tabPage View`
            WHERE entered_at >= %(from_dt)s
              AND entered_at <= %(to_dt)s
              AND IFNULL(model_name, '') != ''
            GROUP BY model_name
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
            as_dict=True,
        )
        for row in time_rows:
            name = row.get("model_name")
            avg_time_map[name] = round(flt(row.get("avg_time") or 0), 2)
            scroll_map[name] = round(flt(row.get("avg_scroll") or 0), 2)

    product_page_analysis = []
    for row in product_views:
        model_name = row.get("model_name")
        views = cint(row.get("view_sessions") or 0)
        image_sessions = image_open_map.get(model_name, 0)
        add_sessions = add_to_cart_map.get(model_name, 0)
        product_page_analysis.append(
            {
                "model_name": model_name,
                "view_sessions": views,
                "avg_time_spent_seconds": avg_time_map.get(model_name, 0),
                "avg_scroll_depth": scroll_map.get(model_name, 0),
                "images_open_rate": _safe_rate(image_sessions, views),
                "add_to_cart_rate": _safe_rate(add_sessions, views),
            }
        )

    abandoned_products = []
    abandoned_rows = frappe.db.sql(
        """
        SELECT model_name, add_count, order_count
        FROM (
            SELECT
                model_name,
                SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_count,
                SUM(CASE WHEN event_type = 'order_submit' THEN 1 ELSE 0 END) AS order_count
            FROM `tabAnalytics Event`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
              AND event_type IN ('add_to_cart', 'order_submit')
              AND IFNULL(model_name, '') != ''
            GROUP BY model_name
        ) AS grouped
        WHERE add_count > order_count
        ORDER BY (add_count - order_count) DESC
        LIMIT %(limit)s
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59", "limit": limit},
        as_dict=True,
    )
    for row in abandoned_rows:
        add_count = cint(row.get("add_count") or 0)
        order_count = cint(row.get("order_count") or 0)
        abandoned_products.append(
            {
                "model_name": row.get("model_name"),
                "add_to_cart": add_count,
                "order_submit": order_count,
                "abandoned": max(add_count - order_count, 0),
            }
        )

    latency_rows = frappe.db.sql(
        """
        SELECT AVG(TIMESTAMPDIFF(MINUTE, first_add, first_order)) AS avg_minutes
        FROM (
            SELECT
                session_id,
                MIN(CASE WHEN event_type = 'add_to_cart' THEN occurred_at END) AS first_add,
                MIN(CASE WHEN event_type = 'order_submit' THEN occurred_at END) AS first_order
            FROM `tabAnalytics Event`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
              AND IFNULL(session_id, '') != ''
              AND event_type IN ('add_to_cart', 'order_submit')
            GROUP BY session_id
        ) seq
        WHERE first_add IS NOT NULL
          AND first_order IS NOT NULL
          AND first_order >= first_add
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )
    avg_minutes_add_to_order = round(flt((latency_rows or [{}])[0].get("avg_minutes") or 0), 2)

    cart_open_rows = frappe.db.sql(
        """
        SELECT AVG(open_count) AS avg_open_count
        FROM (
            SELECT session_id, COUNT(*) AS open_count
            FROM `tabAnalytics Event`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
              AND event_type = 'cart_open'
              AND IFNULL(session_id, '') != ''
            GROUP BY session_id
        ) opens
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )
    avg_cart_open_per_session = round(flt((cart_open_rows or [{}])[0].get("avg_open_count") or 0), 2)

    cta_rows = frappe.db.sql(
        """
        SELECT event_type, page_url, session_id
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND event_type IN ('call_click', 'whatsapp_click', 'email_click')
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )
    cta_summary_map = {
        "call_click": {"event_type": "call_click", "label": "تماس تلفنی", "clicks": 0, "sessions": set()},
        "whatsapp_click": {"event_type": "whatsapp_click", "label": "واتساپ", "clicks": 0, "sessions": set()},
        "email_click": {"event_type": "email_click", "label": "ایمیل", "clicks": 0, "sessions": set()},
    }
    cta_by_page_map = defaultdict(lambda: {"call_click": 0, "whatsapp_click": 0, "email_click": 0, "sessions": set()})
    for row in cta_rows:
        event_type = _safe_str(row.get("event_type")).lower()
        session_id = _safe_str(row.get("session_id"))
        page_path = _normalize_path(row.get("page_url")) or "/"
        if event_type not in cta_summary_map:
            continue
        cta_summary_map[event_type]["clicks"] += 1
        if session_id:
            cta_summary_map[event_type]["sessions"].add(session_id)
            cta_by_page_map[page_path]["sessions"].add(session_id)
        cta_by_page_map[page_path][event_type] += 1

    cta_summary = [
        {
            "event_type": row.get("event_type"),
            "label": row.get("label"),
            "clicks": cint(row.get("clicks") or 0),
            "sessions": len(row.get("sessions") or set()),
        }
        for row in cta_summary_map.values()
    ]
    cta_by_page = sorted(
        [
            {
                "path": path,
                "call_click": values.get("call_click") or 0,
                "whatsapp_click": values.get("whatsapp_click") or 0,
                "email_click": values.get("email_click") or 0,
                "total_clicks": (values.get("call_click") or 0) + (values.get("whatsapp_click") or 0) + (values.get("email_click") or 0),
                "sessions": len(values.get("sessions") or set()),
            }
            for path, values in cta_by_page_map.items()
        ],
        key=lambda item: -item.get("total_clicks", 0),
    )[:limit]

    form_rows = frappe.db.sql(
        """
        SELECT session_id, page_url, properties_json
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND event_type = 'form_submit'
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )
    form_total = 0
    form_sessions = set()
    form_type_map = defaultdict(lambda: {"submissions": 0, "sessions": set()})
    form_page_map = defaultdict(lambda: {"submissions": 0, "sessions": set(), "types": defaultdict(int)})
    for row in form_rows:
        props = _safe_json(row.get("properties_json"))
        form_type = _safe_str(
            props.get("form_type") or props.get("form_name") or props.get("form") or props.get("type") or "general"
        ).lower()
        page_path = _normalize_path(row.get("page_url")) or "/"
        session_id = _safe_str(row.get("session_id"))

        form_total += 1
        if session_id:
            form_sessions.add(session_id)
            form_type_map[form_type]["sessions"].add(session_id)
            form_page_map[page_path]["sessions"].add(session_id)
        form_type_map[form_type]["submissions"] += 1
        form_page_map[page_path]["submissions"] += 1
        form_page_map[page_path]["types"][form_type] += 1

    form_by_type = sorted(
        [
            {
                "form_type": key,
                "submissions": values.get("submissions") or 0,
                "sessions": len(values.get("sessions") or set()),
            }
            for key, values in form_type_map.items()
        ],
        key=lambda item: -item.get("submissions", 0),
    )[:limit]
    form_by_page = sorted(
        [
            {
                "path": path,
                "submissions": values.get("submissions") or 0,
                "sessions": len(values.get("sessions") or set()),
                "top_form_type": sorted((values.get("types") or {}).items(), key=lambda item: -item[1])[0][0]
                if values.get("types")
                else "general",
            }
            for path, values in form_page_map.items()
        ],
        key=lambda item: -item.get("submissions", 0),
    )[:limit]

    search_rows = frappe.db.sql(
        """
        SELECT page_url, properties_json
        FROM `tabAnalytics Event`
        WHERE occurred_at >= %(from_dt)s
          AND occurred_at <= %(to_dt)s
          AND event_type = 'site_search'
        LIMIT 5000
        """,
        {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
        as_dict=True,
    )
    search_terms_counter = defaultdict(int)
    for row in search_rows:
        props = _safe_json(row.get("properties_json"))
        page_url = _safe_str(row.get("page_url"))
        term = _safe_str(
            props.get("query")
            or props.get("search_term")
            or props.get("term")
            or props.get("keyword")
            or _query_param(page_url, "q")
            or _query_param(page_url, "query")
        ).lower()
        if term:
            search_terms_counter[term] += 1
    internal_search_terms = [
        {"term": term, "count": count}
        for term, count in sorted(search_terms_counter.items(), key=lambda item: -item[1])[:limit]
    ]

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": days},
        "entry_sources": [
            {"source_channel": row.get("source_channel") or "direct", "sessions": cint(row.get("sessions") or 0)}
            for row in entry_sources
        ],
        "exit_pages": [{"url": row.get("url"), "exits": cint(row.get("exits") or 0)} for row in exit_pages],
        "user_flow": user_flow,
        "product_page_analysis": product_page_analysis,
        "cta_actions": {"summary": cta_summary, "by_page": cta_by_page},
        "form_interactions": {
            "total_submissions": form_total,
            "unique_sessions": len(form_sessions),
            "by_form_type": form_by_type,
            "by_page": form_by_page,
        },
        "internal_search_terms": internal_search_terms,
        "cart_analysis": {
            "abandoned_products": abandoned_products,
            "avg_minutes_add_to_order": avg_minutes_add_to_order,
            "avg_cart_open_per_session": avg_cart_open_per_session,
        },
    }


def get_site_traffic_payload(range_key=None, from_date=None, to_date=None, group_key=None, page_path=None, limit=20):
    require_management_access()
    from_date, to_date, days = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)
    limit = min(max(_to_int(limit, 20), 5), 200)
    engagement = _engagement_metrics(from_date, to_date)

    base_payload = {
        "range": {"from_date": from_date, "to_date": to_date, "days": days},
        "totals": {
            "views": 0,
            "unique_sessions": 0,
            "avg_time_spent_seconds": 0,
            "avg_scroll_depth": 0,
            "total_sessions": engagement.get("total_sessions") or 0,
            "pages_per_session": engagement.get("pages_per_session") or 0,
            "bounce_rate": engagement.get("bounce_rate") or 0,
            "new_visitors": engagement.get("new_visitors") or 0,
            "returning_visitors": engagement.get("returning_visitors") or 0,
        },
        "charts": {
            "daily_views": [],
            "source_breakdown": [],
            "channel_group_breakdown": [],
        },
        "group_summary": [],
        "selected_group": {
            "group_key": _safe_identifier(group_key) or "",
            "label": "",
            "root_path": "",
            "views": 0,
            "unique_sessions": 0,
            "avg_time_spent_seconds": 0,
            "avg_scroll_depth": 0,
            "pages": [],
        },
        "top_pages": [],
        "available_pages": [],
        "selected_page": {
            "path": _normalize_path(page_path) or "",
            "exists": False,
            "metrics": {
                "views": 0,
                "unique_sessions": 0,
                "avg_time_spent_seconds": 0,
                "avg_scroll_depth": 0,
                "exits": 0,
                "exit_rate": 0,
                "landing_sessions": 0,
                "landing_conversions": 0,
                "landing_conversion_rate": 0,
                "bounced_sessions": 0,
                "bounce_rate": 0,
            },
            "daily_views": [],
            "source_breakdown": [],
            "channel_group_breakdown": [],
        },
    }

    if not _doctype_exists("Page View"):
        return base_payload

    params = {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"}

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
        "total_sessions": engagement.get("total_sessions") or 0,
        "pages_per_session": engagement.get("pages_per_session") or 0,
        "bounce_rate": engagement.get("bounce_rate") or 0,
        "new_visitors": engagement.get("new_visitors") or 0,
        "returning_visitors": engagement.get("returning_visitors") or 0,
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
        path = _normalize_path(row.get("raw_path"))
        if not path:
            continue
        exit_map[path] = exit_map.get(path, 0) + cint(row.get("exits") or 0)

    merged = {}
    for row in route_rows:
        path = _normalize_path(row.get("raw_path"))
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

    route_stats = []
    for path, row in merged.items():
        views = max(cint(row.get("views") or 0), 1)
        exits = exit_map.get(path, 0)
        route_stats.append(
            {
                "path": path,
                "views": cint(row.get("views") or 0),
                "unique_sessions": cint(row.get("unique_sessions") or 0),
                "avg_time_spent_seconds": round((row.get("_time_weighted") or 0) / views, 2),
                "avg_scroll_depth": round((row.get("_scroll_weighted") or 0) / views, 2),
                "exits": exits,
                "exit_rate": round((exits / views) * 100, 2),
            }
        )
    route_stats = sorted(route_stats, key=lambda item: (-(item.get("views") or 0), item.get("path") or ""))

    order_sessions = set()
    if _event_table_available():
        order_rows = frappe.db.sql(
            """
            SELECT DISTINCT session_id
            FROM `tabAnalytics Event`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
              AND event_type = 'order_submit'
              AND IFNULL(session_id, '') != ''
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
            as_dict=True,
        )
        order_sessions = {row.get("session_id") for row in order_rows if row.get("session_id")}

    landing_rows = frappe.db.sql(
        """
        SELECT
            seq.session_id,
            MIN(SUBSTRING_INDEX(IFNULL(pv.url, ''), '?', 1)) AS landing_path,
            MAX(seq.page_count) AS page_count
        FROM (
            SELECT
                session_id,
                MIN(entered_at) AS first_ts,
                COUNT(*) AS page_count
            FROM `tabPage View`
            WHERE entered_at >= %(from_dt)s
              AND entered_at <= %(to_dt)s
              AND IFNULL(session_id, '') != ''
            GROUP BY session_id
        ) seq
        INNER JOIN `tabPage View` pv
            ON pv.session_id = seq.session_id
           AND pv.entered_at = seq.first_ts
        GROUP BY seq.session_id
        """,
        params,
        as_dict=True,
    )
    landing_map = defaultdict(lambda: {"landing_sessions": 0, "landing_conversions": 0, "bounced_sessions": 0})
    for row in landing_rows:
        path = _normalize_path(row.get("landing_path"))
        sid = _safe_str(row.get("session_id"))
        if not path or not sid:
            continue
        bucket = landing_map[path]
        bucket["landing_sessions"] += 1
        if cint(row.get("page_count") or 0) <= 1:
            bucket["bounced_sessions"] += 1
        if sid in order_sessions:
            bucket["landing_conversions"] += 1

    for row in route_stats:
        landing = landing_map.get(row.get("path")) or {}
        landing_sessions = cint(landing.get("landing_sessions") or 0)
        landing_conversions = cint(landing.get("landing_conversions") or 0)
        bounced_sessions = cint(landing.get("bounced_sessions") or 0)
        row["landing_sessions"] = landing_sessions
        row["landing_conversions"] = landing_conversions
        row["landing_conversion_rate"] = _safe_rate(landing_conversions, landing_sessions)
        row["bounced_sessions"] = bounced_sessions
        row["bounce_rate"] = _safe_rate(bounced_sessions, landing_sessions)

    channel_group_breakdown = []
    channel_group_by_path = defaultdict(lambda: defaultdict(lambda: {"views": 0, "sessions": set()}))
    if _event_table_available():
        group_counter = defaultdict(int)
        group_sessions = defaultdict(set)
        for event_row in _event_rows_for_range(from_date, to_date):
            if event_row.get("event_type") not in {"page_view", "product_view"}:
                continue
            group_key = _source_channel_group(event_row)
            group_counter[group_key] += 1
            session_key = _safe_str(event_row.get("session_id") or event_row.get("journey_key"))
            if session_key:
                group_sessions[group_key].add(session_key)

            path = _normalize_path(event_row.get("page_url"))
            if path:
                channel_group_by_path[path][group_key]["views"] += 1
                if session_key:
                    channel_group_by_path[path][group_key]["sessions"].add(session_key)

        total_group_views = max(1, sum(group_counter.values()))
        channel_group_breakdown = [
            {
                "channel_group": key,
                "views": value,
                "unique_sessions": len(group_sessions.get(key) or set()),
                "share_percent": round((value / total_group_views) * 100, 2),
            }
            for key, value in sorted(group_counter.items(), key=lambda item: -item[1])
        ]

    grouped_map = {}
    for row in route_stats:
        meta = _path_group_meta(row.get("path"))
        key = meta["group_key"]
        bucket = grouped_map.setdefault(
            key,
            {
                "group_key": key,
                "label": meta["label"],
                "root_path": meta["root_path"],
                "views": 0,
                "unique_sessions": 0,
                "_time_weighted": 0,
                "_scroll_weighted": 0,
                "pages": [],
            },
        )
        views = cint(row.get("views") or 0)
        bucket["views"] += views
        bucket["unique_sessions"] += cint(row.get("unique_sessions") or 0)
        bucket["_time_weighted"] += flt(row.get("avg_time_spent_seconds") or 0) * views
        bucket["_scroll_weighted"] += flt(row.get("avg_scroll_depth") or 0) * views
        bucket["pages"].append(row)

    groups = []
    for key, bucket in grouped_map.items():
        views = max(cint(bucket.get("views") or 0), 1)
        groups.append(
            {
                "group_key": key,
                "label": bucket.get("label"),
                "root_path": bucket.get("root_path"),
                "views": cint(bucket.get("views") or 0),
                "unique_sessions": cint(bucket.get("unique_sessions") or 0),
                "avg_time_spent_seconds": round((bucket.get("_time_weighted") or 0) / views, 2),
                "avg_scroll_depth": round((bucket.get("_scroll_weighted") or 0) / views, 2),
                "pages": sorted(bucket.get("pages") or [], key=lambda item: (-(item.get("views") or 0), item.get("path") or "")),
            }
        )
    groups = sorted(groups, key=lambda item: (-(item.get("views") or 0), item.get("label") or ""))

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
    base_payload["charts"]["daily_views"] = [
        {"date": str(row.get("day_key")), "views": cint(row.get("views") or 0)}
        for row in daily_rows
    ]

    source_rows = frappe.db.sql(
        """
        SELECT
            IFNULL(source_channel, 'other') AS source_channel,
            COUNT(*) AS views,
            COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS unique_sessions
        FROM `tabPage View`
        WHERE entered_at >= %(from_dt)s
          AND entered_at <= %(to_dt)s
        GROUP BY IFNULL(source_channel, 'other')
        ORDER BY views DESC
        """,
        params,
        as_dict=True,
    )
    base_payload["charts"]["source_breakdown"] = [
        {
            "source_channel": row.get("source_channel") or "other",
            "views": cint(row.get("views") or 0),
            "unique_sessions": cint(row.get("unique_sessions") or 0),
        }
        for row in source_rows
    ]
    base_payload["charts"]["channel_group_breakdown"] = channel_group_breakdown

    selected_group_key = _safe_identifier(group_key) or ""
    show_all_mode = selected_group_key in {"__all__", "all"}
    selected_group = None
    if show_all_mode:
        selected_group = {
            "group_key": "__all__",
            "label": "همه صفحات",
            "root_path": "/mysite",
            "views": sum(cint(row.get("views") or 0) for row in route_stats),
            "unique_sessions": sum(cint(row.get("unique_sessions") or 0) for row in route_stats),
            "avg_time_spent_seconds": 0,
            "avg_scroll_depth": 0,
            "pages": route_stats,
        }
    else:
        if selected_group_key:
            selected_group = next((row for row in groups if row.get("group_key") == selected_group_key), None)
        if not selected_group:
            selected_group = groups[0] if groups else None

    selected_group_pages = (selected_group or {}).get("pages") or route_stats

    selected_path = _normalize_path(page_path)
    if not selected_path:
        if selected_group_pages:
            selected_path = selected_group_pages[0]["path"]
        else:
            selected_path = route_stats[0]["path"] if route_stats else "/mysite"

    selected_metrics = next((row for row in route_stats if row.get("path") == selected_path), None)

    selected_daily_rows = frappe.db.sql(
        """
        SELECT DATE(entered_at) AS day_key, SUBSTRING_INDEX(IFNULL(url, ''), '?', 1) AS raw_path, COUNT(*) AS views
        FROM `tabPage View`
        WHERE entered_at >= %(from_dt)s
          AND entered_at <= %(to_dt)s
          AND IFNULL(url, '') != ''
        GROUP BY DATE(entered_at), SUBSTRING_INDEX(IFNULL(url, ''), '?', 1)
        ORDER BY day_key ASC
        """,
        params,
        as_dict=True,
    )
    selected_daily_map = defaultdict(int)
    for row in selected_daily_rows:
        if _normalize_path(row.get("raw_path")) != selected_path:
            continue
        selected_daily_map[str(row.get("day_key"))] += cint(row.get("views") or 0)
    selected_daily = [
        {"date": day_key, "views": count}
        for day_key, count in sorted(selected_daily_map.items(), key=lambda item: item[0])
    ]

    selected_source_rows = frappe.db.sql(
        """
        SELECT
            SUBSTRING_INDEX(IFNULL(url, ''), '?', 1) AS raw_path,
            IFNULL(source_channel, 'other') AS source_channel,
            COUNT(*) AS views,
            COUNT(DISTINCT COALESCE(NULLIF(session_id, ''), name)) AS unique_sessions
        FROM `tabPage View`
        WHERE entered_at >= %(from_dt)s
          AND entered_at <= %(to_dt)s
          AND IFNULL(url, '') != ''
        GROUP BY SUBSTRING_INDEX(IFNULL(url, ''), '?', 1), IFNULL(source_channel, 'other')
        """,
        params,
        as_dict=True,
    )
    selected_source_map = {}
    for row in selected_source_rows:
        if _normalize_path(row.get("raw_path")) != selected_path:
            continue
        channel = row.get("source_channel") or "other"
        bucket = selected_source_map.setdefault(channel, {"source_channel": channel, "views": 0, "unique_sessions": 0})
        bucket["views"] += cint(row.get("views") or 0)
        bucket["unique_sessions"] += cint(row.get("unique_sessions") or 0)
    selected_source_breakdown = sorted(selected_source_map.values(), key=lambda item: -(item.get("views") or 0))
    selected_channel_group_breakdown = []
    if selected_path and channel_group_by_path.get(selected_path):
        grouped = channel_group_by_path.get(selected_path) or {}
        total_views = max(1, sum(cint(values.get("views") or 0) for values in grouped.values()))
        selected_channel_group_breakdown = sorted(
            [
                {
                    "channel_group": key,
                    "views": cint(values.get("views") or 0),
                    "unique_sessions": len(values.get("sessions") or set()),
                    "share_percent": round((cint(values.get("views") or 0) / total_views) * 100, 2),
                }
                for key, values in grouped.items()
            ],
            key=lambda item: -(item.get("views") or 0),
        )

    base_payload["group_summary"] = [
        {
            "group_key": row.get("group_key"),
            "label": row.get("label"),
            "root_path": row.get("root_path"),
            "views": cint(row.get("views") or 0),
            "unique_sessions": cint(row.get("unique_sessions") or 0),
            "avg_time_spent_seconds": round(flt(row.get("avg_time_spent_seconds") or 0), 2),
            "avg_scroll_depth": round(flt(row.get("avg_scroll_depth") or 0), 2),
            "pages_count": len(row.get("pages") or []),
        }
        for row in groups
    ]
    base_payload["selected_group"] = {
        "group_key": (selected_group or {}).get("group_key") or "",
        "label": (selected_group or {}).get("label") or "",
        "root_path": (selected_group or {}).get("root_path") or "",
        "views": cint((selected_group or {}).get("views") or 0),
        "unique_sessions": cint((selected_group or {}).get("unique_sessions") or 0),
        "avg_time_spent_seconds": round(flt((selected_group or {}).get("avg_time_spent_seconds") or 0), 2),
        "avg_scroll_depth": round(flt((selected_group or {}).get("avg_scroll_depth") or 0), 2),
        "pages": selected_group_pages[:limit],
    }
    base_payload["top_pages"] = route_stats[:limit]
    base_payload["available_pages"] = [{"path": row.get("path"), "views": cint(row.get("views") or 0)} for row in route_stats[:200]]
    selected_metrics_payload = {
        "path": selected_path,
        "views": 0,
        "unique_sessions": 0,
        "avg_time_spent_seconds": 0,
        "avg_scroll_depth": 0,
        "exits": 0,
        "exit_rate": 0,
        "landing_sessions": 0,
        "landing_conversions": 0,
        "landing_conversion_rate": 0,
        "bounced_sessions": 0,
        "bounce_rate": 0,
    }
    if selected_metrics:
        selected_metrics_payload.update(selected_metrics)
    base_payload["selected_page"] = {
        "path": selected_path,
        "exists": bool(selected_metrics),
        "metrics": selected_metrics_payload,
        "daily_views": selected_daily,
        "source_breakdown": selected_source_breakdown,
        "channel_group_breakdown": selected_channel_group_breakdown,
    }
    return base_payload


def get_products_report_payload(range_key=None, from_date=None, to_date=None, category=None, sort_by="views", sort_order="desc", page=1, page_size=20):
    require_management_access()
    from_date, to_date, days = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)
    page = max(_to_int(page, 1), 1)
    page_size = min(max(_to_int(page_size, 20), 1), 100)

    if not _event_table_available():
        return {
            "range": {"from_date": from_date, "to_date": to_date, "days": days},
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 1,
            "charts": {"top_selling": [], "top_viewed_low_buy": [], "new_vs_old": []},
        }

    params = {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"}
    where = ["occurred_at >= %(from_dt)s", "occurred_at <= %(to_dt)s", "IFNULL(model_name, '') != ''"]
    if category:
        where.append("item_group = %(item_group)s")
        params["item_group"] = category

    base_rows = frappe.db.sql(
        f"""
        SELECT
            model_name,
            IFNULL(item_group, '') AS item_group,
            SUM(CASE WHEN event_type = 'product_view' THEN 1 ELSE 0 END) AS views,
            SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
            SUM(CASE WHEN event_type = 'order_submit' THEN 1 ELSE 0 END) AS purchases,
            SUM(CASE WHEN event_type = 'order_submit' THEN IFNULL(amount, 0) ELSE 0 END) AS revenue
        FROM `tabAnalytics Event`
        WHERE {' AND '.join(where)}
        GROUP BY model_name, item_group
        """,
        params,
        as_dict=True,
    )

    decision_rows = frappe.db.sql(
        f"""
        SELECT model_name, AVG(TIMESTAMPDIFF(MINUTE, first_view, first_order)) AS avg_minutes
        FROM (
            SELECT
                session_id,
                model_name,
                MIN(CASE WHEN event_type = 'product_view' THEN occurred_at END) AS first_view,
                MIN(CASE WHEN event_type = 'order_submit' THEN occurred_at END) AS first_order
            FROM `tabAnalytics Event`
            WHERE {' AND '.join(where)}
              AND IFNULL(session_id, '') != ''
              AND event_type IN ('product_view', 'order_submit')
            GROUP BY session_id, model_name
        ) decision
        WHERE first_view IS NOT NULL
          AND first_order IS NOT NULL
          AND first_order >= first_view
        GROUP BY model_name
        """,
        params,
        as_dict=True,
    )
    decision_map = {row.get("model_name"): round(flt(row.get("avg_minutes") or 0), 2) for row in decision_rows}

    rows = []
    for row in base_rows:
        views = cint(row.get("views") or 0)
        purchases = cint(row.get("purchases") or 0)
        payload = {
            "model_name": row.get("model_name"),
            "item_group": row.get("item_group") or "",
            "views": views,
            "add_to_cart": cint(row.get("add_to_cart") or 0),
            "purchases": purchases,
            "conversion_rate": _safe_rate(purchases, views),
            "revenue": round(flt(row.get("revenue") or 0), 2),
            "avg_decision_minutes": decision_map.get(row.get("model_name"), 0),
        }
        rows.append(payload)

    allowed_sort = {
        "model_name",
        "item_group",
        "views",
        "add_to_cart",
        "purchases",
        "conversion_rate",
        "revenue",
        "avg_decision_minutes",
    }
    sort_key = sort_by if sort_by in allowed_sort else "views"
    reverse = str(sort_order).lower() != "asc"
    rows = sorted(rows, key=lambda item: item.get(sort_key) or 0, reverse=reverse)

    total = len(rows)
    start = (page - 1) * page_size
    end = start + page_size
    paged = rows[start:end]

    top_selling = sorted(rows, key=lambda item: (item["purchases"], item["revenue"]), reverse=True)[:10]
    top_viewed_low_buy = sorted(rows, key=lambda item: (item["views"], -item["purchases"]), reverse=True)[:10]

    new_vs_old = []
    if rows:
        model_names = [row["model_name"] for row in rows if row.get("model_name")]
        age_map = {}
        if _doctype_exists("Item Variant Attribute") and model_names:
            placeholders = ", ".join(["%s"] * len(model_names))
            age_rows = frappe.db.sql(
                f"""
                SELECT iva.attribute_value AS model_name, MIN(i.creation) AS first_seen
                FROM `tabItem Variant Attribute` iva
                INNER JOIN `tabItem` i ON i.name = iva.parent
                WHERE iva.attribute = 'مدل محصول'
                  AND iva.attribute_value IN ({placeholders})
                GROUP BY iva.attribute_value
                """,
                tuple(model_names),
                as_dict=True,
            )
            for row in age_rows:
                age_map[row.get("model_name")] = row.get("first_seen")

        split_date = add_days(getdate(nowdate()), -90)
        bucket = {"new": {"label": "جدید", "purchases": 0, "revenue": 0}, "old": {"label": "قدیمی", "purchases": 0, "revenue": 0}}
        for row in rows:
            model_name = row.get("model_name")
            first_seen = age_map.get(model_name)
            bucket_key = "new"
            if first_seen:
                try:
                    bucket_key = "new" if getdate(first_seen) >= split_date else "old"
                except Exception:
                    bucket_key = "old"
            else:
                bucket_key = "old"
            bucket[bucket_key]["purchases"] += row.get("purchases") or 0
            bucket[bucket_key]["revenue"] += row.get("revenue") or 0

        new_vs_old = [bucket["new"], bucket["old"]]

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": days},
        "items": paged,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max((total + page_size - 1) // page_size, 1),
        "charts": {
            "top_selling": top_selling,
            "top_viewed_low_buy": top_viewed_low_buy,
            "new_vs_old": new_vs_old,
        },
    }


def export_products_report_payload(file_type="xlsx", **filters):
    payload = get_products_report_payload(page=1, page_size=5000, **filters)
    rows = payload.get("items") or []

    header = [
        "Model Name",
        "Category",
        "Views",
        "Add To Cart",
        "Purchases",
        "Conversion Rate (%)",
        "Revenue",
        "Avg Decision (min)",
    ]
    matrix = [header]
    for row in rows:
        matrix.append(
            [
                row.get("model_name"),
                row.get("item_group"),
                row.get("views"),
                row.get("add_to_cart"),
                row.get("purchases"),
                row.get("conversion_rate"),
                row.get("revenue"),
                row.get("avg_decision_minutes"),
            ]
        )

    ext = str(file_type or "xlsx").lower()
    filename = f"analytics_products_{now_datetime().strftime('%Y%m%d_%H%M%S')}"

    if ext == "csv":
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerows(matrix)
        frappe.response.filename = f"{filename}.csv"
        frappe.response.filecontent = stream.getvalue()
        frappe.response.type = "download"
        return {"ok": True, "filename": frappe.response.filename}

    from frappe.utils.xlsxutils import make_xlsx

    xlsx_data = make_xlsx(matrix, "Products Report")
    frappe.response.filename = f"{filename}.xlsx"
    frappe.response.filecontent = xlsx_data.getvalue()
    frappe.response.type = "download"
    return {"ok": True, "filename": frappe.response.filename}


def get_time_comparison_payload(
    left_from=None,
    left_to=None,
    right_from=None,
    right_to=None,
    preset="week_vs_previous",
):
    require_management_access()

    today = getdate(nowdate())
    if not (left_from and left_to and right_from and right_to):
        if preset == "month_vs_previous":
            left_to = str(today)
            left_from = str(add_days(today, -29))
            right_to = str(add_days(getdate(left_from), -1))
            right_from = str(add_days(getdate(right_to), -29))
        elif preset == "year_same_period":
            left_to = str(today)
            left_from = str(add_days(today, -29))
            right_from = str(add_days(getdate(left_from), -365))
            right_to = str(add_days(getdate(left_to), -365))
        else:
            left_to = str(today)
            left_from = str(add_days(today, -6))
            right_to = str(add_days(getdate(left_from), -1))
            right_from = str(add_days(getdate(right_to), -6))

    left_metrics = _summary_metrics(left_from, left_to)
    right_metrics = _summary_metrics(right_from, right_to)

    def _delta(current, previous):
        if not previous:
            return 0
        return round(((current - previous) / previous) * 100, 2)

    overlay = {"left": [], "right": []}
    if _event_table_available():
        for side, from_date, to_date in [
            ("left", left_from, left_to),
            ("right", right_from, right_to),
        ]:
            rows = frappe.db.sql(
                """
                SELECT DATE(occurred_at) AS day_key, SUM(CASE WHEN event_type = 'order_submit' THEN IFNULL(amount, 0) ELSE 0 END) AS revenue
                FROM `tabAnalytics Event`
                WHERE occurred_at >= %(from_dt)s
                  AND occurred_at <= %(to_dt)s
                GROUP BY DATE(occurred_at)
                ORDER BY day_key ASC
                """,
                {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
                as_dict=True,
            )
            overlay[side] = [
                {"date": str(row.get("day_key")), "revenue": round(flt(row.get("revenue") or 0), 2)}
                for row in rows
            ]

    return {
        "left_range": {"from_date": left_from, "to_date": left_to},
        "right_range": {"from_date": right_from, "to_date": right_to},
        "left": left_metrics,
        "right": right_metrics,
        "delta": {
            "views": _delta(left_metrics["views"], right_metrics["views"]),
            "orders": _delta(left_metrics["orders"], right_metrics["orders"]),
            "revenue": _delta(left_metrics["revenue"], right_metrics["revenue"]),
            "conversion_rate": _delta(left_metrics["conversion_rate"], right_metrics["conversion_rate"]),
            "aov": _delta(left_metrics["aov"], right_metrics["aov"]),
            "cart_abandonment_rate": _delta(left_metrics["cart_abandonment_rate"], right_metrics["cart_abandonment_rate"]),
        },
        "overlay": overlay,
    }


def _load_goal_definitions(active_only=True):
    rows = []
    if _doctype_exists("Analytics Funnel Definition"):
        filters = {"is_active": 1} if active_only else None
        rows = frappe.get_all(
            "Analytics Funnel Definition",
            filters=filters,
            fields=["name", "title", "is_active", "is_default", "steps_json"],
            order_by="is_default desc, title asc",
            limit_page_length=0,
        )
    if not rows:
        rows = [
            {
                "name": "default-goal",
                "title": "قیف اصلی",
                "is_active": 1,
                "is_default": 1,
                "steps_json": json.dumps(DEFAULT_GOAL_STEPS),
            }
        ]
    return _normalize_goal_rows(rows, ensure_default=True)


def _build_goals_report_from_events(events, goals):
    journeys = defaultdict(list)
    for row in events:
        journeys[row.get("journey_key")].append(row.get("event_type"))

    results = []
    for goal in goals:
        steps = goal.get("steps") or list(DEFAULT_FUNNEL_STEPS)
        aliases = [_goal_step_aliases(step) for step in steps]
        sessions_per_step = [0 for _ in steps]
        matched_journeys = 0

        for event_sequence in journeys.values():
            cursor = -1
            matched = 0
            for step_aliases in aliases:
                found = False
                for idx in range(cursor + 1, len(event_sequence)):
                    if _safe_str(event_sequence[idx]).lower() in step_aliases:
                        found = True
                        cursor = idx
                        break
                if not found:
                    break
                matched += 1
            if matched:
                matched_journeys += 1
                for step_idx in range(matched):
                    sessions_per_step[step_idx] += 1

        steps_payload = []
        for idx, step in enumerate(steps):
            count = sessions_per_step[idx]
            prev = sessions_per_step[idx - 1] if idx > 0 else sessions_per_step[0] if sessions_per_step else 0
            drop = _safe_rate(prev - count if prev >= count else 0, prev) if idx > 0 else 0
            steps_payload.append(
                {
                    "step": step,
                    "sessions": count,
                    "drop_percent": round(drop, 2),
                }
            )

        first_step = sessions_per_step[0] if sessions_per_step else 0
        conversions = sessions_per_step[-1] if sessions_per_step else 0
        results.append(
            {
                "name": goal.get("name"),
                "title": goal.get("title") or "قیف",
                "is_default": cint(goal.get("is_default") or 0),
                "total_journeys": matched_journeys,
                "conversion_sessions": conversions,
                "conversion_rate": _safe_rate(conversions, first_step),
                "steps": steps_payload,
            }
        )

    return sorted(results, key=lambda item: (-(item.get("conversion_sessions") or 0), item.get("title") or ""))


def _build_cohort_retention_from_events(events):
    visitor_days = defaultdict(set)
    for row in events:
        visitor_key = _safe_str(row.get("visitor_key"))
        occurred_at = row.get("occurred_at")
        if not visitor_key or not occurred_at:
            continue
        day_key = getdate(occurred_at)
        visitor_days[visitor_key].add(day_key)

    cohorts = defaultdict(lambda: {"cohort_size": 0, "retained_7": 0, "retained_30": 0, "retained_90": 0})
    for _, days in visitor_days.items():
        if not days:
            continue
        first_day = min(days)
        cohort_start = first_day - timedelta(days=first_day.weekday())
        revisit_offsets = [(day - first_day).days for day in days if day > first_day]
        has_7 = any(1 <= diff <= 7 for diff in revisit_offsets)
        has_30 = any(1 <= diff <= 30 for diff in revisit_offsets)
        has_90 = any(1 <= diff <= 90 for diff in revisit_offsets)

        bucket = cohorts[str(cohort_start)]
        bucket["cohort_size"] += 1
        bucket["retained_7"] += 1 if has_7 else 0
        bucket["retained_30"] += 1 if has_30 else 0
        bucket["retained_90"] += 1 if has_90 else 0

    rows = []
    for cohort_start, row in sorted(cohorts.items(), key=lambda item: item[0], reverse=True):
        size = row.get("cohort_size") or 0
        rows.append(
            {
                "cohort_start": cohort_start,
                "cohort_size": size,
                "retained_7": row.get("retained_7") or 0,
                "retained_30": row.get("retained_30") or 0,
                "retained_90": row.get("retained_90") or 0,
                "retention_7_rate": _safe_rate(row.get("retained_7") or 0, size),
                "retention_30_rate": _safe_rate(row.get("retained_30") or 0, size),
                "retention_90_rate": _safe_rate(row.get("retained_90") or 0, size),
            }
        )

    overall_size = sum(item.get("cohort_size") or 0 for item in rows)
    return {
        "cohorts": rows[:16],
        "overall": {
            "cohort_size": overall_size,
            "retention_7_rate": _safe_rate(sum(item.get("retained_7") or 0 for item in rows), overall_size),
            "retention_30_rate": _safe_rate(sum(item.get("retained_30") or 0 for item in rows), overall_size),
            "retention_90_rate": _safe_rate(sum(item.get("retained_90") or 0 for item in rows), overall_size),
        },
    }


def _touch_key(row):
    utm_source = _safe_str(row.get("utm_source")).lower()
    utm_medium = _safe_str(row.get("utm_medium")).lower()
    utm_campaign = _safe_str(row.get("utm_campaign")).lower()
    utm_term = _safe_str(row.get("utm_term")).lower()
    utm_content = _safe_str(row.get("utm_content")).lower()

    if any([utm_source, utm_medium, utm_campaign, utm_term, utm_content]):
        key = f"utm::{utm_source}|{utm_medium}|{utm_campaign}|{utm_term}|{utm_content}"
        label = utm_campaign or "کمپین UTM"
        if utm_source and utm_medium:
            label = f"{utm_source} / {utm_medium}" if not utm_campaign else f"{utm_campaign} ({utm_source}/{utm_medium})"
        return (
            key,
            label,
            {
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_term": utm_term,
                "utm_content": utm_content,
                "source_channel": _safe_str(row.get("source_channel") or "other").lower(),
            },
        )

    source = _safe_str(row.get("source_channel") or "other").lower() or "other"
    return (
        f"source::{source}",
        source,
        {
            "utm_source": "",
            "utm_medium": "",
            "utm_campaign": "",
            "utm_term": "",
            "utm_content": "",
            "source_channel": source,
        },
    )


def _build_attribution_from_events(events):
    by_journey = defaultdict(list)
    for row in events:
        by_journey[row.get("journey_key")].append(row)

    first_touch = defaultdict(lambda: {"label": "", "conversions": 0, "revenue": 0.0})
    last_touch = defaultdict(lambda: {"label": "", "conversions": 0, "revenue": 0.0})
    conversions_total = 0
    revenue_total = 0.0

    for rows in by_journey.values():
        ordered = sorted(rows, key=lambda row: row.get("occurred_at") or now_datetime())
        for idx, row in enumerate(ordered):
            if row.get("event_type") != "order_submit":
                continue
            conversions_total += 1
            amount = flt(row.get("amount") or 0)
            revenue_total += amount
            history = ordered[: idx + 1]
            first = history[0] if history else row
            last = history[-1] if history else row

            first_key, first_label, first_meta = _touch_key(first)
            last_key, last_label, last_meta = _touch_key(last)

            first_bucket = first_touch[first_key]
            first_bucket["label"] = first_label
            first_bucket["conversions"] += 1
            first_bucket["revenue"] += amount
            for key, value in first_meta.items():
                first_bucket[key] = value

            last_bucket = last_touch[last_key]
            last_bucket["label"] = last_label
            last_bucket["conversions"] += 1
            last_bucket["revenue"] += amount
            for key, value in last_meta.items():
                last_bucket[key] = value

    def _sorted_touch(payload):
        rows = sorted(payload.values(), key=lambda item: (-(item.get("conversions") or 0), -(item.get("revenue") or 0)))
        for row in rows:
            row["conversion_share"] = _safe_rate(row.get("conversions") or 0, conversions_total)
            row["revenue"] = round(flt(row.get("revenue") or 0), 2)
        return rows[:10]

    return {
        "conversions_total": conversions_total,
        "revenue_total": round(revenue_total, 2),
        "first_touch": _sorted_touch(first_touch),
        "last_touch": _sorted_touch(last_touch),
    }


def _build_data_quality_from_events(events):
    total = len(events)
    if not total:
        return {
            "total_events": 0,
            "duplicate_events": 0,
            "rapid_duplicate_events": 0,
            "bot_events": 0,
            "internal_events": 0,
            "missing_session_events": 0,
            "quality_score": 100.0,
            "rates": {"duplicate_rate": 0, "rapid_duplicate_rate": 0, "bot_rate": 0, "internal_rate": 0},
            "top_bot_agents": [],
            "top_internal_ips": [],
        }

    dedupe_counts = defaultdict(int)
    for row in events:
        key = _safe_str(row.get("dedupe_key"))
        if key:
            dedupe_counts[key] += 1
    duplicate_events = sum(max(count - 1, 0) for count in dedupe_counts.values() if count > 1)

    rapid_duplicate_events = 0
    by_journey = defaultdict(list)
    for row in events:
        by_journey[row.get("journey_key")].append(row)
    for rows in by_journey.values():
        ordered = sorted(rows, key=lambda row: row.get("occurred_at") or now_datetime())
        for idx in range(1, len(ordered)):
            prev = ordered[idx - 1]
            curr = ordered[idx]
            prev_time = prev.get("occurred_at")
            curr_time = curr.get("occurred_at")
            if not prev_time or not curr_time:
                continue
            if prev.get("event_type") == curr.get("event_type") and _normalize_path(prev.get("page_url")) == _normalize_path(curr.get("page_url")):
                delta = (curr_time - prev_time).total_seconds()
                if delta <= 15:
                    rapid_duplicate_events += 1

    ip_rules = _load_ip_exclusion_rules()
    bot_events = 0
    internal_events = 0
    missing_session_events = 0
    bot_agents = defaultdict(int)
    internal_ips = defaultdict(int)

    for row in events:
        if not _safe_str(row.get("session_id")):
            missing_session_events += 1
        ua = _safe_str(row.get("user_agent"))
        if ua and BOT_UA_REGEX.search(ua):
            bot_events += 1
            bot_agents[ua[:120]] += 1
        request_ip = _safe_str(row.get("request_ip"))
        if request_ip and _ip_in_rules(request_ip, ip_rules):
            internal_events += 1
            internal_ips[request_ip] += 1

    issue_rate = min(
        100,
        _safe_rate(duplicate_events + rapid_duplicate_events + bot_events + internal_events, total),
    )
    quality_score = round(max(0, 100 - issue_rate), 2)

    return {
        "total_events": total,
        "duplicate_events": duplicate_events,
        "rapid_duplicate_events": rapid_duplicate_events,
        "bot_events": bot_events,
        "internal_events": internal_events,
        "missing_session_events": missing_session_events,
        "quality_score": quality_score,
        "rates": {
            "duplicate_rate": _safe_rate(duplicate_events, total),
            "rapid_duplicate_rate": _safe_rate(rapid_duplicate_events, total),
            "bot_rate": _safe_rate(bot_events, total),
            "internal_rate": _safe_rate(internal_events, total),
        },
        "top_bot_agents": [
            {"user_agent": key, "count": count}
            for key, count in sorted(bot_agents.items(), key=lambda item: -item[1])[:8]
        ],
        "top_internal_ips": [
            {"ip": key, "count": count}
            for key, count in sorted(internal_ips.items(), key=lambda item: -item[1])[:8]
        ],
    }


def get_advanced_insights_payload(range_key=None, from_date=None, to_date=None, segment_key=None):
    require_management_access()
    from_date, to_date, days = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)
    active_segment, all_segments = _resolve_active_segment(segment_key=segment_key)
    events = _event_rows_for_range(from_date, to_date)
    segment_events = _filter_events_by_segment(events, active_segment)
    goals = _load_goal_definitions(active_only=True)

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": days},
        "segment": active_segment,
        "segments": all_segments,
        "goals": _build_goals_report_from_events(segment_events, goals),
        "cohort": _build_cohort_retention_from_events(segment_events),
        "attribution": _build_attribution_from_events(segment_events),
        "data_quality": _build_data_quality_from_events(segment_events),
    }


def _load_service_account_info(section):
    section = section or {}
    raw_json = _safe_str(section.get("service_account_json"))
    if raw_json:
        try:
            return json.loads(raw_json)
        except Exception:
            return None

    raw_path = _safe_str(section.get("service_account_path"))
    if not raw_path:
        return None
    path = raw_path if os.path.isabs(raw_path) else frappe.get_site_path(raw_path)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def _fetch_ga4_payload(section, from_date, to_date):
    section = section or {}
    if not cint(section.get("enabled")):
        return {
            "connected": False,
            "reason": "disabled",
            "overview": {},
            "channels": [],
            "top_pages": [],
            "audience": {"by_browser": [], "by_os": [], "by_language": []},
            "demographics": {"gender": [], "age_brackets": []},
            "error": "",
        }

    property_id = _safe_str(section.get("property_id"))
    if not property_id:
        return {
            "connected": False,
            "reason": "missing_property_id",
            "overview": {},
            "channels": [],
            "top_pages": [],
            "audience": {"by_browser": [], "by_os": [], "by_language": []},
            "demographics": {"gender": [], "age_brackets": []},
            "error": "property_id تنظیم نشده است.",
        }

    info = _load_service_account_info(section)
    if not info:
        return {
            "connected": False,
            "reason": "missing_credentials",
            "overview": {},
            "channels": [],
            "top_pages": [],
            "audience": {"by_browser": [], "by_os": [], "by_language": []},
            "demographics": {"gender": [], "age_brackets": []},
            "error": "اطلاعات Service Account برای GA4 تنظیم نشده است.",
        }

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        from google.oauth2 import service_account
    except Exception:
        return {
            "connected": False,
            "reason": "missing_sdk",
            "overview": {},
            "channels": [],
            "top_pages": [],
            "audience": {"by_browser": [], "by_os": [], "by_language": []},
            "demographics": {"gender": [], "age_brackets": []},
            "error": "کتابخانه Google Analytics Data در سرور نصب نشده است.",
        }

    try:
        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        client = BetaAnalyticsDataClient(credentials=credentials)
        main_report = client.run_report(
            request=RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=from_date, end_date=to_date)],
                metrics=[
                    Metric(name="totalUsers"),
                    Metric(name="newUsers"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                ],
            )
        )

        overview = {
            "total_users": 0,
            "new_users": 0,
            "sessions": 0,
            "page_views": 0,
            "bounce_rate": 0,
            "avg_session_duration": 0,
        }
        if main_report.rows:
            values = [flt(metric.value or 0) for metric in main_report.rows[0].metric_values]
            overview = {
                "total_users": cint(values[0]),
                "new_users": cint(values[1]),
                "sessions": cint(values[2]),
                "page_views": cint(values[3]),
                "bounce_rate": round(flt(values[4]), 2),
                "avg_session_duration": round(flt(values[5]), 2),
            }

        channel_report = client.run_report(
            request=RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=from_date, end_date=to_date)],
                dimensions=[Dimension(name="sessionDefaultChannelGroup")],
                metrics=[Metric(name="sessions")],
                limit=10,
            )
        )
        channels = []
        for row in channel_report.rows:
            channels.append(
                {
                    "channel": _safe_str((row.dimension_values or [{}])[0].value) or "Unknown",
                    "sessions": cint(flt((row.metric_values or [{}])[0].value or 0)),
                }
            )

        page_report = client.run_report(
            request=RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=from_date, end_date=to_date)],
                dimensions=[Dimension(name="pagePath")],
                metrics=[Metric(name="screenPageViews")],
                limit=12,
            )
        )
        top_pages = []
        for row in page_report.rows:
            top_pages.append(
                {
                    "page": _safe_str((row.dimension_values or [{}])[0].value) or "/",
                    "views": cint(flt((row.metric_values or [{}])[0].value or 0)),
                }
            )

        def _run_dimension_breakdown(dimension_name, metric_name="activeUsers", limit=10):
            try:
                report = client.run_report(
                    request=RunReportRequest(
                        property=f"properties/{property_id}",
                        date_ranges=[DateRange(start_date=from_date, end_date=to_date)],
                        dimensions=[Dimension(name=dimension_name)],
                        metrics=[Metric(name=metric_name)],
                        limit=limit,
                    )
                )
                rows = []
                for report_row in report.rows:
                    rows.append(
                        {
                            "label": _safe_str((report_row.dimension_values or [{}])[0].value) or "Unknown",
                            "value": cint(flt((report_row.metric_values or [{}])[0].value or 0)),
                        }
                    )
                return rows
            except Exception:
                return []

        audience = {
            "by_browser": _run_dimension_breakdown("browser", metric_name="sessions"),
            "by_os": _run_dimension_breakdown("operatingSystem", metric_name="sessions"),
            "by_language": _run_dimension_breakdown("language", metric_name="activeUsers"),
        }
        demographics = {
            "gender": _run_dimension_breakdown("userGender", metric_name="activeUsers"),
            "age_brackets": _run_dimension_breakdown("userAgeBracket", metric_name="activeUsers"),
        }

        return {
            "connected": True,
            "reason": "ok",
            "overview": overview,
            "channels": channels,
            "top_pages": top_pages,
            "audience": audience,
            "demographics": demographics,
            "error": "",
            "last_synced_at": now_datetime().isoformat(),
        }
    except Exception as exc:
        return {
            "connected": False,
            "reason": "request_failed",
            "overview": {},
            "channels": [],
            "top_pages": [],
            "audience": {"by_browser": [], "by_os": [], "by_language": []},
            "demographics": {"gender": [], "age_brackets": []},
            "error": _safe_str(exc),
        }


def _fetch_gsc_payload(section, from_date, to_date):
    section = section or {}
    if not cint(section.get("enabled")):
        return {"connected": False, "reason": "disabled", "overview": {}, "top_queries": [], "top_pages": [], "error": ""}

    site_url = _safe_str(section.get("site_url"))
    if not site_url:
        return {"connected": False, "reason": "missing_site_url", "overview": {}, "top_queries": [], "top_pages": [], "error": "site_url تنظیم نشده است."}

    info = _load_service_account_info(section)
    if not info:
        return {"connected": False, "reason": "missing_credentials", "overview": {}, "top_queries": [], "top_pages": [], "error": "اطلاعات Service Account برای GSC تنظیم نشده است."}

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception:
        return {
            "connected": False,
            "reason": "missing_sdk",
            "overview": {},
            "top_queries": [],
            "top_pages": [],
            "error": "کتابخانه Google API Client در سرور نصب نشده است.",
        }

    try:
        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

        total_response = service.searchanalytics().query(
            siteUrl=site_url,
            body={"startDate": from_date, "endDate": to_date, "rowLimit": 1},
        ).execute()
        total_row = (total_response.get("rows") or [{}])[0]
        overview = {
            "clicks": cint(flt(total_row.get("clicks") or 0)),
            "impressions": cint(flt(total_row.get("impressions") or 0)),
            "ctr": round(flt(total_row.get("ctr") or 0) * 100, 2),
            "position": round(flt(total_row.get("position") or 0), 2),
        }

        queries_response = service.searchanalytics().query(
            siteUrl=site_url,
            body={"startDate": from_date, "endDate": to_date, "dimensions": ["query"], "rowLimit": 10},
        ).execute()
        pages_response = service.searchanalytics().query(
            siteUrl=site_url,
            body={"startDate": from_date, "endDate": to_date, "dimensions": ["page"], "rowLimit": 10},
        ).execute()

        top_queries = [
            {
                "query": _safe_str((row.get("keys") or [""])[0]),
                "clicks": cint(flt(row.get("clicks") or 0)),
                "impressions": cint(flt(row.get("impressions") or 0)),
                "ctr": round(flt(row.get("ctr") or 0) * 100, 2),
                "position": round(flt(row.get("position") or 0), 2),
            }
            for row in (queries_response.get("rows") or [])
        ]
        top_pages = [
            {
                "page": _safe_str((row.get("keys") or [""])[0]),
                "clicks": cint(flt(row.get("clicks") or 0)),
                "impressions": cint(flt(row.get("impressions") or 0)),
                "ctr": round(flt(row.get("ctr") or 0) * 100, 2),
                "position": round(flt(row.get("position") or 0), 2),
            }
            for row in (pages_response.get("rows") or [])
        ]

        return {
            "connected": True,
            "reason": "ok",
            "overview": overview,
            "top_queries": top_queries,
            "top_pages": top_pages,
            "error": "",
            "last_synced_at": now_datetime().isoformat(),
        }
    except Exception as exc:
        return {
            "connected": False,
            "reason": "request_failed",
            "overview": {},
            "top_queries": [],
            "top_pages": [],
            "error": _safe_str(exc),
        }


def _build_local_seo_payload(events, engagement):
    sessions = set()
    organic_sessions = set()
    source_counter = defaultdict(int)
    top_pages_counter = defaultdict(int)
    search_terms = defaultdict(int)

    for row in events:
        if row.get("event_type") not in {"page_view", "product_view", "site_search"}:
            continue
        session_key = _safe_str(row.get("session_id") or row.get("journey_key"))
        if session_key:
            sessions.add(session_key)
        source = _safe_str(row.get("source_channel") or "other").lower() or "other"
        source_counter[source] += 1

        if source in {"google", "bing", "yahoo"} or _safe_str(row.get("utm_medium")).lower() == "organic":
            if session_key:
                organic_sessions.add(session_key)

        path = _normalize_path(row.get("page_url"))
        if path:
            top_pages_counter[path] += 1

        if row.get("event_type") == "site_search":
            props = row.get("properties") or {}
            term = _safe_str(props.get("query") or props.get("search") or props.get("search_term") or props.get("keyword")).lower()
            if term:
                search_terms[term] += 1

    total_sessions = engagement.get("total_sessions") or len(sessions)
    organic_count = len(organic_sessions)
    top_sources = [
        {"source_channel": key, "events": value}
        for key, value in sorted(source_counter.items(), key=lambda item: -item[1])[:8]
    ]
    top_pages = [
        {"path": key, "views": value}
        for key, value in sorted(top_pages_counter.items(), key=lambda item: -item[1])[:10]
    ]
    top_keywords = [
        {"query": key, "count": value}
        for key, value in sorted(search_terms.items(), key=lambda item: -item[1])[:10]
    ]
    return {
        "organic_sessions": organic_count,
        "organic_share": _safe_rate(organic_count, total_sessions),
        "top_sources": top_sources,
        "top_landing_pages": top_pages,
        "top_keywords": top_keywords,
    }


def _social_channel_from_row(row):
    source = _safe_str(row.get("source_channel")).lower()
    utm_source = _safe_str(row.get("utm_source")).lower()
    ref = _safe_str(row.get("referrer_url")).lower()
    probe = f"{source} {utm_source} {ref}"

    if any(token in probe for token in ["instagram", "instagr.am"]):
        return "instagram"
    if any(token in probe for token in ["telegram", "t.me"]):
        return "telegram"
    if any(token in probe for token in ["facebook", "fb.com", "fb.me"]):
        return "facebook"
    if any(token in probe for token in ["pinterest", "pin.it"]):
        return "pinterest"
    if "linkedin" in probe:
        return "linkedin"
    if any(token in probe for token in ["twitter", "x.com"]):
        return "x"
    if any(token in probe for token in ["youtube", "youtu.be"]):
        return "youtube"
    if "tiktok" in probe:
        return "tiktok"
    if any(token in probe for token in ["whatsapp", "wa.me"]):
        return "whatsapp"
    return ""


def _build_social_payload(events):
    channel_totals = {}
    content_counter = defaultdict(lambda: defaultdict(int))

    for row in events:
        channel = _social_channel_from_row(row)
        if not channel:
            continue

        bucket = channel_totals.setdefault(
            channel,
            {
                "channel": channel,
                "page_views": 0,
                "add_to_cart": 0,
                "orders": 0,
                "revenue": 0,
                "_sessions": set(),
            },
        )
        session_key = _safe_str(row.get("session_id") or row.get("journey_key"))
        if session_key:
            bucket["_sessions"].add(session_key)

        event_type = row.get("event_type")
        if event_type in {"page_view", "product_view"}:
            bucket["page_views"] += 1
            content_key = _safe_str(row.get("model_name")) or _normalize_path(row.get("page_url"))
            if content_key:
                content_counter[channel][content_key] += 1
        elif event_type == "add_to_cart":
            bucket["add_to_cart"] += 1
        elif event_type == "order_submit":
            bucket["orders"] += 1
            bucket["revenue"] += flt(row.get("amount") or 0)

    channels = []
    best_content = []
    for channel, row in channel_totals.items():
        sessions = len(row.pop("_sessions", set()))
        row["sessions"] = sessions
        row["revenue"] = round(flt(row.get("revenue") or 0), 2)
        row["conversion_rate"] = _safe_rate(row.get("orders") or 0, row.get("page_views") or 0)
        channels.append(row)

        for content, views in sorted(content_counter.get(channel, {}).items(), key=lambda item: -item[1])[:8]:
            best_content.append(
                {
                    "channel": channel,
                    "content": content,
                    "views": views,
                }
            )

    channels = sorted(channels, key=lambda item: (-(item.get("page_views") or 0), item.get("channel") or ""))
    best_content = sorted(best_content, key=lambda item: (-(item.get("views") or 0), item.get("channel") or ""))[:24]
    return {
        "channels": channels,
        "best_content": best_content,
        "total_social_views": sum(cint(row.get("page_views") or 0) for row in channels),
    }


def _build_audience_payload(events, ga4_payload=None):
    counters = {
        "device": defaultdict(int),
        "city": defaultdict(int),
        "source": defaultdict(int),
        "browser": defaultdict(int),
        "os": defaultdict(int),
        "language": defaultdict(int),
        "gender": defaultdict(int),
        "age": defaultdict(int),
    }
    heatmap = defaultdict(int)

    for row in events:
        if row.get("event_type") not in {"page_view", "product_view"}:
            continue
        props = row.get("properties") or {}
        ua = _safe_str(row.get("user_agent"))

        device = _safe_str(row.get("device_type")).lower() or "other"
        city = _safe_str(row.get("city")).lower() or "unknown"
        source = _safe_str(row.get("source_channel")).lower() or "other"
        browser = _safe_str(row.get("browser_name") or props.get("browser_name") or _browser_from_user_agent(ua)).lower() or "other"
        os_name = _safe_str(row.get("os_name") or props.get("os_name") or _os_from_user_agent(ua)).lower() or "other"
        language = _normalize_language_code(row.get("language") or props.get("language") or props.get("lang")) or "unknown"
        gender = _safe_str(props.get("gender")).lower() or ""
        age = _safe_str(props.get("age_range") or props.get("age")).lower() or ""

        counters["device"][device] += 1
        counters["city"][city] += 1
        counters["source"][source] += 1
        counters["browser"][browser] += 1
        counters["os"][os_name] += 1
        counters["language"][language] += 1
        if gender:
            counters["gender"][gender] += 1
        if age:
            counters["age"][age] += 1

        occurred = row.get("occurred_at")
        if occurred:
            heatmap[(occurred.weekday(), occurred.hour)] += 1

    def _to_rows(counter, key_name, limit=10):
        return [
            {key_name: key, "value": value}
            for key, value in sorted(counter.items(), key=lambda item: -item[1])[:limit]
        ]

    ga4_payload = ga4_payload or {}
    ga4_demographics = ga4_payload.get("demographics") if isinstance(ga4_payload, dict) else {}
    ga4_audience = ga4_payload.get("audience") if isinstance(ga4_payload, dict) else {}

    return {
        "device_breakdown": _to_rows(counters["device"], "device_type"),
        "city_breakdown": _to_rows(counters["city"], "city"),
        "source_breakdown": _to_rows(counters["source"], "source_channel"),
        "browser_breakdown": _to_rows(counters["browser"], "browser"),
        "os_breakdown": _to_rows(counters["os"], "os"),
        "language_breakdown": _to_rows(counters["language"], "language"),
        "time_heatmap": [
            {"weekday": weekday, "hour": hour, "value": value}
            for (weekday, hour), value in sorted(heatmap.items(), key=lambda item: (item[0][0], item[0][1]))
        ],
        "demographics": {
            "gender": ga4_demographics.get("gender") or _to_rows(counters["gender"], "label"),
            "age_brackets": ga4_demographics.get("age_brackets") or _to_rows(counters["age"], "label"),
        },
        "ga4_audience": {
            "by_browser": ga4_audience.get("by_browser") or [],
            "by_os": ga4_audience.get("by_os") or [],
            "by_language": ga4_audience.get("by_language") or [],
        },
    }


def _build_crawl_errors_payload(from_date, to_date):
    if not _doctype_exists("Error Log"):
        return {"total_404": 0, "total_500": 0, "bot_404": 0, "bot_500": 0, "top_paths": []}

    rows = []
    try:
        rows = frappe.db.sql(
            """
            SELECT method, error
            FROM `tabError Log`
            WHERE creation >= %(from_dt)s
              AND creation <= %(to_dt)s
            ORDER BY creation DESC
            LIMIT 3000
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
            as_dict=True,
        )
    except Exception:
        return {"total_404": 0, "total_500": 0, "bot_404": 0, "bot_500": 0, "top_paths": []}

    total_404 = 0
    total_500 = 0
    bot_404 = 0
    bot_500 = 0
    path_counter = defaultdict(int)
    bot_regex = re.compile(r"(googlebot|bingbot|yandex|crawler|spider|bot|facebookexternalhit|slurp)", re.I)
    path_regex = re.compile(r"(/mysite/[A-Za-z0-9\-_\/]+)")

    for row in rows:
        method = _safe_str(row.get("method"))
        error = _safe_str(row.get("error"))
        text = f"{method} {error}"
        text_l = text.lower()
        is_404 = ("404" in text_l) or ("not found" in text_l)
        is_500 = ("500" in text_l) or ("internal server error" in text_l)
        is_bot = bool(bot_regex.search(text))

        if is_404:
            total_404 += 1
            if is_bot:
                bot_404 += 1
        if is_500:
            total_500 += 1
            if is_bot:
                bot_500 += 1

        match = path_regex.search(text)
        if match and (is_404 or is_500):
            path_counter[match.group(1)] += 1

    top_paths = [
        {"path": path, "errors": count}
        for path, count in sorted(path_counter.items(), key=lambda item: -item[1])[:12]
    ]
    return {
        "total_404": total_404,
        "total_500": total_500,
        "bot_404": bot_404,
        "bot_500": bot_500,
        "top_paths": top_paths,
    }


def _build_technical_payload(events, from_date, to_date, engagement):
    page_load_samples = []
    mobile_page_load = []
    desktop_page_load = []
    lcp_samples = []
    cls_samples = []
    fid_samples = []
    inp_samples = []

    for row in events:
        props = row.get("properties") or {}
        page_load = flt(props.get("page_load_ms") or props.get("page_load_time_ms") or 0)
        lcp = flt(props.get("lcp_ms") or 0)
        cls = flt(props.get("cls_score") or props.get("cls") or 0)
        fid = flt(props.get("fid_ms") or 0)
        inp = flt(props.get("inp_ms") or 0)
        device = _safe_str(row.get("device_type")).lower()

        if page_load > 0:
            page_load_samples.append(page_load)
            if device == "mobile":
                mobile_page_load.append(page_load)
            elif device == "desktop":
                desktop_page_load.append(page_load)
        if lcp > 0:
            lcp_samples.append(lcp)
        if cls > 0:
            cls_samples.append(cls)
        if fid > 0:
            fid_samples.append(fid)
        if inp > 0:
            inp_samples.append(inp)

    def _avg(values):
        if not values:
            return 0
        return round(sum(values) / len(values), 2)

    lcp_avg = _avg(lcp_samples)
    cls_avg = _avg(cls_samples)
    fid_avg = _avg(fid_samples)
    inp_avg = _avg(inp_samples)

    cwv_status = "good"
    if (lcp_avg and lcp_avg > 4000) or (cls_avg and cls_avg > 0.25) or (fid_avg and fid_avg > 300):
        cwv_status = "poor"
    elif (lcp_avg and lcp_avg > 2500) or (cls_avg and cls_avg > 0.1) or (fid_avg and fid_avg > 100):
        cwv_status = "needs_improvement"

    errors_404 = 0
    errors_500 = 0
    if _doctype_exists("Error Log"):
        try:
            rows = frappe.db.sql(
                """
                SELECT
                    SUM(CASE WHEN LOWER(IFNULL(error, '')) LIKE '%%404%%'
                                  OR LOWER(IFNULL(error, '')) LIKE '%%not found%%'
                                  OR LOWER(IFNULL(method, '')) LIKE '%%404%%'
                             THEN 1 ELSE 0 END) AS count_404,
                    SUM(CASE WHEN LOWER(IFNULL(error, '')) LIKE '%%500%%'
                                  OR LOWER(IFNULL(error, '')) LIKE '%%internal server error%%'
                             THEN 1 ELSE 0 END) AS count_500
                FROM `tabError Log`
                WHERE creation >= %(from_dt)s
                  AND creation <= %(to_dt)s
                """,
                {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
                as_dict=True,
            )
            row = (rows or [{}])[0]
            errors_404 = cint(row.get("count_404") or 0)
            errors_500 = cint(row.get("count_500") or 0)
        except Exception:
            errors_404 = 0
            errors_500 = 0

    estimated_success_requests = max(cint(engagement.get("page_views") or 0), 0)
    denominator = max(estimated_success_requests + errors_500, 1)
    uptime_percent = round(max(0, (1 - (errors_500 / denominator)) * 100), 2)
    payment = get_payment_gateway_success_payload(from_date=from_date, to_date=to_date)

    return {
        "core_web_vitals": {
            "lcp_ms": lcp_avg,
            "cls_score": cls_avg,
            "fid_ms": fid_avg,
            "inp_ms": inp_avg,
            "status": cwv_status,
            "samples": {
                "lcp": len(lcp_samples),
                "cls": len(cls_samples),
                "fid": len(fid_samples),
                "inp": len(inp_samples),
            },
        },
        "page_speed": {
            "avg_page_load_ms": _avg(page_load_samples),
            "avg_mobile_page_load_ms": _avg(mobile_page_load),
            "avg_desktop_page_load_ms": _avg(desktop_page_load),
            "samples": len(page_load_samples),
        },
        "errors": {
            "http_404": errors_404,
            "http_500": errors_500,
        },
        "uptime": {
            "uptime_percent": uptime_percent,
            "estimated_by": "500_error_ratio",
        },
        "payment": payment,
    }


def get_external_analytics_settings_payload():
    require_management_access()
    return _load_external_settings()


def update_external_analytics_settings_payload(payload):
    require_analytics_manage_access()
    payload = payload or {}
    settings = _save_external_settings(payload)
    audit_log_event(
        module_key="analytics",
        action_key="analytics.update_external_settings",
        target_type="analytics_settings",
        target_key="external",
        result="success",
        details={"keys": sorted((payload or {}).keys())},
    )
    return {"ok": True, "settings": settings}


def get_technical_dashboard_payload(range_key=None, from_date=None, to_date=None):
    require_management_access()
    from_date, to_date, days = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)
    events = _event_rows_for_range(from_date, to_date)
    engagement = _engagement_metrics(from_date, to_date)
    local_seo = _build_local_seo_payload(events, engagement)
    external_settings = _load_external_settings()
    ga4 = _fetch_ga4_payload(external_settings.get("ga4"), from_date, to_date)
    gsc = _fetch_gsc_payload(external_settings.get("gsc"), from_date, to_date)
    crawl_errors = _build_crawl_errors_payload(from_date, to_date)
    technical = _build_technical_payload(events, from_date, to_date, engagement)
    audience = _build_audience_payload(events, ga4_payload=ga4)
    social = _build_social_payload(events)

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": days},
        "engagement": engagement,
        "seo": {
            "local": local_seo,
            "ga4": ga4,
            "gsc": gsc,
            "crawl_errors": crawl_errors,
            "cwv_snapshot": technical.get("core_web_vitals") or {},
        },
        "audience": audience,
        "social": social,
        "technical": technical,
        "integration_settings": external_settings,
    }


def get_tracking_settings_payload():
    require_management_access()

    toggles = []
    goals = []
    alerts = []
    ip_exclusions = []
    segments = _load_saved_segments()

    if _doctype_exists("Analytics Event Toggle"):
        toggles = frappe.get_all(
            "Analytics Event Toggle",
            fields=["name", "event_key", "is_active", "description"],
            order_by="event_key asc",
            limit_page_length=0,
        )
    if not toggles:
        toggles = [
            {"name": key, "event_key": key, "is_active": 1, "description": desc}
            for key, desc in DEFAULT_EVENT_TOGGLES
        ]

    goals = _load_goal_definitions(active_only=False)

    if _doctype_exists("Analytics Alert Rule"):
        alerts = frappe.get_all(
            "Analytics Alert Rule",
            fields=[
                "name",
                "metric_key",
                "operator",
                "threshold_value",
                "window_days",
                "is_active",
                "notify_email",
                "notify_notification_log",
                "recipients",
            ],
            order_by="modified desc",
            limit_page_length=0,
        )

    if _doctype_exists("Analytics IP Exclusion"):
        ip_exclusions = frappe.get_all(
            "Analytics IP Exclusion",
            fields=["name", "ip_or_cidr", "is_active", "note"],
            order_by="ip_or_cidr asc",
            limit_page_length=0,
        )

    return {
        "toggles": toggles,
        "goals": goals,
        "funnels": goals,
        "segments": segments,
        "alerts": alerts,
        "supported_alert_metrics": ALERT_METRIC_DEFINITIONS,
        "ip_exclusions": ip_exclusions,
    }


def _upsert_doc(doctype, unique_field, rows, allowed_fields=None):
    if not _doctype_exists(doctype):
        return
    allowed = set(allowed_fields or [])

    for row in rows or []:
        unique_value = _safe_str(row.get(unique_field))
        if not unique_value:
            continue
        name = row.get("name") or frappe.db.get_value(doctype, {unique_field: unique_value}, "name")
        if name and frappe.db.exists(doctype, name):
            doc = frappe.get_doc(doctype, name)
            for key, value in row.items():
                if key == "name":
                    continue
                if allowed and key not in allowed:
                    continue
                doc.set(key, value)
            doc.save(ignore_permissions=True)
        else:
            payload = {key: value for key, value in dict(row).items() if not allowed or key in allowed}
            payload["doctype"] = doctype
            frappe.get_doc(payload).insert(ignore_permissions=True)


def update_tracking_settings_payload(payload):
    require_analytics_manage_access()
    payload = payload or {}

    _upsert_doc(
        "Analytics Event Toggle",
        "event_key",
        payload.get("toggles") or [],
        allowed_fields=["event_key", "is_active", "description"],
    )
    goal_rows = payload.get("goals")
    if goal_rows is None:
        goal_rows = payload.get("funnels") or []
    normalized_goals = _normalize_goal_rows(goal_rows, ensure_default=False)
    _upsert_doc(
        "Analytics Funnel Definition",
        "title",
        normalized_goals or [],
        allowed_fields=["title", "is_active", "is_default", "steps_json"],
    )
    valid_alert_rows = []
    for row in payload.get("alerts") or []:
        metric_key = _safe_str((row or {}).get("metric_key"))
        if metric_key not in ALERT_METRIC_DEFINITIONS:
            continue
        valid_alert_rows.append(row)

    _upsert_doc(
        "Analytics Alert Rule",
        "metric_key",
        valid_alert_rows,
        allowed_fields=[
            "metric_key",
            "operator",
            "threshold_value",
            "window_days",
            "is_active",
            "notify_email",
            "notify_notification_log",
            "recipients",
        ],
    )
    _upsert_doc(
        "Analytics IP Exclusion",
        "ip_or_cidr",
        payload.get("ip_exclusions") or [],
        allowed_fields=["ip_or_cidr", "is_active", "note"],
    )
    if payload.get("segments") is not None:
        _save_saved_segments(payload.get("segments") or [])
    frappe.db.commit()
    audit_log_event(
        module_key="analytics",
        action_key="analytics.update_tracking_settings",
        target_type="analytics_settings",
        target_key="tracking",
        result="success",
        details={
            "toggles": len(payload.get("toggles") or []),
            "goals": len(payload.get("goals") or payload.get("funnels") or []),
            "alerts": len(payload.get("alerts") or []),
            "ip_exclusions": len(payload.get("ip_exclusions") or []),
        },
    )

    return {"ok": True}


def get_funnel_drop_diagnosis_payload(step="checkout_start", range_key=None, from_date=None, to_date=None):
    require_management_access()
    from_date, to_date, _ = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)

    step = _safe_str(step) or "checkout_start"
    step_index = DEFAULT_FUNNEL_STEPS.index(step) if step in DEFAULT_FUNNEL_STEPS else 2
    previous_step = DEFAULT_FUNNEL_STEPS[max(step_index - 1, 0)]

    reasons = []
    for dimension in ["device_type", "source_channel", "item_group"]:
        rows = frappe.db.sql(
            f"""
            SELECT segment, prev_count, curr_count
            FROM (
                SELECT
                    IFNULL({dimension}, 'unknown') AS segment,
                    SUM(CASE WHEN step_name = %(previous_step)s THEN 1 ELSE 0 END) AS prev_count,
                    SUM(CASE WHEN step_name = %(step)s THEN 1 ELSE 0 END) AS curr_count
                FROM `tabFunnel Step`
                WHERE occurred_at >= %(from_dt)s
                  AND occurred_at <= %(to_dt)s
                GROUP BY IFNULL({dimension}, 'unknown')
            ) AS grouped
            WHERE prev_count > 0
            ORDER BY (prev_count - curr_count) DESC
            LIMIT 5
            """,
            {
                "previous_step": previous_step,
                "step": step,
                "from_dt": f"{from_date} 00:00:00",
                "to_dt": f"{to_date} 23:59:59",
            },
            as_dict=True,
        )
        for row in rows[:2]:
            prev_count = cint(row.get("prev_count") or 0)
            curr_count = cint(row.get("curr_count") or 0)
            if prev_count <= 0:
                continue
            drop = _safe_rate(prev_count - curr_count if prev_count >= curr_count else 0, prev_count)
            if drop < 5:
                continue
            reasons.append(
                {
                    "dimension": dimension,
                    "segment": row.get("segment"),
                    "drop_percent": drop,
                    "message": f"افت در {dimension}={row.get('segment')} حدود {drop}% است.",
                }
            )

    if not reasons:
        reasons.append(
            {
                "dimension": "general",
                "segment": "all",
                "drop_percent": 0,
                "message": "الگوی افت غیرعادی مشخصی دیده نشد؛ احتمالاً ترکیبی از سرعت، قیمت یا UX مرحله checkout است.",
            }
        )

    return {
        "step": step,
        "previous_step": previous_step,
        "range": {"from_date": from_date, "to_date": to_date},
        "reasons": reasons,
    }


def get_payment_gateway_success_payload(range_key=None, from_date=None, to_date=None):
    require_management_access()
    from_date, to_date, _ = _resolve_range(range_key=range_key, from_date=from_date, to_date=to_date)

    rows = []
    if _doctype_exists("Payment Entry"):
        rows = frappe.db.sql(
            """
            SELECT
                IFNULL(mode_of_payment, 'unknown') AS gateway,
                SUM(CASE WHEN docstatus = 1 THEN 1 ELSE 0 END) AS success_count,
                SUM(CASE WHEN docstatus = 2 THEN 1 ELSE 0 END) AS failed_count,
                COUNT(*) AS total_count
            FROM `tabPayment Entry`
            WHERE posting_date >= %(from_date)s
              AND posting_date <= %(to_date)s
            GROUP BY IFNULL(mode_of_payment, 'unknown')
            ORDER BY total_count DESC
            """,
            {"from_date": from_date, "to_date": to_date},
            as_dict=True,
        )

    return {
        "range": {"from_date": from_date, "to_date": to_date},
        "gateways": [
            {
                "gateway": row.get("gateway") or "unknown",
                "success_count": cint(row.get("success_count") or 0),
                "failed_count": cint(row.get("failed_count") or 0),
                "total_count": cint(row.get("total_count") or 0),
                "success_rate": _safe_rate(row.get("success_count") or 0, row.get("total_count") or 0),
            }
            for row in rows
        ],
    }


def build_legacy_funnel_payload(days=30):
    days = min(max(_to_int(days, 30), 1), 365)
    from_date, to_date, _ = _resolve_range(days=days)
    payload = get_conversion_funnel_payload(from_date=from_date, to_date=to_date)

    sessions = payload.get("sessions") or {}
    top_models = payload.get("top_models") or {}

    daily = {}
    if _doctype_exists("Funnel Step"):
        rows = frappe.db.sql(
            """
            SELECT DATE(occurred_at) AS day_key, step_name, COUNT(*) AS count
            FROM `tabFunnel Step`
            WHERE occurred_at >= %(from_dt)s
              AND occurred_at <= %(to_dt)s
            GROUP BY DATE(occurred_at), step_name
            """,
            {"from_dt": f"{from_date} 00:00:00", "to_dt": f"{to_date} 23:59:59"},
            as_dict=True,
        )
        for row in rows:
            day_key = str(row.get("day_key"))
            step_name = row.get("step_name")
            if day_key not in daily:
                daily[day_key] = {step: 0 for step in DEFAULT_FUNNEL_STEPS}
            if step_name in daily[day_key]:
                daily[day_key][step_name] = cint(row.get("count") or 0)

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": days},
        "events": {
            "product_view": sessions.get("product_view", 0),
            "add_to_cart": sessions.get("add_to_cart", 0),
            "order_submit": sessions.get("order_submit", 0),
        },
        "sessions": {
            "product_view": sessions.get("product_view", 0),
            "add_to_cart": sessions.get("add_to_cart", 0),
            "order_submit": sessions.get("order_submit", 0),
            "view_to_cart": min(sessions.get("product_view", 0), sessions.get("add_to_cart", 0)),
            "cart_to_order": min(sessions.get("add_to_cart", 0), sessions.get("order_submit", 0)),
            "view_to_order": min(sessions.get("product_view", 0), sessions.get("order_submit", 0)),
        },
        "conversion_rate": payload.get("conversion_rate") or {},
        "top_models": {
            "product_view": top_models.get("product_view") or [],
            "add_to_cart": top_models.get("add_to_cart") or [],
            "order_submit": top_models.get("order_submit") or [],
        },
        "daily": daily,
    }


def ingest_legacy_funnel_event(step=None, model_name=None, item_code=None, qty=1, amount=0, session_id=None, customer=None, path=None, extra=None):
    payload = {
        "event_type": step,
        "funnel_step": step,
        "session_id": session_id,
        "model_name": model_name,
        "product_id": item_code,
        "qty": qty,
        "amount": amount,
        "customer": customer,
        "page_url": path,
        "properties": extra or {},
        "dedupe_key": f"legacy::{step}::{_safe_str(session_id)}::{_safe_str(item_code)}::{_safe_str(model_name)}::{now_datetime().strftime('%Y%m%d%H%M')}",
    }
    return track_event_payload(payload, from_fallback=True)
