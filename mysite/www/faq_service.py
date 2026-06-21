from __future__ import annotations

from typing import Dict, List

import frappe
from erpnext.controllers.website_list_for_contact import get_parents_for_user


SAMPLE_FAQS = [
    {
        "faq_question": "چطور مناسب‌ترین مدل را انتخاب کنم؟",
        "faq_answer": "برای انتخاب دقیق، ابتدا نوع فضا (نشیمن، ناهارخوری یا اتاق خواب) و ابعاد محل قرارگیری را مشخص کنید. سپس مدل، رنگ بدنه و پارچه را انتخاب کنید تا قیمت نهایی همان ترکیب را ببینید.",
        "faq_category": "محصولات",
        "sort_order": 10,
        "show_on_homepage": 1,
    },
    {
        "faq_question": "آیا قیمت نمایش‌داده‌شده با انتخاب پارچه تغییر می‌کند؟",
        "faq_answer": "بله. قیمت هر محصول با توجه به پارچه انتخاب‌شده و مقدار پارچه مورد نیاز همان محصول محاسبه می‌شود و قیمت نهایی در سایت نمایش داده می‌شود.",
        "faq_category": "پارچه و رنگ",
        "sort_order": 20,
        "show_on_homepage": 1,
    },
    {
        "faq_question": "امکان انتخاب پارچه متفاوت برای هر بخش مبل وجود دارد؟",
        "faq_answer": "بله. برای محصولاتی که پارچه اصلی و پارچه جزیی دارند، هر دو پارچه قابل انتخاب هستند. اگر مدل فقط یک پارچه داشته باشد، تنها پارچه اصلی نمایش داده می‌شود.",
        "faq_category": "پارچه و رنگ",
        "sort_order": 30,
        "show_on_homepage": 1,
    },
    {
        "faq_question": "مدت زمان آماده‌سازی سفارش چقدر است؟",
        "faq_answer": "زمان آماده‌سازی بسته به مدل، پارچه و حجم سفارش متغیر است. زمان تقریبی هر سفارش هنگام ثبت نهایی توسط تیم فروش اعلام می‌شود.",
        "faq_category": "زمان ساخت و ارسال",
        "sort_order": 40,
        "show_on_homepage": 0,
    },
    {
        "faq_question": "آیا امکان ثبت سفارش سفارشی وجود دارد؟",
        "faq_answer": "بله. در بسیاری از مدل‌ها امکان تغییر پارچه، رنگ بدنه و برخی ویژگی‌ها وجود دارد. برای درخواست‌های خاص می‌توانید از مسیر مشاوره یا تماس ثبت سفارش سفارشی انجام دهید.",
        "faq_category": "ثبت سفارش",
        "sort_order": 50,
        "show_on_homepage": 1,
    },
    {
        "faq_question": "شرایط گارانتی محصولات چگونه است؟",
        "faq_answer": "محصولات بر اساس نوع کالا شامل گارانتی کیفیت ساخت هستند. جزئیات کامل گارانتی هنگام خرید و در فاکتور نهایی ثبت می‌شود.",
        "faq_category": "گارانتی",
        "sort_order": 60,
        "show_on_homepage": 0,
    },
    {
        "faq_question": "هزینه ارسال و نصب چطور محاسبه می‌شود؟",
        "faq_answer": "هزینه ارسال و نصب بر اساس شهر مقصد، تعداد آیتم و شرایط حمل تعیین می‌شود و قبل از نهایی‌سازی سفارش به شما اعلام خواهد شد.",
        "faq_category": "نصب و خدمات",
        "sort_order": 70,
        "show_on_homepage": 0,
    },
    {
        "faq_question": "چه روش‌های پرداختی در دسترس است؟",
        "faq_answer": "با توجه به نوع سفارش، امکان پرداخت نقدی یا پرداخت مرحله‌ای وجود دارد. جزئیات روش‌های فعال در زمان ثبت سفارش به شما نمایش داده می‌شود.",
        "faq_category": "پرداخت",
        "sort_order": 80,
        "show_on_homepage": 0,
    },
]


def _safe_int(value, default=0):
    try:
        return int(value or 0)
    except Exception:
        return int(default)


def _normalize_text(value):
    return " ".join(str(value or "").split()).strip()


def _get_default_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _resolve_customer_price_context(requested_customer):
    selected_customer = ""
    selected_price_list = _get_default_price_list() or ""
    price_source = "default"

    requested_customer = (requested_customer or "").strip()
    if not requested_customer or frappe.session.user == "Guest":
        return selected_customer, selected_price_list, price_source

    try:
        allowed_customers = get_parents_for_user("Customer") or []
    except Exception:
        allowed_customers = []

    if requested_customer in allowed_customers:
        selected_customer = requested_customer
        customer_price_list = frappe.db.get_value("Customer", requested_customer, "default_price_list")
        if customer_price_list:
            selected_price_list = customer_price_list
            price_source = "customer"

    return selected_customer, selected_price_list, price_source


