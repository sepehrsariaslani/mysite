import frappe


def _doctype_exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def _default_team():
    if not _doctype_exists("MS Support Team"):
        return ""
    return frappe.db.get_value("MS Support Team", {"enabled": 1}, "name", order_by="modified asc") or ""


def _seed_shift(default_team):
    if not _doctype_exists("MS Support Shift"):
        return

    if frappe.db.count("MS Support Shift"):
        return

    doc = frappe.get_doc(
        {
            "doctype": "MS Support Shift",
            "shift_name": "شیفت پیش‌فرض پشتیبانی",
            "enabled": 1,
            "is_default": 1,
            "team": default_team,
            "weekdays": "sat,sun,mon,tue,wed,thu",
            "start_time": "09:00:00",
            "end_time": "18:00:00",
        }
    )

    if default_team and _doctype_exists("MS Support Team Member"):
        members = frappe.get_all(
            "MS Support Team Member",
            filters={"parent": default_team, "parenttype": "MS Support Team"},
            fields=["user"],
            order_by="idx asc",
            ignore_permissions=True,
            limit_page_length=0,
        )
        for row in members:
            user = str(row.get("user") or "").strip()
            if user:
                doc.append("members", {"user": user, "enabled": 1})

    doc.insert(ignore_permissions=True)


def _seed_macros():
    if not _doctype_exists("MS Support Macro"):
        return

    if not (
        frappe.db.exists("MS Support Macro", "Quick Acknowledge")
        or frappe.db.exists("MS Support Macro", "تایید سریع")
    ):
        frappe.get_doc(
            {
                "doctype": "MS Support Macro",
                "macro_name": "تایید سریع",
                "enabled": 1,
                "category": "عمومی",
                "content": "درخواست شما ثبت شد و همکاران ما در اسرع وقت پاسخ خواهند داد.",
                "send_email": 1,
            }
        ).insert(ignore_permissions=True)

    if not (
        frappe.db.exists("MS Support Macro", "Need More Info")
        or frappe.db.exists("MS Support Macro", "نیاز به اطلاعات بیشتر")
    ):
        frappe.get_doc(
            {
                "doctype": "MS Support Macro",
                "macro_name": "نیاز به اطلاعات بیشتر",
                "enabled": 1,
                "category": "عمومی",
                "content": "برای بررسی دقیق‌تر، لطفاً جزئیات بیشتری ارسال کنید (شماره سفارش، زمان رخداد، تصویر/ویدیو).",
                "send_email": 1,
            }
        ).insert(ignore_permissions=True)


def _seed_automation(default_team):
    if not _doctype_exists("MS Support Automation Rule"):
        return

    if (
        frappe.db.exists("MS Support Automation Rule", "Ticket Created Auto Route")
        or frappe.db.exists("MS Support Automation Rule", "مسیر خودکار تیکت جدید")
    ):
        return

    doc = frappe.get_doc(
        {
            "doctype": "MS Support Automation Rule",
            "rule_name": "مسیر خودکار تیکت جدید",
            "enabled": 1,
            "priority": 10,
            "trigger_event": "Ticket Created",
            "description": "برای تیکت جدید، تیم تعیین کن و فعالیت ثبت کن.",
            "stop_after_first_match": 1,
            "actions": [
                {
                    "action_type": "Set Team",
                    "value": default_team,
                    "extra_json": "",
                },
                {
                    "action_type": "Add Activity",
                    "value": "automation_ticket_created",
                    "extra_json": "",
                },
            ],
        }
    )
    doc.insert(ignore_permissions=True)


def execute():
    default_team = _default_team()

    _seed_shift(default_team)
    _seed_macros()
    _seed_automation(default_team)

    frappe.db.commit()
