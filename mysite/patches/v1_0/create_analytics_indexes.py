import frappe


INDEX_SPECS = [
    ("Analytics Event", "idx_analytics_event_occurred", "(`occurred_at`)", False),
    ("Analytics Event", "idx_analytics_event_session", "(`session_id`)", False),
    ("Analytics Event", "idx_analytics_event_type_time", "(`event_type`, `occurred_at`)", False),
    ("Page View", "idx_page_view_entered", "(`entered_at`)", False),
    ("Page View", "idx_page_view_session", "(`session_id`)", False),
    ("Page View", "idx_page_view_url", "(`url`)", False),
    ("Cart Event", "idx_cart_event_occurred", "(`occurred_at`)", False),
    ("Cart Event", "idx_cart_event_session_action", "(`session_id`, `action`)", False),
    ("Funnel Step", "idx_funnel_step_occurred", "(`occurred_at`)", False),
    ("Funnel Step", "idx_funnel_step_session", "(`session_id`)", False),
    ("Funnel Step", "idx_funnel_step_name_time", "(`step_name`, `occurred_at`)", False),
]


def _has_index(table_name, index_name):
    rows = frappe.db.sql(
        f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s",
        (index_name,),
        as_dict=True,
    )
    return bool(rows)


def _table_exists(table_name):
    rows = frappe.db.sql("SHOW TABLES LIKE %s", (table_name,), as_dict=True)
    return bool(rows)


def execute():
    for doctype, index_name, fields_sql, unique in INDEX_SPECS:
        if not frappe.db.exists("DocType", doctype):
            continue
        table_name = f"tab{doctype}"
        if not _table_exists(table_name):
            continue
        if _has_index(table_name, index_name):
            continue
        uniqueness = "UNIQUE " if unique else ""
        frappe.db.sql(
            f"CREATE {uniqueness}INDEX `{index_name}` ON `{table_name}` {fields_sql}"
        )

    frappe.db.commit()
