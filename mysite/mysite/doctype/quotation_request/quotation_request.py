import frappe
from frappe import _
from frappe.model.document import Document


def _get_default_customer_group():
    try:
        setting_value = frappe.db.get_single_value("Selling Settings", "customer_group")
    except Exception:
        setting_value = None

    return setting_value or frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or _(
        "All Customer Groups"
    )


def _get_default_territory():
    try:
        setting_value = frappe.db.get_single_value("Selling Settings", "territory")
    except Exception:
        setting_value = None

    return setting_value or frappe.db.get_value("Territory", {"is_group": 0}, "name") or _(
        "All Territories"
    )


def resolve_or_create_customer(customer_name=None, email=None, phone=None):
    customer_name = (customer_name or "").strip()
    email = (email or "").strip() or None
    phone = (phone or "").strip() or None

    customer = None
    if email:
        customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    if not customer and phone:
        customer = frappe.db.get_value("Customer", {"mobile_no": phone}, "name")
    if not customer and customer_name:
        customer = frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")

    if customer:
        return customer

    customer_doc = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": customer_name or phone or email or _("Guest"),
            "customer_type": "Individual",
            "email_id": email,
            "mobile_no": phone,
            "customer_group": _get_default_customer_group(),
            "territory": _get_default_territory(),
        }
    )
    customer_doc.insert(ignore_permissions=True)
    return customer_doc.name


class QuotationRequest(Document):
    def validate(self):
        if not self.status:
            self.status = "Submitted"

        if self.customer:
            customer_meta = frappe.db.get_value(
                "Customer",
                self.customer,
                ["customer_name", "email_id", "mobile_no"],
                as_dict=True,
            ) or {}
            self.customer_name = self.customer_name or customer_meta.get("customer_name") or self.customer
            self.email = self.email or customer_meta.get("email_id")
            self.phone = self.phone or customer_meta.get("mobile_no")
        else:
            self.customer = resolve_or_create_customer(
                customer_name=self.customer_name, email=self.email, phone=self.phone
            )

        if not self.customer_name:
            self.customer_name = self.customer or _("Guest")


@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.quotation_to = "Customer"
        if source.customer:
            target.party_name = source.customer
        if source.request_note:
            target.tc_name = ""
            target.terms = (target.terms or "") + f"\n\nPortal Request Note:\n{source.request_note}"

    doclist = get_mapped_doc(
        "Quotation Request",
        source_name,
        {
            "Quotation Request": {
                "doctype": "Quotation",
                "field_map": {
                    "customer": "party_name",
                },
            },
            "Quotation Request Item": {
                "doctype": "Quotation Item",
                "field_map": {
                    "item_code": "item_code",
                    "item_name": "item_name",
                    "qty": "qty",
                    "price": "rate",
                },
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist
