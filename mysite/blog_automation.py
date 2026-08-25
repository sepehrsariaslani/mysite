from __future__ import annotations

import json
import os
import ssl
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils.file_manager import save_file


RESULT_LOG_PATH = Path("/Users/sepehr/Downloads/frappe-bench/logs/denroom_blog_automation_last.json")
IMAGE_TIMEOUT_SECONDS = 20
CONTENT_MIN_WORDS = 900
CONTENT_MAX_WORDS = 1100
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-latest"

KEYWORD_STRATEGY = [
    "خرید مبل راحتی",
    "قیمت مبل راحتی",
    "خرید مبل ال",
    "قیمت مبل ال جدید",
    "خرید کاناپه مدرن",
    "خرید صندلی ناهارخوری",
    "قیمت صندلی ناهارخوری",
    "خرید صندلی اپن",
    "قیمت صندلی اپن",
    "خرید میز ناهارخوری",
    "قیمت میز ناهارخوری 4 نفره",
    "قیمت میز ناهارخوری 6 نفره",
    "خرید میز جلومبلی",
    "خرید میز عسلی",
    "خرید نیمکت مدرن",
    "خرید سرویس خواب",
    "قیمت سرویس خواب دو نفره",
    "مبل مینیمال مدرن",
    "مبل مناسب خانه کوچک",
    "مبل مناسب پذیرایی بزرگ",
    "راهنمای خرید مبل راحتی",
    "راهنمای انتخاب پارچه مبل",
    "بهترین پارچه مبل برای خانه بچه‌دار",
    "ابعاد استاندارد مبل راحتی",
    "فاصله استاندارد مبل تا میز جلو مبلی",
    "چیدمان مبل در پذیرایی کوچک",
    "چیدمان مبل ال در خانه ایرانی",
    "ترکیب رنگ مبل و پرده",
    "ترکیب رنگ مبل و فرش",
    "بهترین رنگ مبل برای خانه کم‌نور",
    "مبل طوسی با چه رنگی ست میشه",
    "نگهداری پارچه مبل",
    "تمیز کردن لکه مبل پارچه‌ای",
    "تمیز کردن مبل مخمل",
    "تفاوت مبل راحتی و مبل کلاسیک",
    "تفاوت میز ناهارخوری چوبی و فلزی",
    "بهترین چوب برای مبلمان",
    "صندلی ارگونومیک برای ناهارخوری",
    "ایده دکوراسیون نشیمن مدرن",
    "ایده چیدمان اتاق خواب مدرن",
]

SECONDARY_KEYWORDS_BY_BUCKET = {
    "sofas": [
        "خرید مبل راحتی",
        "قیمت مبل راحتی",
        "خرید مبل ال",
        "مبل مینیمال مدرن",
        "مبل مناسب خانه کوچک",
        "چیدمان مبل در پذیرایی کوچک",
        "ترکیب رنگ مبل و پرده",
        "ترکیب رنگ مبل و فرش",
    ],
    "barstools": [
        "خرید صندلی اپن",
        "قیمت صندلی اپن",
        "خرید صندلی ناهارخوری",
        "قیمت صندلی ناهارخوری",
        "صندلی ارگونومیک برای ناهارخوری",
    ],
    "tables": [
        "خرید میز ناهارخوری",
        "قیمت میز ناهارخوری 4 نفره",
        "قیمت میز ناهارخوری 6 نفره",
        "تفاوت میز ناهارخوری چوبی و فلزی",
    ],
    "coffee-tables": [
        "خرید میز جلومبلی",
        "خرید میز عسلی",
        "فاصله استاندارد مبل تا میز جلو مبلی",
        "ایده دکوراسیون نشیمن مدرن",
    ],
    "benches": [
        "خرید نیمکت مدرن",
        "ایده دکوراسیون نشیمن مدرن",
        "مبل مناسب پذیرایی بزرگ",
    ],
    "beds": [
        "خرید سرویس خواب",
        "قیمت سرویس خواب دو نفره",
        "ایده چیدمان اتاق خواب مدرن",
    ],
}

