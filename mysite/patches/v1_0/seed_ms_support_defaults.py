import frappe

from mysite.patches.v1_0.ms_support_migration_utils import (
    doctype_exists,
    first_ms_open_status,
    first_ms_priority,
    first_ms_ticket_type,
    map_existing_name,
    migration_logger,
    normalize_status_category,
    to_int,
)


DEFAULT_STATUSES = [
    {"label_agent": "Open", "category": "Open", "order": 10, "color": "Blue", "enabled": 1},
    {"label_agent": "In Progress", "category": "Open", "order": 20, "color": "Cyan", "enabled": 1},
    {"label_agent": "On Hold", "category": "Paused", "order": 30, "color": "Amber", "enabled": 1},
    {"label_agent": "Resolved", "category": "Resolved", "order": 40, "color": "Green", "enabled": 1},
    {"label_agent": "Closed", "category": "Closed", "order": 50, "color": "Gray", "enabled": 1},
]

DEFAULT_PRIORITIES = [
    {"priority": "Urgent", "weight": 10, "enabled": 1},
    {"priority": "High", "weight": 20, "enabled": 1},
    {"priority": "Medium", "weight": 30, "enabled": 1},
    {"priority": "Low", "weight": 40, "enabled": 1},
]

DEFAULT_TYPES = [
    {"ticket_type_name": "General Inquiry", "enabled": 1},
    {"ticket_type_name": "Technical", "enabled": 1},
    {"ticket_type_name": "Billing", "enabled": 1},
]

DEFAULT_FEEDBACK_OPTIONS = [
    {"label": "خیلی بد", "rating": 1, "enabled": 1},
    {"label": "بد", "rating": 2, "enabled": 1},
    {"label": "متوسط", "rating": 3, "enabled": 1},
    {"label": "خوب", "rating": 4, "enabled": 1},
    {"label": "عالی", "rating": 5, "enabled": 1},
]


def _upsert_named_doc(doctype, name, payload, update=True):
    if frappe.db.exists(doctype, name):
        if not update:
            return frappe.get_doc(doctype, name)
        doc = frappe.get_doc(doctype, name)
        for key, value in payload.items():
            doc.set(key, value)
        doc.save(ignore_permissions=True)
        return doc

    doc = frappe.get_doc({"doctype": doctype, **payload})
    doc.insert(ignore_permissions=True)
    return doc


def _seed_statuses(logger):
    rows = []
    if doctype_exists("HD Ticket Status"):
        rows = frappe.db.sql(
            """
            SELECT
                name,
                label_agent,
                category,
                `order` AS sort_order,
                color,
                enabled
            FROM `tabHD Ticket Status`
            ORDER BY `order` ASC, modified ASC
            """,
            as_dict=True,
        )

    if not rows:
        rows = DEFAULT_STATUSES

    for idx, row in enumerate(rows, start=1):
        label = str(row.get("label_agent") or row.get("name") or "").strip()
        if not label:
            continue

        category = normalize_status_category(row.get("category"))
        if label.lower() == "closed":
            category = "Closed"

        payload = {
            "label_agent": label,
            "category": category,
            "order": to_int(row.get("sort_order"), idx * 10),
            "color": str(row.get("color") or "Blue").strip() or "Blue",
            "enabled": 1 if to_int(row.get("enabled"), 1) else 0,
        }
        _upsert_named_doc("MS Support Ticket Status", label, payload, update=True)

    for row in DEFAULT_STATUSES:
        label = row["label_agent"]
        if not frappe.db.exists("MS Support Ticket Status", label):
            _upsert_named_doc("MS Support Ticket Status", label, row, update=False)

    logger.info("seeded ms support statuses")


def _seed_priorities(logger):
    rows = []
    if doctype_exists("HD Ticket Priority"):
        rows = frappe.db.sql(
            """
            SELECT
                name,
                integer_value
            FROM `tabHD Ticket Priority`
            ORDER BY integer_value ASC, modified ASC
            """,
            as_dict=True,
        )

    if rows:
        for idx, row in enumerate(rows, start=1):
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            payload = {
                "priority": name,
                "weight": to_int(row.get("integer_value"), idx * 10),
                "enabled": 1,
            }
            _upsert_named_doc("MS Support Ticket Priority", name, payload, update=True)
    else:
        for payload in DEFAULT_PRIORITIES:
            _upsert_named_doc("MS Support Ticket Priority", payload["priority"], payload, update=False)

    logger.info("seeded ms support priorities")


def _seed_ticket_types(logger):
    rows = []
    if doctype_exists("HD Ticket Type"):
        rows = frappe.db.sql(
            """
            SELECT
                name,
                priority
            FROM `tabHD Ticket Type`
            ORDER BY modified ASC
            """,
            as_dict=True,
        )

    if rows:
        default_priority = first_ms_priority()
        for row in rows:
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            mapped_priority = map_existing_name(
                "MS Support Ticket Priority",
                row.get("priority"),
                fallback=default_priority,
            )
            payload = {
                "ticket_type_name": name,
                "priority": mapped_priority,
                "enabled": 1,
            }
            _upsert_named_doc("MS Support Ticket Type", name, payload, update=True)
    else:
        default_priority = first_ms_priority()
        for payload in DEFAULT_TYPES:
            row = dict(payload)
            row["priority"] = default_priority
            _upsert_named_doc("MS Support Ticket Type", row["ticket_type_name"], row, update=False)

    logger.info("seeded ms support ticket types")


