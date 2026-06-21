import frappe

from mysite.www.about_service import DEFAULT_ABOUT_PAYLOAD


SCALAR_FIELDS = [
	"title",
	"subtitle",
	"hero_intro",
	"founded_year",
	"mission_title",
	"mission_body",
	"vision_title",
	"vision_body",
	"history_title",
	"history_intro",
	"history_body",
]

VALUE_FIELDS = ["icon", "value_title", "value_description", "sort_order", "is_active"]
TIMELINE_FIELDS = [
	"year_label",
	"milestone_title",
	"milestone_description",
	"sort_order",
	"is_highlight",
	"is_active",
]


def _table_exists(table_name: str) -> bool:
	try:
		frappe.db.sql("show columns from `{}`".format(table_name))
		return True
	except Exception:
		return False


def _get_table_columns(table_name: str) -> set[str]:
	if not _table_exists(table_name):
		return set()

	rows = frappe.db.sql("show columns from `{}`".format(table_name), as_dict=True) or []
	return {str(row.get("Field") or "").strip() for row in rows if row.get("Field")}


def _get_source_about_row():
	table_name = "tabWebsite About"
	if not _table_exists(table_name):
		return None

	columns = _get_table_columns(table_name)
	select_fields = [field for field in ["name", *SCALAR_FIELDS] if field in columns]
	if not select_fields:
		return None

	order_by = []
	if "is_published" in columns:
		order_by.append("ifnull(is_published, 1) desc")
	if "sort_order" in columns:
		order_by.append("ifnull(sort_order, 0) asc")
	if "modified" in columns:
		order_by.append("modified desc")
	if not order_by:
		order_by.append("name asc")

	query = """
		select {fields}
		from `tabWebsite About`
		order by {order_by}
		limit 1
	""".format(
		fields=", ".join(f"`{field}`" for field in select_fields),
		order_by=", ".join(order_by),
	)

	rows = frappe.db.sql(query, as_dict=True)
	return rows[0] if rows else None


def _get_child_rows(table_name: str, parent_name: str, parentfield: str, candidate_fields: list[str]):
	if not _table_exists(table_name):
		return []

	columns = _get_table_columns(table_name)
	select_fields = [field for field in candidate_fields if field in columns]
	if "idx" in columns and "idx" not in select_fields:
		select_fields.append("idx")
	if not select_fields:
		return []

	conditions = ["parent = %s"]
	params = [parent_name]

	if "parenttype" in columns:
		conditions.append("parenttype = 'Website About'")
	if "parentfield" in columns:
		conditions.append("parentfield = %s")
		params.append(parentfield)

	order_by = []
	if "sort_order" in columns:
		order_by.append("ifnull(sort_order, 0) asc")
	if "idx" in columns:
		order_by.append("idx asc")
	if "modified" in columns:
		order_by.append("modified asc")
	if not order_by:
		order_by.append("name asc")

	query = """
		select {fields}
		from `{table_name}`
		where {where_clause}
		order by {order_by}
	""".format(
		fields=", ".join(f"`{field}`" for field in select_fields),
		table_name=table_name,
		where_clause=" and ".join(conditions),
		order_by=", ".join(order_by),
	)

	return frappe.db.sql(query, tuple(params), as_dict=True) or []


def _copy_scalar_fields(doc, source_row: dict):
	for fieldname in SCALAR_FIELDS:
		if fieldname not in source_row:
			continue
		value = source_row.get(fieldname)
		if value in (None, ""):
			continue
		doc.set(fieldname, value)


def _copy_value_rows(doc, rows):
	if not rows:
		return

	doc.set("core_values", [])
	for row in rows:
		doc.append(
			"core_values",
			{
				"icon": row.get("icon") or "",
				"value_title": row.get("value_title") or "",
				"value_description": row.get("value_description") or "",
				"sort_order": row.get("sort_order") or 0,
				"is_active": 0 if str(row.get("is_active") or "1") in ("0", "false", "False") else 1,
			},
		)


def _copy_timeline_rows(doc, rows):
	if not rows:
		return

	doc.set("history_timeline", [])
	for row in rows:
		doc.append(
			"history_timeline",
			{
				"year_label": row.get("year_label") or "",
				"milestone_title": row.get("milestone_title") or "",
				"milestone_description": row.get("milestone_description") or "",
				"sort_order": row.get("sort_order") or 0,
				"is_highlight": 0
				if str(row.get("is_highlight") or "0") in ("0", "false", "False")
				else 1,
				"is_active": 0 if str(row.get("is_active") or "1") in ("0", "false", "False") else 1,
			},
        )


def _has_single_content() -> bool:
    return any(
        str(frappe.db.get_single_value("Website About", fieldname) or "").strip()
        for fieldname in ("title", "mission_title", "vision_title", "history_title")
    )


def _default_source_row():
    return {
        "title": DEFAULT_ABOUT_PAYLOAD["hero"]["title"],
        "subtitle": DEFAULT_ABOUT_PAYLOAD["hero"]["subtitle"],
        "hero_intro": DEFAULT_ABOUT_PAYLOAD["hero"]["intro"],
        "founded_year": DEFAULT_ABOUT_PAYLOAD["hero"]["founded_year"],
        "mission_title": DEFAULT_ABOUT_PAYLOAD["mission"]["title"],
        "mission_body": DEFAULT_ABOUT_PAYLOAD["mission"]["body"],
        "vision_title": DEFAULT_ABOUT_PAYLOAD["vision"]["title"],
        "vision_body": DEFAULT_ABOUT_PAYLOAD["vision"]["body"],
        "history_title": DEFAULT_ABOUT_PAYLOAD["history"]["title"],
        "history_intro": DEFAULT_ABOUT_PAYLOAD["history"]["intro"],
        "history_body": DEFAULT_ABOUT_PAYLOAD["history"]["body"],
    }


def _default_value_rows():
    rows = []
    for index, row in enumerate(DEFAULT_ABOUT_PAYLOAD.get("values") or []):
        rows.append(
            {
                "icon": row.get("icon") or "",
                "value_title": row.get("title") or "",
                "value_description": row.get("description") or "",
                "sort_order": (index + 1) * 10,
                "is_active": 1,
            }
        )
    return rows


def _default_timeline_rows():
    rows = []
    for index, row in enumerate(DEFAULT_ABOUT_PAYLOAD.get("timeline") or []):
        rows.append(
            {
                "year_label": row.get("year") or "",
                "milestone_title": row.get("title") or "",
                "milestone_description": row.get("description") or "",
                "sort_order": (index + 1) * 10,
                "is_highlight": 1 if str(row.get("highlight") or "0") in ("1", "true", "True") else 0,
                "is_active": 1,
            }
        )
    return rows


def execute():
    if not frappe.db.exists("DocType", "Website About"):
        return

    source_row = _get_source_about_row()
    value_rows = []
    timeline_rows = []

    if source_row:
        parent_name = source_row.get("name")
        value_rows = _get_child_rows(
            "tabWebsite About Value",
            parent_name,
            "core_values",
            VALUE_FIELDS,
        )
        timeline_rows = _get_child_rows(
            "tabWebsite About Timeline",
            parent_name,
            "history_timeline",
            TIMELINE_FIELDS,
        )
    elif _has_single_content():
        return
    else:
        source_row = _default_source_row()
        value_rows = _default_value_rows()
        timeline_rows = _default_timeline_rows()

    doc = frappe.get_single("Website About")
    _copy_scalar_fields(doc, source_row)
    _copy_value_rows(doc, value_rows)
    _copy_timeline_rows(doc, timeline_rows)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
