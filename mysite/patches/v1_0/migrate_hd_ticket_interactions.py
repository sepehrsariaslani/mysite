import frappe

from mysite.patches.v1_0.ms_support_migration_utils import (
    doctype_exists,
    map_user,
    migration_logger,
    to_int,
)


BATCH_SIZE = 300


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


def _ticket_map():
    rows = frappe.get_all(
        "MS Support Ticket",
        filters={"legacy_ticket_id": ["!=", ""]},
        fields=["name", "legacy_ticket_id"],
        ignore_permissions=True,
        limit_page_length=0,
    )
    return {str(row.get("legacy_ticket_id") or "").strip(): row.get("name") for row in rows if row.get("legacy_ticket_id")}


def _copy_attachments(old_communication, new_communication):
    file_rows = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Communication",
            "attached_to_name": old_communication,
        },
        fields=["file_name", "file_url", "is_private", "folder"],
        ignore_permissions=True,
        limit_page_length=0,
    )

    for row in file_rows:
        file_url = str(row.get("file_url") or "").strip()
        if not file_url:
            continue

        exists = frappe.db.exists(
            "File",
            {
                "attached_to_doctype": "Communication",
                "attached_to_name": new_communication,
                "file_url": file_url,
            },
        )
        if exists:
            continue

        try:
            frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": row.get("file_name") or file_url.split("/")[-1],
                    "file_url": file_url,
                    "is_private": to_int(row.get("is_private"), 0),
                    "folder": row.get("folder") or "Home/Attachments",
                    "attached_to_doctype": "Communication",
                    "attached_to_name": new_communication,
                }
            ).insert(ignore_permissions=True)
        except Exception:
            migration_logger().error(
                "failed to copy communication attachment old=%s new=%s\n%s",
                old_communication,
                new_communication,
                frappe.get_traceback(),
            )


def _migrate_comments(ticket_by_legacy, logger):
    if not doctype_exists("HD Ticket Comment"):
        return {"migrated": 0, "skipped": 0, "failed": 0}

    migrated = skipped = failed = 0
    start = 0
    fields = [
        "name",
        "reference_ticket",
        "commented_by",
        "content",
        "is_pinned",
        "creation",
        "modified",
        "owner",
    ]

    while True:
        rows = frappe.get_all(
            "HD Ticket Comment",
            fields=fields,
            order_by="creation asc",
            start=start,
            page_length=BATCH_SIZE,
            ignore_permissions=True,
        )
        if not rows:
            break

        for row in rows:
            legacy_comment_id = str(row.get("name") or "").strip()
            if not legacy_comment_id:
                continue

            if frappe.db.exists("MS Support Ticket Comment", {"legacy_comment_id": legacy_comment_id}):
                skipped += 1
                continue

            old_ticket = str(row.get("reference_ticket") or "").strip()
            new_ticket = ticket_by_legacy.get(old_ticket)
            if not new_ticket:
                skipped += 1
                continue

            try:
                doc = frappe.get_doc(
                    {
                        "doctype": "MS Support Ticket Comment",
                        "reference_ticket": new_ticket,
                        "commented_by": map_user(row.get("commented_by"), fallback=row.get("owner") or "Administrator"),
                        "content": row.get("content") or "",
                        "is_pinned": to_int(row.get("is_pinned"), 0),
                        "legacy_comment_id": legacy_comment_id,
                    }
                )
                doc.insert(ignore_permissions=True)
                _set_creation_metadata("MS Support Ticket Comment", doc.name, row)
                migrated += 1
            except Exception:
                failed += 1
                logger.error(
                    "failed to migrate hd comment %s\n%s",
                    legacy_comment_id,
                    frappe.get_traceback(),
                )

        start += len(rows)
        frappe.db.commit()

    return {"migrated": migrated, "skipped": skipped, "failed": failed}


