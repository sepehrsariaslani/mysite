import frappe

from mysite.mysite.doctype.quotation_request.quotation_request import resolve_or_create_customer


def execute():
    rows = frappe.db.sql(
        """
        SELECT name, customer_name, email, phone
        FROM `tabQuotation Request`
        WHERE IFNULL(customer, '') = ''
        """,
        as_dict=True,
    )

    for row in rows:
        customer = resolve_or_create_customer(
            customer_name=row.get("customer_name"),
            email=row.get("email"),
            phone=row.get("phone"),
        )
        frappe.db.set_value("Quotation Request", row["name"], "customer", customer, update_modified=False)

    if rows:
        frappe.db.commit()
