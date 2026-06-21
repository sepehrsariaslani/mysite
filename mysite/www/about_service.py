from __future__ import annotations

from typing import Dict, List, Optional

import frappe


DEFAULT_ABOUT_PAYLOAD = {
    "hero": {
        "badge": "ABOUT DENROOM",
        "title": "ما دن‌روم هستیم",
        "subtitle": "طراحی، ساخت و اجرای مبلمان سفارشی برای فضاهای مسکونی و تجاری",
        "intro": "تمرکز ما روی ترکیب طراحی معاصر، کیفیت ساخت دقیق و تجربه خرید شفاف است.",
        "founded_year": 1396,
    },
    "mission": {
        "title": "ماموریت ما",
        "body": "<p>ماموریت دن‌روم ساخت محصولاتی است که هم از نظر زیبایی و هم از نظر کاربری، زندگی روزمره را بهتر کنند.</p><p>ما تلاش می‌کنیم انتخاب مبلمان را از یک مسیر پیچیده، به تجربه‌ای دقیق، شفاف و لذت‌بخش تبدیل کنیم.</p>",
    },
    "vision": {
        "title": "چشم‌انداز ما",
        "body": "<p>چشم‌انداز ما تبدیل‌شدن به مرجع مبلمان سفارشی در ایران است؛ برندی که مشتری با اطمینان از کیفیت، خدمات و پشتیبانی، آن را انتخاب می‌کند.</p><p>دن‌روم به‌دنبال توسعه شبکه طراحی و تولید خود با استانداردهای بین‌المللی است.</p>",
    },
    "history": {
        "title": "تاریخچه دن‌روم",
        "intro": "دن‌روم از یک کارگاه تخصصی کوچک شروع شد و امروز به یک تیم طراحی، تولید و اجرای کامل تبدیل شده است.",
        "body": "<p>طی این مسیر، تمرکز اصلی ما روی بهبود مداوم کیفیت متریال، فرآیند ساخت و خدمات پس از فروش بوده است. رشد دن‌روم نتیجه همکاری نزدیک تیم تولید، تیم طراحی و بازخورد مستقیم مشتریان واقعی است.</p>",
    },
    "values": [
        {
            "icon": "✦",
            "title": "کیفیت واقعی",
            "description": "انتخاب متریال استاندارد و کنترل دقیق کیفیت در هر مرحله ساخت.",
        },
        {
            "icon": "✦",
            "title": "شفافیت",
            "description": "ارائه اطلاعات روشن درباره محصول، قیمت و زمان تحویل.",
        },
        {
            "icon": "✦",
            "title": "مشتری‌محوری",
            "description": "طراحی راه‌حل براساس نیاز واقعی هر فضا و هر مشتری.",
        },
        {
            "icon": "✦",
            "title": "نوآوری کاربردی",
            "description": "ترکیب طراحی روز با راحتی، دوام و امکان شخصی‌سازی.",
        },
    ],
    "timeline": [
        {
            "year": "۱۳۹۶",
            "title": "شروع مسیر",
            "description": "آغاز فعالیت با تمرکز بر طراحی و تولید سفارشی مبلمان خانگی.",
            "highlight": 0,
        },
        {
            "year": "۱۳۹۸",
            "title": "توسعه محصولات",
            "description": "گسترش سبد محصولات به صندلی، میز و اکسسوری‌های مکمل.",
            "highlight": 0,
        },
        {
            "year": "۱۴۰۱",
            "title": "ورود به پروژه‌های بزرگ",
            "description": "همکاری با پروژه‌های مسکونی و تجاری و اجرای چیدمان کامل.",
            "highlight": 1,
        },
        {
            "year": "امروز",
            "title": "توسعه مستمر",
            "description": "تمرکز روی تجربه دیجیتال بهتر و خدمات مشاوره تخصصی‌تر.",
            "highlight": 0,
        },
    ],
}


def _normalize_text(value: object) -> str:
    return " ".join(str(value or "").split()).strip()


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value or 0)
    except Exception:
        return int(default)


def _get_available_fields(doctype: str) -> set:
    if not frappe.db.exists("DocType", doctype):
        return set()
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        return set()
    return {field.fieldname for field in (meta.fields or []) if field.fieldname}