PRODUCT_SPECIFIC_NOTES = {
    "sofas": """- عمق نشیمن استاندارد: حدود 50 تا 60 سانتی‌متر
- ارتفاع نشیمن: حدود 42 تا 45 سانتی‌متر
- چگالی مناسب فوم: 30 تا 35 کیلوگرم بر مترمکعب
- نکته مهم: استحکام کلاف داخلی (چوب راش یا روس خشک) و نوع فنربندی
- نکته ایرانی: انتخاب پارچه قابل شست‌وشو برای خانه‌های پرتردد""",
    "barstools": """- ارتفاع نشیمن برای اپن 90 سانتی‌متری: حدود 60 تا 65 سانتی‌متر
- ارتفاع نشیمن برای کانتر 105 سانتی‌متری: حدود 70 تا 75 سانتی‌متر
- فاصله مناسب بین صندلی‌های اپن: حداقل 55 تا 60 سانتی‌متر
- نکته مهم: وجود زیرپایی برای ارگونومی بهتر
- نکته ایرانی: روکش مقاوم در برابر لکه و چربی آشپزخانه""",
    "tables": """- ابعاد استاندارد: 4 نفره 80×120، 6 نفره 90×180، 8 نفره 100×220
- فاصله استاندارد بین صندلی‌ها: حداقل 60 سانتی‌متر
- فاصله دور میز تا دیوار: حداقل 90 سانتی‌متر
- نکته مهم: ضخامت صفحه و کیفیت اتصالات پایه
- نکته ایرانی: مقاومت سطح در برابر گرما برای سرو چای""",
    "coffee-tables": """- ارتفاع مناسب میز جلو مبلی: حدود 35 تا 45 سانتی‌متر
- فاصله استاندارد تا مبل: حدود 40 تا 45 سانتی‌متر
- طول میز جلو مبلی: حدود دو سوم طول مبل اصلی
- نکته مهم: گوشه‌های نرم برای ایمنی کودک
- نکته ایرانی: داشتن طبقه یا فضای ذخیره‌سازی برای ریموت و پذیرایی""",
    "benches": """- ارتفاع مناسب نیمکت نشیمن: حدود 42 تا 46 سانتی‌متر
- عمق مناسب نیمکت: حدود 35 تا 45 سانتی‌متر
- عرض پیشنهادی برای ورودی: 90 تا 140 سانتی‌متر
- نکته مهم: تحمل وزن و پایداری پایه‌ها
- نکته ایرانی: مدل‌های باکس‌دار برای نگهداری کفش و وسایل""",
    "beds": """- ابعاد استاندارد: یک‌نفره 90×200، دونفره 160×200، کینگ 180×200
- ارتفاع مناسب کف تخت از زمین: حدود 30 تا 40 سانتی‌متر
- نکات مهم: کیفیت تخته‌های زیر تشک، استحکام هدبورد، صدای اتصالات
- مواد رایج: MDF، چوب راش، فلز
- نکته ایرانی: استفاده از فضای زیر تخت برای ذخیره‌سازی""",
}


def _word_count(text: str) -> int:
    return len([w for w in text.replace("\n", " ").split(" ") if w.strip()])


