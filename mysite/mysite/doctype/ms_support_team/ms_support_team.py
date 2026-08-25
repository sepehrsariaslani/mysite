import frappe
from frappe import _
from frappe.model.document import Document


class MSSupportTeam(Document):
    def validate(self):
        seen = set()
        for row in self.members or []:
            user = str(row.user or "").strip()
            if not user:
                continue
            if user in seen:
                frappe.throw(_("Duplicate team member is not allowed."))
            seen.add(user)
