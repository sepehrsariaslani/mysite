import frappe

from mysite.patches.v1_0.ms_support_migration_utils import doctype_exists, migration_logger


INDEX_SPECS = [
    ("tabMS Support Ticket", "idx_ms_support_ticket_legacy", "(`legacy_ticket_id`)", False),
    ("tabMS Support Ticket", "idx_ms_support_ticket_customer", "(`customer`)", False),
    ("tabMS Support Ticket", "idx_ms_support_ticket_status", "(`status`)", False),
    ("tabMS Support Ticket", "idx_ms_support_ticket_priority", "(`priority`)", False),
    ("tabMS Support Ticket", "idx_ms_support_ticket_agreement", "(`agreement_status`)", False),
    ("tabMS Support Ticket", "idx_ms_support_ticket_creation", "(`creation`)", False),
    ("tabMS Support Ticket", "idx_ms_support_ticket_response_by", "(`response_by`)", False),
    ("tabMS Support Ticket", "idx_ms_support_ticket_resolution_by", "(`resolution_by`)", False),
    ("tabMS Support Ticket Comment", "idx_ms_support_comment_legacy", "(`legacy_comment_id`)", False),
    ("tabMS Support Ticket Activity", "idx_ms_support_activity_legacy", "(`legacy_activity_id`)", False),
]


def _table_exists(table_name):
    return bool(frappe.db.sql("SHOW TABLES LIKE %s", (table_name,), as_dict=True))


def _index_exists(table_name, index_name):
    return bool(
        frappe.db.sql(
            f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s",
            (index_name,),
            as_dict=True,
        )
    )


def _create_indexes(logger):
    for table_name, index_name, fields_sql, unique in INDEX_SPECS:
        if not _table_exists(table_name):
            continue
        if _index_exists(table_name, index_name):
            continue

        unique_sql = "UNIQUE " if unique else ""
        try:
            frappe.db.sql(f"CREATE {unique_sql}INDEX `{index_name}` ON `{table_name}` {fields_sql}")
        except Exception:
            logger.error(
                "failed to create index %s on %s\n%s",
                index_name,
                table_name,
                frappe.get_traceback(),
            )


def _count_parity_checks(logger):
    metrics = {}

    if doctype_exists("HD Ticket"):
        metrics["hd_tickets"] = frappe.db.count("HD Ticket")
    metrics["ms_tickets_from_hd"] = frappe.db.count("MS Support Ticket", {"legacy_ticket_id": ["!=", ""]})

    if doctype_exists("HD Ticket Comment"):
        metrics["hd_comments"] = frappe.db.count("HD Ticket Comment")
    metrics["ms_comments_from_hd"] = frappe.db.count("MS Support Ticket Comment", {"legacy_comment_id": ["!=", ""]})

    if doctype_exists("HD Ticket Activity"):
        metrics["hd_activities"] = frappe.db.count("HD Ticket Activity")
    metrics["ms_activities_from_hd"] = frappe.db.count("MS Support Ticket Activity", {"legacy_activity_id": ["!=", ""]})

    if doctype_exists("Communication"):
        metrics["hd_communications"] = frappe.db.count("Communication", {"reference_doctype": "HD Ticket"})
        metrics["ms_communications_from_hd"] = frappe.db.count(
            "Communication",
            {
                "reference_doctype": "MS Support Ticket",
                "message_id": ["like", "ms-mig-%"],
            },
        )

    if metrics.get("hd_tickets") is not None:
        metrics["ticket_count_parity_ok"] = metrics["hd_tickets"] == metrics["ms_tickets_from_hd"]
    if metrics.get("hd_comments") is not None:
        metrics["comment_count_parity_ok"] = metrics["hd_comments"] == metrics["ms_comments_from_hd"]
    if metrics.get("hd_activities") is not None:
        metrics["activity_count_parity_ok"] = metrics["hd_activities"] == metrics["ms_activities_from_hd"]

    logger.info("migration parity metrics: %s", metrics)


def _response_time_spot_check(logger):
    if not doctype_exists("HD Ticket"):
        return

    rows = frappe.db.sql(
        """
        SELECT
            hd.name AS hd_ticket,
            COALESCE(hd.first_response_time, 0) AS hd_first_response_time,
            COALESCE(ms.first_response_time, 0) AS ms_first_response_time,
            COALESCE(hd.avg_response_time, 0) AS hd_avg_response_time,
            COALESCE(ms.avg_response_time, 0) AS ms_avg_response_time
        FROM `tabHD Ticket` hd
        INNER JOIN `tabMS Support Ticket` ms ON ms.legacy_ticket_id = hd.name
        ORDER BY hd.modified DESC
        LIMIT 50
        """,
        as_dict=True,
    )

    mismatches = []
    for row in rows:
        hd_frt = float(row.get("hd_first_response_time") or 0)
        ms_frt = float(row.get("ms_first_response_time") or 0)
        hd_art = float(row.get("hd_avg_response_time") or 0)
        ms_art = float(row.get("ms_avg_response_time") or 0)

        if abs(hd_frt - ms_frt) > 1 or abs(hd_art - ms_art) > 1:
            mismatches.append(
                {
                    "ticket": row.get("hd_ticket"),
                    "hd_first_response_time": hd_frt,
                    "ms_first_response_time": ms_frt,
                    "hd_avg_response_time": hd_art,
                    "ms_avg_response_time": ms_art,
                }
            )

    logger.info(
        "response time spot-check sample=%s mismatches=%s details=%s",
        len(rows),
        len(mismatches),
        mismatches[:10],
    )


def execute():
    logger = migration_logger()

    if not doctype_exists("MS Support Ticket"):
        logger.warning("skip post checks; MS Support Ticket missing")
        return

    _create_indexes(logger)
    _count_parity_checks(logger)
    _response_time_spot_check(logger)

    frappe.db.commit()