def _pick_keyword(existing_titles: list[str]) -> dict:
    pool = [
        {
            "key": "sofas",
            "tokens": ["sofa", "sofas", "مبل", "مبلمان", "کاناپه"],
            "label": "مبل راحتی",
            "title": "راهنمای کامل انتخاب مبل راحتی برای دکوراسیون ایرانی",
            "image_urls": [
                "https://source.unsplash.com/1600x900/?sofa,living-room,interior",
                "https://loremflickr.com/1600/900/sofa,livingroom",
                "https://picsum.photos/seed/denroom-sofa/1600/900",
            ],
            "image_credit": "Unsplash",
            "image_source_url": "https://source.unsplash.com/1600x900/?sofa,living-room,interior",
        },
        {
            "key": "barstools",
            "tokens": ["barstool", "barstools", "صندلی اپن", "صندلی بار", "اپن"],
            "label": "صندلی اپن",
            "title": "چگونه صندلی اپن مناسب آشپزخانه مدرن انتخاب کنیم؟",
            "image_urls": [
                "https://source.unsplash.com/1600x900/?barstool,kitchen,interior",
                "https://loremflickr.com/1600/900/barstool,kitchen",
                "https://picsum.photos/seed/denroom-barstool/1600/900",
            ],
            "image_credit": "Unsplash",
            "image_source_url": "https://source.unsplash.com/1600x900/?barstool,kitchen,interior",
        },
        {
            "key": "tables",
            "tokens": ["table", "tables", "میز", "میز ناهارخوری", "ناهارخوری"],
            "label": "میز ناهارخوری",
            "title": "۷ اصل انتخاب میز ناهارخوری متناسب با سبک زندگی خانواده",
            "image_urls": [
                "https://source.unsplash.com/1600x900/?dining-table,home,interior",
                "https://loremflickr.com/1600/900/dining,table",
                "https://picsum.photos/seed/denroom-dining/1600/900",
            ],
            "image_credit": "Unsplash",
            "image_source_url": "https://source.unsplash.com/1600x900/?dining-table,home,interior",
        },
        {
            "key": "coffee-tables",
            "tokens": ["coffee", "coffee-table", "میز جلو مبلی", "جلومبلی", "جلو مبلی"],
            "label": "میز جلو مبلی",
            "title": "راهنمای انتخاب میز جلو مبلی: از ابعاد استاندارد تا ترکیب با مبل",
            "image_urls": [
                "https://source.unsplash.com/1600x900/?coffee-table,living-room,interior",
                "https://loremflickr.com/1600/900/coffee-table,livingroom",
                "https://picsum.photos/seed/denroom-coffee/1600/900",
            ],
            "image_credit": "Unsplash",
            "image_source_url": "https://source.unsplash.com/1600x900/?coffee-table,living-room,interior",
        },
        {
            "key": "benches",
            "tokens": ["bench", "benches", "نیمکت", "پاف نیمکتی"],
            "label": "نیمکت",
            "title": "نیمکت در دکوراسیون داخلی: ۱۰ ایده کاربردی برای ورودی تا اتاق خواب",
            "image_urls": [
                "https://source.unsplash.com/1600x900/?bench,interior,home",
                "https://loremflickr.com/1600/900/bench,interior",
                "https://picsum.photos/seed/denroom-bench/1600/900",
            ],
            "image_credit": "Unsplash",
            "image_source_url": "https://source.unsplash.com/1600x900/?bench,interior,home",
        },
        {
            "key": "beds",
            "tokens": ["bed", "beds", "تخت", "تخت خواب", "اتاق خواب"],
            "label": "تخت خواب",
            "title": "راهنمای خرید تخت خواب استاندارد برای خواب بهتر و دکوراسیون هماهنگ",
            "image_urls": [
                "https://source.unsplash.com/1600x900/?bedroom,bed,interior",
                "https://loremflickr.com/1600/900/bedroom,bed",
                "https://picsum.photos/seed/denroom-bed/1600/900",
            ],
            "image_credit": "Unsplash",
            "image_source_url": "https://source.unsplash.com/1600x900/?bedroom,bed,interior",
        },
    ]

    existing_titles_lc = [t.lower() for t in existing_titles if t]
    for item in pool:
        token_lc = [tok.lower() for tok in item["tokens"]]
        item["score"] = sum(1 for title in existing_titles_lc if any(tok in title for tok in token_lc))

    pool.sort(key=lambda x: (x["score"], x["key"]))
    for item in pool:
        if item["title"].lower() not in existing_titles_lc:
            return item

    fallback = dict(pool[0])
    fallback["title"] = f"{fallback['title']} | {date.today().isoformat()}"
    return fallback


def _secondary_keywords(bucket_key: str) -> list[str]:
    return SECONDARY_KEYWORDS_BY_BUCKET.get(bucket_key, KEYWORD_STRATEGY[:8])


def _product_notes(bucket_key: str) -> str:
    return PRODUCT_SPECIFIC_NOTES.get(
        bucket_key,
        "- ابعاد استاندارد و نکات ارگونومی مرتبط را دقیق پوشش بده\n- متریال رایج و تفاوت قیمت/دوام را توضیح بده",
    )


def _get_anthropic_api_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY") or frappe.conf.get("anthropic_api_key")
    if not api_key:
        raise frappe.ValidationError("missing_anthropic_api_key")
    return str(api_key)


def _build_claude_prompts(
    keyword: str,
    secondary_keywords: list[str],
    product_specific_notes: str,
    existing_titles: list[str],
) -> tuple[str, str]:
    system_prompt = """تو یه نویسنده محتوای متخصص در حوزه مبلمان و دکوراسیون داخلی ایرانی هستی.
وظیفه‌ات نوشتن مقاله‌های راهنمای خرید برای سایت denroom.ir است.

قوانین:
- زبان: فارسی روان و ساده، نه ترجمه‌ای
- طول: بین ۹۰۰ تا ۱۱۰۰ کلمه
- ساختار: Markdown با هدینگ H2 و H3
- لحن: دوستانه و کاربردی، نه تبلیغاتی
- هر مقاله باید اطلاعات اختصاصی همان محصول داشته باشه (ابعاد واقعی، نکات فنی خاص)
- در انتها بخش FAQ با ۴ تا ۵ سوال واقعی که کاربران می‌پرسن"""

    user_prompt = f"""یه مقاله راهنمای خرید برای [{keyword}] بنویس.

محصول: {keyword}
کلمات کلیدی ثانویه: {' | '.join(secondary_keywords)}
ویژگی‌های خاص این محصول که باید پوشش بده:
{product_specific_notes}

برای جلوگیری از تکراری شدن، عنوان‌های اخیر سایت:
{json.dumps(existing_titles[:20], ensure_ascii=False)}

مقاله باید این بخش‌ها رو داشته باشه:
۱. چرا انتخاب درست {keyword} مهمه
۲. ابعاد و اندازه استاندارد (اعداد واقعی بده)
۳. متریال‌های رایج و مقایسه آن‌ها
۴. نکات مخصوص خانه‌های ایرانی
۵. اشتباهات رایج خرید
۶. چک‌لیست خرید
۷. FAQ

خروجی فقط Markdown باشد و عنوان H1 نده."""

    return system_prompt, user_prompt