def _get_available_fields(doctype):
    if not frappe.db.exists("DocType", doctype):
        return set()
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        return set()
    return {f.fieldname for f in (meta.fields or []) if f.fieldname}


def _build_categories(items: List[Dict]) -> List[Dict]:
    fixed_order = [
        "عمومی",
        "محصولات",
        "پارچه و رنگ",
        "ثبت سفارش",
        "زمان ساخت و ارسال",
        "نصب و خدمات",
        "گارانتی",
        "پرداخت",
    ]
    ordered = []
    for cat in fixed_order:
        if any(_normalize_text(item.get("category")) == cat for item in items):
            ordered.append(cat)
    for item in items:
        cat = _normalize_text(item.get("category"))
        if cat and cat not in ordered:
            ordered.append(cat)
    categories = [{"id": "all", "label": "همه"}]
    categories.extend({"id": frappe.scrub(cat) or "general", "label": cat} for cat in ordered)
    return categories


def get_faq_payload(requested_customer="", only_homepage=False, limit=200):
    selected_customer, selected_price_list, price_source = _resolve_customer_price_context(requested_customer)
    items: List[Dict] = []

    if frappe.db.exists("DocType", "Website FAQ"):
        available_fields = _get_available_fields("Website FAQ")
        filters = {}
        if "is_published" in available_fields:
            filters["is_published"] = 1
        if only_homepage and "show_on_homepage" in available_fields:
            filters["show_on_homepage"] = 1

        requested_fields = [
            "name",
            "faq_question",
            "faq_answer",
            "faq_category",
            "sort_order",
            "show_on_homepage",
            "modified",
        ]
        fields = [f for f in requested_fields if f == "name" or f in available_fields]
        order_by = "sort_order asc, modified desc" if "sort_order" in available_fields else "modified desc"

        try:
            rows = frappe.get_all(
                "Website FAQ",
                filters=filters,
                fields=fields,
                order_by=order_by,
                limit_page_length=max(1, _safe_int(limit, default=200)),
            )
        except Exception:
            rows = []

        for row in rows:
            question = _normalize_text(row.get("faq_question"))
            answer = str(row.get("faq_answer") or "").strip()
            if not question or not answer:
                continue
            category = _normalize_text(row.get("faq_category")) or "عمومی"
            items.append(
                {
                    "id": row.get("name"),
                    "question": question,
                    "answer": answer,
                    "category": category,
                    "category_id": frappe.scrub(category) or "general",
                    "sort_order": _safe_int(row.get("sort_order"), default=0),
                }
            )

    if not items:
        for index, row in enumerate(SAMPLE_FAQS):
            if only_homepage and not row.get("show_on_homepage"):
                continue
            category = _normalize_text(row.get("faq_category")) or "عمومی"
            items.append(
                {
                    "id": f"sample-{index + 1}",
                    "question": _normalize_text(row.get("faq_question")),
                    "answer": str(row.get("faq_answer") or "").strip(),
                    "category": category,
                    "category_id": frappe.scrub(category) or "general",
                    "sort_order": _safe_int(row.get("sort_order"), default=(index + 1) * 10),
                }
            )

    items.sort(key=lambda x: (x.get("sort_order", 0), x.get("question", "")))

    return {
        "FAQItems": items,
        "FAQCategories": _build_categories(items),
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": selected_price_list or "",
        "PriceSource": price_source,
    }


@frappe.whitelist()
def ensure_sample_faq_data():
    if not frappe.db.exists("DocType", "Website FAQ"):
        return {"status": "skipped", "reason": "doctype_not_installed"}

    created = 0
    for row in SAMPLE_FAQS:
        question = _normalize_text(row.get("faq_question"))
        if not question:
            continue
        if frappe.db.exists("Website FAQ", {"faq_question": question}):
            continue
        doc = frappe.get_doc(
            {
                "doctype": "Website FAQ",
                "faq_question": question,
                "faq_answer": row.get("faq_answer"),
                "faq_category": row.get("faq_category") or "عمومی",
                "sort_order": _safe_int(row.get("sort_order"), default=0),
                "is_published": 1,
                "show_on_homepage": 1 if row.get("show_on_homepage") else 0,
            }
        )
        doc.insert(ignore_permissions=True)
        created += 1

    if created:
        frappe.db.commit()
    return {"status": "ok", "created": created}