def _migrate_activities(ticket_by_legacy, logger):
    if not doctype_exists("HD Ticket Activity"):
        return {"migrated": 0, "skipped": 0, "failed": 0}

    migrated = skipped = failed = 0
    start = 0
    fields = ["name", "ticket", "action", "creation", "modified", "owner"]

    while True:
        rows = frappe.get_all(
            "HD Ticket Activity",
            fields=fields,
            order_by="creation asc",
            start=start,
            page_length=BATCH_SIZE,
            ignore_permissions=True,
        )
        if not rows:
            break

        for row in rows:
            legacy_activity_id = str(row.get("name") or "").strip()
            if not legacy_activity_id:
                continue

            if frappe.db.exists("MS Support Ticket Activity", {"legacy_activity_id": legacy_activity_id}):
                skipped += 1
                continue

            old_ticket = str(row.get("ticket") or "").strip()
            new_ticket = ticket_by_legacy.get(old_ticket)
            if not new_ticket:
                skipped += 1
                continue

            try:
                doc = frappe.get_doc(
                    {
                        "doctype": "MS Support Ticket Activity",
                        "ticket": new_ticket,
                        "action": row.get("action") or "",
                        "legacy_activity_id": legacy_activity_id,
                    }
                )
                doc.insert(ignore_permissions=True)
                _set_creation_metadata("MS Support Ticket Activity", doc.name, row)
                migrated += 1
            except Exception:
                failed += 1
                logger.error(
                    "failed to migrate hd activity %s\n%s",
                    legacy_activity_id,
                    frappe.get_traceback(),
                )

        start += len(rows)
        frappe.db.commit()

    return {"migrated": migrated, "skipped": skipped, "failed": failed}


def _migrate_communications(ticket_by_legacy, logger):
    if not doctype_exists("Communication"):
        return {"migrated": 0, "skipped": 0, "failed": 0}

    migrated = skipped = failed = 0
    start = 0

    while True:
        rows = frappe.get_all(
            "Communication",
            filters={"reference_doctype": "HD Ticket"},
            fields=[
                "name",
                "reference_name",
                "communication_type",
                "communication_medium",
                "sent_or_received",
                "sender",
                "recipients",
                "cc",
                "bcc",
                "subject",
                "content",
                "status",
                "email_status",
                "creation",
                "modified",
                "owner",
            ],
            order_by="creation asc",
            start=start,
            page_length=BATCH_SIZE,
            ignore_permissions=True,
        )
        if not rows:
            break

        for row in rows:
            old_name = str(row.get("name") or "").strip()
            old_ticket = str(row.get("reference_name") or "").strip()
            new_ticket = ticket_by_legacy.get(old_ticket)
            if not old_name or not new_ticket:
                skipped += 1
                continue

            marker = f"ms-mig-{old_name}"
            if frappe.db.exists("Communication", {"message_id": marker}):
                skipped += 1
                continue

            try:
                doc = frappe.get_doc(
                    {
                        "doctype": "Communication",
                        "communication_type": row.get("communication_type") or "Communication",
                        "communication_medium": row.get("communication_medium") or "",
                        "sent_or_received": row.get("sent_or_received") or "Sent",
                        "reference_doctype": "MS Support Ticket",
                        "reference_name": new_ticket,
                        "subject": row.get("subject") or f"Migrated Communication {old_name}",
                        "content": row.get("content") or "",
                        "sender": row.get("sender") or "",
                        "recipients": row.get("recipients") or "",
                        "cc": row.get("cc") or "",
                        "bcc": row.get("bcc") or "",
                        "status": row.get("status") or "Linked",
                        "email_status": row.get("email_status") or "Open",
                        "message_id": marker,
                    }
                )
                doc.insert(ignore_permissions=True)
                _set_creation_metadata("Communication", doc.name, row)
                _copy_attachments(old_name, doc.name)
                migrated += 1
            except Exception:
                failed += 1
                logger.error(
                    "failed to migrate communication %s\n%s",
                    old_name,
                    frappe.get_traceback(),
                )

        start += len(rows)
        frappe.db.commit()

    return {"migrated": migrated, "skipped": skipped, "failed": failed}


def execute():
    logger = migration_logger()

    required = ["MS Support Ticket", "MS Support Ticket Comment", "MS Support Ticket Activity"]
    for doctype in required:
        if not doctype_exists(doctype):
            logger.warning("skip interaction migration; missing doctype: %s", doctype)
            return

    ticket_by_legacy = _ticket_map()
    if not ticket_by_legacy:
        logger.info("skip interaction migration; no migrated tickets found")
        return

    comments = _migrate_comments(ticket_by_legacy, logger)
    activities = _migrate_activities(ticket_by_legacy, logger)
    communications = _migrate_communications(ticket_by_legacy, logger)

    logger.info(
        "interaction migration completed comments=%s activities=%s communications=%s",
        comments,
        activities,
        communications,
    )
    frappe.db.commit()