def _extract_text_blocks(content_blocks: list[dict]) -> str:
    text_parts = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(str(block.get("text") or "").strip())
    return "\n\n".join([part for part in text_parts if part]).strip()


def _generate_content_with_claude(
    keyword: str,
    bucket_key: str,
    existing_titles: list[str],
) -> tuple[str, list[str]]:
    secondary_keywords = _secondary_keywords(bucket_key)
    product_specific_notes = _product_notes(bucket_key)
    system_prompt, user_prompt = _build_claude_prompts(
        keyword=keyword,
        secondary_keywords=secondary_keywords,
        product_specific_notes=product_specific_notes,
        existing_titles=existing_titles,
    )

    payload = {
        "model": os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL),
        "max_tokens": 3200,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    req = Request(
        ANTHROPIC_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": _get_anthropic_api_key(),
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=45) as response:
        body = response.read().decode("utf-8")

    parsed = json.loads(body)
    content_md = _extract_text_blocks(parsed.get("content") or [])
    if not content_md:
        raise frappe.ValidationError("empty_claude_response")
    return content_md, secondary_keywords


def _validate_generated_content(content_md: str):
    word_count = _word_count(content_md)
    if word_count < CONTENT_MIN_WORDS or word_count > CONTENT_MAX_WORDS:
        raise frappe.ValidationError(f"word_count_out_of_range:{word_count}")
    if "## " not in content_md:
        raise frappe.ValidationError("missing_h2")
    if "### " not in content_md:
        raise frappe.ValidationError("missing_h3")
    if "## FAQ" not in content_md:
        raise frappe.ValidationError("missing_faq_section")
    faq_questions = [line for line in content_md.splitlines() if line.strip().startswith("### ")]
    if len(faq_questions) < 4:
        raise frappe.ValidationError("insufficient_faq_questions")


def _ensure_blog_custom_fields():
    custom_fields = {
        "Blog Post": [
            {
                "fieldname": "custom_focus_keyword",
                "label": "Focus Keyword",
                "fieldtype": "Data",
                "insert_after": "meta_description",
            },
            {
                "fieldname": "custom_secondary_keywords",
                "label": "Secondary Keywords",
                "fieldtype": "Small Text",
                "insert_after": "custom_focus_keyword",
            },
            {
                "fieldname": "custom_image_source_url",
                "label": "Image Source URL",
                "fieldtype": "Data",
                "insert_after": "custom_secondary_keywords",
            },
            {
                "fieldname": "custom_image_credit",
                "label": "Image Credit",
                "fieldtype": "Data",
                "insert_after": "custom_image_source_url",
            },
        ]
    }
    create_custom_fields(custom_fields, ignore_validate=True)


def _download_image(image_urls: list[str]) -> tuple[bytes, str]:
    contexts = [None]
    try:
        import certifi  # type: ignore

        contexts.append(ssl.create_default_context(cafile=certifi.where()))
    except Exception:
        pass
    # Environment fallback: some local benches miss CA roots.
    contexts.append(ssl._create_unverified_context())

    last_error = None
    for image_url in image_urls:
        req = Request(image_url, headers={"User-Agent": "denroom-blog-automation/1.0"})
        for ctx in contexts:
            try:
                if ctx is None:
                    with urlopen(req, timeout=IMAGE_TIMEOUT_SECONDS) as response:
                        data = response.read()
                else:
                    with urlopen(req, timeout=IMAGE_TIMEOUT_SECONDS, context=ctx) as response:
                        data = response.read()
                if data:
                    return data, image_url
            except Exception as exc:
                last_error = exc

    raise frappe.ValidationError(f"image_download_failed:{last_error}")


def _attach_image_to_post(doc, picked: dict) -> tuple[str, str]:
    image_bytes, source_url = _download_image(picked["image_urls"])
    filename = f"{doc.name}-{picked['key']}.jpg"
    file_doc = save_file(
        fname=filename,
        content=image_bytes,
        dt="Blog Post",
        dn=doc.name,
        folder="Home/Attachments",
        is_private=0,
    )
    return file_doc.file_url, source_url


