import frappe

from mysite.patches.v1_0.ms_support_migration_utils import (
    doctype_exists,
    first_ms_open_status,
    map_customer,
    map_existing_name,
    map_user,
    migration_logger,
    normalize_status_category,
    to_int,
)


BATCH_SIZE = 200


def _resolve_status(value, fallback):
    status = map_existing_name("MS Support Ticket Status", value)
    if status:
        return status

    raw = str(value or "").strip()
    if raw:
        alt = frappe.db.get_value("MS Support Ticket Status", {"label_agent": raw}, "name")
        if alt:
            return alt

    return fallback


def _resolve_priority(value):
    priority = map_existing_name("MS Support Ticket Priority", value)
    if priority:
        return priority
    return frappe.db.get_value("MS Support Ticket Priority", {"enabled": 1}, "name", order_by="weight asc")


def _resolve_ticket_type(value):
    ticket_type = map_existing_name("MS Support Ticket Type", value)
    if ticket_type:
        return ticket_type
    return frappe.db.get_value("MS Support Ticket Type", {"enabled": 1}, "name")


def _resolve_team(value):
    return map_existing_name("MS Support Team", value)


def _resolve_feedback(value):
    feedback = map_existing_name("MS Support Ticket Feedback Option", value)
    if feedback:
        return feedback

    if doctype_exists("HD Ticket Feedback Option") and value and frappe.db.exists("HD Ticket Feedback Option", value):
        label = frappe.db.get_value("HD Ticket Feedback Option", value, "label")
        return map_existing_name("MS Support Ticket Feedback Option", label)
    return ""


def _resolve_contact(value):
    contact = str(value or "").strip()
    if contact and frappe.db.exists("Contact", contact):
        return contact
    return ""


def _resolve_sla(value):
    return map_existing_name("MS Support SLA", value)


def _iter_hd_tickets():
    start = 0
    fields = [
        "name",
        "subject",
        "description",
        "raised_by",
        "contact",
        "customer",
        "status",
        "priority",
        "ticket_type",
        "agent_group",
        "response_by",
        "resolution_by",
        "agreement_status",
        "first_responded_on",
        "first_response_time",
        "avg_response_time",
        "resolution_date",
        "resolution_time",
        "user_resolution_time",
        "service_level_agreement_creation",
        "on_hold_since",
        "total_hold_time",
        "status_category",
        "opening_date",
        "opening_time",
        "via_customer_portal",
        "resolution_details",
        "feedback",
        "sla",
        "creation",
        "modified",
        "owner",
    ]

    while True:
        rows = frappe.get_all(
            "HD Ticket",
            fields=fields,
            order_by="creation asc",
            start=start,
            page_length=BATCH_SIZE,
            ignore_permissions=True,
        )
        if not rows:
            break
        for row in rows:
            yield row
        start += len(rows)


def _set_creation_metadata(doctype, name, row):
    owner = map_user(row.get("owner"), fallback="Administrator")
    frappe.db.sql(
        """
        UPDATE `tab{doctype}`
        SET creation = %(creation)s,
            modified = %(modified)s,
            owner = %(owner)s,
            modified_by = %(owner)s
        WHERE name = %(name)s
        """.format(doctype=doctype),
        {
            "name": name,
            "creation": row.get("creation") or frappe.utils.now(),
            "modified": row.get("modified") or row.get("creation") or frappe.utils.now(),
            "owner": owner,
        },
    )


def execute():
    logger = migration_logger()

    required = ["MS Support Ticket", "MS Support Ticket Status", "MS Support Ticket Priority"]
    for doctype in required:
        if not doctype_exists(doctype):
            logger.warning("skip hd ticket migration; missing doctype: %s", doctype)
            return

    if not doctype_exists("HD Ticket"):
        logger.info("skip hd ticket migration; HD Ticket doctype not found")
        return

    default_status = first_ms_open_status()
    migrated = 0
    skipped = 0
    failed = 0

    for row in _iter_hd_tickets():
        hd_ticket = str(row.get("name") or "").strip()
        if not hd_ticket:
            continue

        if frappe.db.exists("MS Support Ticket", {"legacy_ticket_id": hd_ticket}):
            skipped += 1
            continue

        try:
            status = _resolve_status(row.get("status"), fallback=default_status)
            status_category = (
                frappe.db.get_value("MS Support Ticket Status", status, "category")
                or normalize_status_category(row.get("status_category"))
            )
            priority = _resolve_priority(row.get("priority"))
            ticket_type = _resolve_ticket_type(row.get("ticket_type"))
            team = _resolve_team(row.get("agent_group"))
            customer = map_customer(row.get("customer"))
            feedback = _resolve_feedback(row.get("feedback"))
            contact = _resolve_contact(row.get("contact"))
            raised_by = map_user(row.get("raised_by"), fallback=row.get("owner") or "Administrator")
            sla = _resolve_sla(row.get("sla"))

            subject = str(row.get("subject") or "").strip() or f"Migrated Ticket {hd_ticket}"
            description = (row.get("description") or row.get("subject") or "").strip() or subject

            doc = frappe.get_doc(
                {
                    "doctype": "MS Support Ticket",
                    "subject": subject,
                    "description": description,
                    "raised_by": raised_by,
                    "status": status,
                    "priority": priority,
                    "ticket_type": ticket_type,
                    "team": team,
                    "customer": customer,
                    "contact": contact,
                    "via_customer_portal": to_int(row.get("via_customer_portal"), 0),
                    "source_channel": "helpdesk_migration",
                    "source_page": "/helpdesk",
                    "legacy_ticket_id": hd_ticket,
                }
            )
            doc.insert(ignore_permissions=True)

            update_payload = {
                "raised_by": raised_by,
                "contact": contact,
                "customer": customer,
                "status": status,
                "priority": priority,
                "ticket_type": ticket_type,
                "team": team,
                "response_by": row.get("response_by"),
                "resolution_by": row.get("resolution_by"),
                "agreement_status": row.get("agreement_status") or "",
                "first_responded_on": row.get("first_responded_on"),
                "first_response_time": row.get("first_response_time") or 0,
                "avg_response_time": row.get("avg_response_time") or 0,
                "resolution_date": row.get("resolution_date"),
                "resolution_time": row.get("resolution_time") or 0,
                "user_resolution_time": row.get("user_resolution_time") or 0,
                "service_level_agreement_creation": row.get("service_level_agreement_creation"),
                "on_hold_since": row.get("on_hold_since"),
                "total_hold_time": row.get("total_hold_time") or 0,
                "status_category": status_category,
                "opening_date": row.get("opening_date"),
                "opening_time": row.get("opening_time"),
                "via_customer_portal": to_int(row.get("via_customer_portal"), 0),
                "resolution_details": row.get("resolution_details") or "",
                "feedback": feedback,
                "sla": sla,
                "source_channel": "helpdesk_migration",
                "source_page": "/helpdesk",
                "legacy_ticket_id": hd_ticket,
            }

            frappe.db.set_value(
                "MS Support Ticket",
                doc.name,
                update_payload,
                update_modified=False,
            )
            _set_creation_metadata("MS Support Ticket", doc.name, row)

            migrated += 1
        except Exception:
            failed += 1
            logger.error(
                "failed to migrate hd ticket %s\n%s",
                hd_ticket,
                frappe.get_traceback(),
            )

        if (migrated + skipped + failed) % 200 == 0:
            frappe.db.commit()

    logger.info(
        "hd ticket migration completed: migrated=%s skipped=%s failed=%s",
        migrated,
        skipped,
        failed,
    )
    frappe.db.commit()
