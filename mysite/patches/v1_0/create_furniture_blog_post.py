import frappe


def execute():
    category_title = "مجله_دن‌روم"
    blogger_short_name = "denroom-editorial"
    blogger_full_name = "تحریریه دن‌روم"
    post_title = "راهنمای انتخاب مبلمان و صندلی برای خانه‌های امروزی"

    category_name = None
    candidate_names = [
        "مجله-دن‌روم",
        "مجله_دن‌روم",
        frappe.scrub(category_title),
        frappe.scrub(category_title.replace("_", " ")),
    ]
    for candidate in candidate_names:
        if frappe.db.exists("Blog Category", candidate):
            category_name = candidate
            break

    if not category_name:
        category_name = frappe.db.get_value("Blog Category", {"title": category_title}, "name")

    if not category_name:
        category_doc = frappe.get_doc(
            {
                "doctype": "Blog Category",
                "title": category_title,
                "description": "ایده‌ها و نکته‌های طراحی برای انتخاب هوشمندانه مبلمان.",
                "published": 1,
            }
        ).insert(ignore_permissions=True, ignore_if_duplicate=True)
        category_name = category_doc.name

    if not frappe.db.exists("Blogger", blogger_short_name):
        frappe.get_doc(
            {
                "doctype": "Blogger",
                "short_name": blogger_short_name,
                "full_name": blogger_full_name,
                "bio": "راهنمای عملی برای انتخاب مبلمان و چیدمان کاربردی.",
            }
        ).insert(ignore_permissions=True, ignore_if_duplicate=True)

    if frappe.db.exists("Blog Post", post_title):
        return

    content_md = "\n".join(
        [
            "انتخاب مبلمان و صندلی فقط به ظاهر ختم نمی‌شود؛ باید راحتی، دوام و هماهنگی با فضا را همزمان ببینید.",
            "",
            "## 1. اندازه و تناسب با فضا",
            "- قبل از خرید، نقشه ساده اتاق را بکشید و مسیر رفت‌وآمد را علامت بزنید.",
            "- حداقل 80 سانتی‌متر فضای عبور بین مبل‌ها و میز را در نظر بگیرید.",
            "",
            "## 2. ارگونومی صندلی",
            "- ارتفاع نشیمن بین 40 تا 45 سانتی‌متر برای اکثر افراد مناسب است.",
            "- زاویه پشتی باید کمر را حمایت کند تا نشستن طولانی خسته‌کننده نشود.",
            "",
            "## 3. جنس و دوام",
            "- برای خانه‌های پر رفت‌وآمد، پارچه‌های مقاوم در برابر لکه انتخاب کنید.",
            "- پایه‌های فلزی یا چوب سخت (مثل راش) معمولاً دوام بیشتری دارند.",
            "",
            "## 4. هماهنگی رنگ و بافت",
            "- یک رنگ خنثی برای مبل اصلی و رنگ‌های جسورانه برای کوسن‌ها انتخاب کنید.",
            "- ترکیب بافت‌ها (چوب، فلز، پارچه) به فضا عمق می‌دهد.",
            "",
            "## 5. جمع‌بندی سریع",
            "اگر بین چند مدل مردد هستید، اول فضا و کاربری را مشخص کنید، بعد به سراغ مدل و رنگ بروید.",
        ]
    )

    doc = frappe.get_doc(
        {
            "doctype": "Blog Post",
            "title": post_title,
            "blog_category": category_name or frappe.scrub(category_title),
            "blogger": blogger_short_name,
            "content_type": "Markdown",
            "content_md": content_md,
            "blog_intro": "چطور مبلمان و صندلی مناسب خانه را انتخاب کنیم؟ نکته‌های کاربردی برای اندازه، ارگونومی و دوام.",
            "meta_description": "راهنمای انتخاب مبلمان و صندلی: اندازه مناسب، ارگونومی درست، جنس بادوام و هماهنگی رنگ‌ها.",
            "published": 1,
            "published_on": "2026-02-22",
        }
    )
    doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
    frappe.db.commit()