def _seed_teams(logger):
    teams = []
    if doctype_exists("HD Team"):
        teams = frappe.get_all(
            "HD Team",
            fields=["name", "team_name", "assignment_rule"],
            order_by="modified asc",
            ignore_permissions=True,
            limit_page_length=0,
        )

    if not teams:
        teams = [{"name": "Support Team", "team_name": "Support Team", "assignment_rule": ""}]

    for row in teams:
        source_name = str(row.get("name") or "").strip()
        team_name = str(row.get("team_name") or source_name).strip()
        if not team_name:
            continue

        if frappe.db.exists("MS Support Team", team_name):
            doc = frappe.get_doc("MS Support Team", team_name)
        else:
            doc = frappe.new_doc("MS Support Team")
            doc.team_name = team_name

        doc.enabled = 1
        doc.assignment_rule = row.get("assignment_rule") or ""

        existing_users = {str(member.user).strip() for member in (doc.members or []) if member.user}
        if doctype_exists("HD Team Member") and source_name:
            user_rows = frappe.get_all(
                "HD Team Member",
                filters={"parent": source_name, "parenttype": "HD Team"},
                fields=["user"],
                order_by="idx asc",
                ignore_permissions=True,
                limit_page_length=0,
            )
            for user_row in user_rows:
                user = str(user_row.get("user") or "").strip()
                if not user or not frappe.db.exists("User", user) or user in existing_users:
                    continue
                doc.append("members", {"user": user, "is_lead": 0})
                existing_users.add(user)

        doc.save(ignore_permissions=True)

    logger.info("seeded ms support teams")


def _seed_feedback_options(logger):
    rows = []
    if doctype_exists("HD Ticket Feedback Option"):
        rows = frappe.get_all(
            "HD Ticket Feedback Option",
            fields=["label", "rating", "disabled"],
            ignore_permissions=True,
            limit_page_length=0,
        )

    if not rows:
        rows = DEFAULT_FEEDBACK_OPTIONS

    for row in rows:
        label = str(row.get("label") or "").strip()
        if not label:
            continue

        payload = {
            "label": label,
            "rating": to_int(row.get("rating"), 0),
            "enabled": 0 if to_int(row.get("disabled"), 0) else 1,
        }
        if "enabled" in row:
            payload["enabled"] = 1 if to_int(row.get("enabled"), 1) else 0

        _upsert_named_doc("MS Support Ticket Feedback Option", label, payload, update=True)

    logger.info("seeded ms support feedback options")


def _seed_settings(logger):
    hd_default_status = ""
    hd_reopen_status = ""
    hd_default_priority = ""
    hd_default_ticket_type = ""
    hd_reply_email = None

    if doctype_exists("HD Settings"):
        hd_default_status = frappe.db.get_single_value("HD Settings", "default_ticket_status") or ""
        hd_reopen_status = frappe.db.get_single_value("HD Settings", "ticket_reopen_status") or ""
        hd_default_priority = frappe.db.get_single_value("HD Settings", "default_priority") or ""
        hd_default_ticket_type = frappe.db.get_single_value("HD Settings", "default_ticket_type") or ""
        hd_reply_email = frappe.db.get_single_value("HD Settings", "enable_reply_email_via_agent")

    default_status = map_existing_name("MS Support Ticket Status", hd_default_status, fallback=first_ms_open_status())
    reopen_status = map_existing_name("MS Support Ticket Status", hd_reopen_status, fallback=default_status)
    default_priority = map_existing_name("MS Support Ticket Priority", hd_default_priority, fallback=first_ms_priority())
    default_type = map_existing_name("MS Support Ticket Type", hd_default_ticket_type, fallback=first_ms_ticket_type())
    default_sla = frappe.db.get_value("MS Support SLA", {"enabled": 1, "default_sla": 1}, "name")
    default_team = frappe.db.get_value("MS Support Team", {"enabled": 1}, "name", order_by="modified asc")

    if frappe.db.exists("MS Support Settings", "MS Support Settings"):
        settings = frappe.get_doc("MS Support Settings", "MS Support Settings")
    else:
        settings = frappe.new_doc("MS Support Settings")

    settings.default_ticket_status = default_status
    settings.ticket_reopen_status = reopen_status
    settings.default_priority = default_priority
    settings.default_ticket_type = default_type
    settings.default_team = default_team or ""
    settings.auto_assign_tickets = 1
    settings.default_sla = default_sla or ""
    settings.enable_live_chat = 1
    if hd_reply_email is None:
        settings.enable_reply_email_via_agent = 1
    else:
        settings.enable_reply_email_via_agent = 1 if to_int(hd_reply_email, 1) else 0

    settings.save(ignore_permissions=True)
    logger.info("seeded ms support settings")


def execute():
    logger = migration_logger()

    required_doctypes = [
        "MS Support Settings",
        "MS Support Ticket Status",
        "MS Support Ticket Priority",
        "MS Support Ticket Type",
        "MS Support Team",
        "MS Support Team Member",
        "MS Support Ticket Feedback Option",
    ]
    for doctype in required_doctypes:
        if not doctype_exists(doctype):
            logger.warning("skip seed defaults; missing doctype: %s", doctype)
            return

    _seed_statuses(logger)
    _seed_priorities(logger)
    _seed_ticket_types(logger)
    _seed_teams(logger)
    _seed_feedback_options(logger)
    _seed_settings(logger)

    frappe.db.commit()