def _image_credit_from_source(source_url: str, default_credit: str) -> str:
    host = (urlparse(source_url).netloc or "").lower()
    if "unsplash.com" in host:
        return "Unsplash"
    if "loremflickr.com" in host:
        return "LoremFlickr"
    if "picsum.photos" in host:
        return "Picsum"
    return default_credit


def run_denroom_daily_post():
    category_title = "مجله دن‌روم"
    category_name = frappe.scrub(category_title)
    blogger_short_name = "denroom-editorial"
    blogger_full_name = "تحریریه دن‌روم"

    result = {"status": "error", "error": "unknown"}
    try:
        _ensure_blog_custom_fields()

        existing_titles = [
            (row.get("title") or "").strip()
            for row in frappe.get_all("Blog Post", fields=["title"], limit_page_length=0)
        ]
        picked = _pick_keyword(existing_titles)
        title = picked["title"]
        keyword = picked["label"]

        existing_category = frappe.db.get_value("Blog Category", {"title": category_title}, "name")
        if not existing_category:
            category_doc = frappe.get_doc(
                {
                    "doctype": "Blog Category",
                    "title": category_title,
                    "description": "مقاله‌های آموزشی و کاربردی درباره انتخاب مبلمان و طراحی داخلی.",
                    "published": 1,
                }
            )
            category_doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
            existing_category = category_doc.name
        category_name = existing_category or category_name

        if not frappe.db.exists("Blogger", {"short_name": blogger_short_name}):
            blogger_doc = frappe.get_doc(
                {
                    "doctype": "Blogger",
                    "short_name": blogger_short_name,
                    "full_name": blogger_full_name,
                    "bio": "تیم تحریریه دن‌روم؛ ارائه راهنمای عملی برای خرید مبلمان و چیدمان حرفه‌ای.",
                }
            )
            blogger_doc.insert(ignore_permissions=True, ignore_if_duplicate=True)

        if frappe.db.exists("Blog Post", title):
            raise frappe.ValidationError("duplicate_title_detected_after_selection")

        content_md, secondary_keywords = _generate_content_with_claude(
            keyword=keyword,
            bucket_key=picked["key"],
            existing_titles=existing_titles,
        )
        _validate_generated_content(content_md)
        word_count = _word_count(content_md)

        doc = frappe.get_doc(
            {
                "doctype": "Blog Post",
                "title": title,
                "blog_category": category_name,
                "blogger": blogger_short_name,
                "content_type": "Markdown",
                "content_md": content_md,
                "blog_intro": f"در این راهنمای جامع یاد می‌گیرید چطور {keyword} مناسب فضای خانه‌تان انتخاب کنید؛ از اندازه و متریال تا رنگ، ایمنی و بودجه‌بندی.",
                "meta_description": f"راهنمای سئو شده انتخاب {keyword}: ابعاد استاندارد، جنس مناسب، هماهنگی با مبلمان، نکات خرید هوشمند و پاسخ به سوالات پرتکرار.",
                "custom_focus_keyword": keyword,
                "custom_secondary_keywords": " | ".join(secondary_keywords),
                "custom_image_source_url": picked["image_source_url"],
                "custom_image_credit": picked["image_credit"],
                "published": 1,
                "published_on": date.today().isoformat(),
            }
        )
        doc.insert(ignore_permissions=True)

        image_url, resolved_source_url = _attach_image_to_post(doc, picked)
        if not str(doc.content_md).startswith("!["):
            doc.content_md = f"![{title}]({image_url})\n\n{doc.content_md}"
        doc.meta_image = image_url
        doc.custom_image_source_url = resolved_source_url
        doc.custom_image_credit = _image_credit_from_source(
            resolved_source_url, picked["image_credit"]
        )
        doc.save(ignore_permissions=True)

        frappe.db.commit()

        saved = frappe.get_doc("Blog Post", doc.name)
        result = {
            "status": "ok",
            "name": saved.name,
            "title": saved.title,
            "route": saved.route,
            "published": int(saved.published),
            "published_on": str(saved.published_on),
            "blog_category": saved.blog_category,
            "blogger": saved.blogger,
            "keyword": picked["key"],
            "word_count": word_count,
            "meta_image": saved.meta_image,
        }
        RESULT_LOG_PATH.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        return result
    except Exception as exc:
        frappe.db.rollback()
        result = {"status": "error", "error": str(exc)}
        RESULT_LOG_PATH.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        raise