def _get_about_doc():
    if not frappe.db.exists("DocType", "Website About"):
        return None

    meta = frappe.get_meta("Website About")
    if meta.issingle:
        return frappe.get_single("Website About")

    available_fields = _get_available_fields("Website About")
    filters = {}
    if "is_published" in available_fields:
        filters["is_published"] = 1

    order_by_parts = []
    if "is_published" in available_fields:
        order_by_parts.append("is_published desc")
    if "sort_order" in available_fields:
        order_by_parts.append("sort_order asc")
    order_by_parts.append("modified desc")

    rows = frappe.get_all(
        "Website About",
        filters=filters,
        fields=["name"],
        order_by=", ".join(order_by_parts),
        limit_page_length=1,
    )

    if not rows and filters:
        rows = frappe.get_all(
            "Website About",
            fields=["name"],
            order_by=", ".join(order_by_parts),
            limit_page_length=1,
        )

    if not rows:
        return None

    return frappe.get_doc("Website About", rows[0].get("name"))


def _build_payload_from_doc() -> Optional[Dict]:
    doc = _get_about_doc()
    if not doc:
        return None

    values: List[Dict] = []
    for index, item in enumerate(doc.get("core_values") or []):
        if _safe_int(item.get("is_active"), default=1) == 0:
            continue
        title = _normalize_text(item.get("value_title"))
        description = str(item.get("value_description") or "").strip()
        if not title or not description:
            continue
        values.append(
            {
                "icon": _normalize_text(item.get("icon")) or "✦",
                "title": title,
                "description": description,
                "sort_order": _safe_int(item.get("sort_order"), default=(index + 1) * 10),
            }
        )

    values.sort(key=lambda item: (item.get("sort_order", 0), item.get("title", "")))

    timeline: List[Dict] = []
    for index, item in enumerate(doc.get("history_timeline") or []):
        if _safe_int(item.get("is_active"), default=1) == 0:
            continue
        year_label = _normalize_text(item.get("year_label"))
        title = _normalize_text(item.get("milestone_title"))
        description = str(item.get("milestone_description") or "").strip()
        if not year_label or not title or not description:
            continue
        timeline.append(
            {
                "year": year_label,
                "title": title,
                "description": description,
                "highlight": 1 if _safe_int(item.get("is_highlight"), default=0) else 0,
                "sort_order": _safe_int(item.get("sort_order"), default=(index + 1) * 10),
            }
        )

    timeline.sort(key=lambda item: (item.get("sort_order", 0), item.get("year", "")))

    return {
        "hero": {
            "badge": "ABOUT DENROOM",
            "title": _normalize_text(doc.get("title")) or DEFAULT_ABOUT_PAYLOAD["hero"]["title"],
            "subtitle": str(doc.get("subtitle") or "").strip() or DEFAULT_ABOUT_PAYLOAD["hero"]["subtitle"],
            "intro": str(doc.get("hero_intro") or "").strip() or DEFAULT_ABOUT_PAYLOAD["hero"]["intro"],
            "founded_year": _safe_int(
                doc.get("founded_year"), default=DEFAULT_ABOUT_PAYLOAD["hero"]["founded_year"]
            ),
        },
        "mission": {
            "title": _normalize_text(doc.get("mission_title")) or DEFAULT_ABOUT_PAYLOAD["mission"]["title"],
            "body": str(doc.get("mission_body") or "").strip() or DEFAULT_ABOUT_PAYLOAD["mission"]["body"],
        },
        "vision": {
            "title": _normalize_text(doc.get("vision_title")) or DEFAULT_ABOUT_PAYLOAD["vision"]["title"],
            "body": str(doc.get("vision_body") or "").strip() or DEFAULT_ABOUT_PAYLOAD["vision"]["body"],
        },
        "history": {
            "title": _normalize_text(doc.get("history_title")) or DEFAULT_ABOUT_PAYLOAD["history"]["title"],
            "intro": str(doc.get("history_intro") or "").strip() or DEFAULT_ABOUT_PAYLOAD["history"]["intro"],
            "body": str(doc.get("history_body") or "").strip() or DEFAULT_ABOUT_PAYLOAD["history"]["body"],
        },
        "values": values or DEFAULT_ABOUT_PAYLOAD["values"],
        "timeline": timeline or DEFAULT_ABOUT_PAYLOAD["timeline"],
    }


def get_about_payload() -> Dict:
    try:
        payload = _build_payload_from_doc()
        if payload:
            return payload
    except Exception:
        frappe.log_error(frappe.get_traceback(), "about_page_payload_failed")
    return DEFAULT_ABOUT_PAYLOAD
