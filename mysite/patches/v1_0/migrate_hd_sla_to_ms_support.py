import frappe

from mysite.patches.v1_0.ms_support_migration_utils import (
    doctype_exists,
    first_ms_open_status,
    map_existing_name,
    map_user,
    migration_logger,
    to_int,
)


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


def _map_status(value):
    fallback = first_ms_open_status()
    status = map_existing_name("MS Support Ticket Status", value, fallback=fallback)
    return status


def _map_priority(value):
    default_priority = frappe.db.get_value(
        "MS Support Ticket Priority",
        {"enabled": 1},
        "name",
        order_by="weight asc, modified asc",
    )
    return map_existing_name("MS Support Ticket Priority", value, fallback=default_priority)


def _sync_sla_priorities(ms_sla_doc, hd_sla_name):
    ms_sla_doc.priorities = []
    if not doctype_exists("HD Service Level Priority"):
        return

    rows = frappe.get_all(
        "HD Service Level Priority",
        filters={"parent": hd_sla_name, "parenttype": "HD Service Level Agreement"},
        fields=["priority", "default_priority", "response_time", "resolution_time"],
        order_by="idx asc",
        ignore_permissions=True,
        limit_page_length=0,
    )

    for row in rows:
        priority = _map_priority(row.get("priority"))
        if not priority:
            continue
        ms_sla_doc.append(
            "priorities",
            {
                "priority": priority,
                "default_priority": 1 if to_int(row.get("default_priority"), 0) else 0,
                "response_time": row.get("response_time") or 0,
                "resolution_time": row.get("resolution_time") or 0,
            },
        )

    if not ms_sla_doc.priorities:
        fallback_priority = _map_priority(None)
        if fallback_priority:
            ms_sla_doc.append(
                "priorities",
                {
                    "priority": fallback_priority,
                    "default_priority": 1,
                    "response_time": 3600,
                    "resolution_time": 0,
                },
            )


def _sync_sla_workdays(ms_sla_doc, hd_sla_name):
    ms_sla_doc.support_and_resolution = []
    if not doctype_exists("HD Service Day"):
        return

    rows = frappe.get_all(
        "HD Service Day",
        filters={"parent": hd_sla_name, "parenttype": "HD Service Level Agreement"},
        fields=["workday", "start_time", "end_time"],
        order_by="idx asc",
        ignore_permissions=True,
        limit_page_length=0,
    )

    for row in rows:
        ms_sla_doc.append(
            "support_and_resolution",
            {
                "workday": row.get("workday"),
                "start_time": row.get("start_time"),
                "end_time": row.get("end_time"),
            },
        )


def _update_settings_default_sla(hd_to_ms):
    if not frappe.db.exists("MS Support Settings", "MS Support Settings"):
        return
    if not doctype_exists("HD Service Level Agreement"):
        return

    hd_default = frappe.db.get_value("HD Service Level Agreement", {"default_sla": 1}, "name")
    if not hd_default:
        return

    mapped = hd_to_ms.get(hd_default)
    if not mapped:
        return

    settings = frappe.get_doc("MS Support Settings", "MS Support Settings")
    settings.default_sla = mapped
    settings.save(ignore_permissions=True)


def _sync_ticket_sla_links(hd_to_ms):
    if not doctype_exists("HD Ticket"):
        return

    rows = frappe.db.sql(
        """
        SELECT
            ms.name AS ms_ticket,
            hd.sla AS hd_sla
        FROM `tabMS Support Ticket` ms
        INNER JOIN `tabHD Ticket` hd ON hd.name = ms.legacy_ticket_id
        WHERE IFNULL(hd.sla, '') != ''
        """,
        as_dict=True,
    )

    for row in rows:
        hd_sla = str(row.get("hd_sla") or "").strip()
        ms_ticket = str(row.get("ms_ticket") or "").strip()
        if not hd_sla or not ms_ticket:
            continue

        ms_sla = hd_to_ms.get(hd_sla) or map_existing_name("MS Support SLA", hd_sla)
        if not ms_sla:
            continue

        frappe.db.set_value("MS Support Ticket", ms_ticket, "sla", ms_sla, update_modified=False)


def execute():
    logger = migration_logger()

    required = ["MS Support SLA", "MS Support SLA Priority", "MS Support SLA Workday"]
    for doctype in required:
        if not doctype_exists(doctype):
            logger.warning("skip sla migration; missing doctype: %s", doctype)
            return

    if not doctype_exists("HD Service Level Agreement"):
        logger.info("skip sla migration; HD Service Level Agreement doctype not found")
        return

    rows = frappe.get_all(
        "HD Service Level Agreement",
        fields=[
            "name",
            "service_level",
            "enabled",
            "default_sla",
            "apply_sla_for_resolution",
            "start_date",
            "end_date",
            "condition",
            "default_ticket_status",
            "ticket_reopen_status",
            "creation",
            "modified",
            "owner",
        ],
        order_by="modified asc",
        ignore_permissions=True,
        limit_page_length=0,
    )

    migrated = 0
    failed = 0
    hd_to_ms = {}

    for row in rows:
        hd_name = str(row.get("name") or "").strip()
        sla_name = str(row.get("service_level") or hd_name).strip()
        if not hd_name or not sla_name:
            continue

        try:
            if frappe.db.exists("MS Support SLA", sla_name):
                doc = frappe.get_doc("MS Support SLA", sla_name)
            else:
                doc = frappe.new_doc("MS Support SLA")

            doc.sla_name = sla_name
            doc.enabled = 1 if to_int(row.get("enabled"), 1) else 0
            doc.default_sla = 1 if to_int(row.get("default_sla"), 0) else 0
            doc.apply_sla_for_resolution = 1 if to_int(row.get("apply_sla_for_resolution"), 1) else 0
            doc.start_date = row.get("start_date")
            doc.end_date = row.get("end_date")
            doc.condition = row.get("condition") or ""
            doc.default_ticket_status = _map_status(row.get("default_ticket_status"))
            doc.ticket_reopen_status = _map_status(row.get("ticket_reopen_status"))

            _sync_sla_priorities(doc, hd_name)
            _sync_sla_workdays(doc, hd_name)

            doc.save(ignore_permissions=True)
            _set_creation_metadata("MS Support SLA", doc.name, row)

            hd_to_ms[hd_name] = doc.name
            hd_to_ms[sla_name] = doc.name
            migrated += 1
        except Exception:
            failed += 1
            logger.error("failed to migrate sla %s\n%s", hd_name, frappe.get_traceback())

    _update_settings_default_sla(hd_to_ms)
    _sync_ticket_sla_links(hd_to_ms)

    logger.info("sla migration completed: migrated=%s failed=%s", migrated, failed)
    frappe.db.commit()
