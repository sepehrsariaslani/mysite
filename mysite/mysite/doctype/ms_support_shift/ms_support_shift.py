import frappe
from frappe import _
from frappe.model.document import Document


class MSSupportShift(Document):
    def validate(self):
        self._validate_members()

    def _validate_members(self):
        seen = set()
        for row in self.members or []:
            user = str(row.user or "").strip()
            if not user:
                continue
            if user in seen:
                frappe.throw(_("Duplicate shift member is not allowed."))
            seen.add(user)
