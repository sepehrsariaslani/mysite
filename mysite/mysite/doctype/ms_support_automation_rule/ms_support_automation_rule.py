import frappe
from frappe import _
from frappe.model.document import Document


class MSSupportAutomationRule(Document):
    def validate(self):
        if not self.actions:
            frappe.throw(_("At least one automation action is required."))
