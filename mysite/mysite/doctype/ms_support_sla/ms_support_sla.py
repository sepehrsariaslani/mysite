import frappe
from frappe import _
from frappe.model.document import Document


class MSSupportSLA(Document):
    def validate(self):
        self._validate_defaults()
        self._validate_priorities()
        self._validate_workdays()

    def _validate_defaults(self):
        if not self.default_sla:
            return
        existing = frappe.db.get_value(
            "MS Support SLA",
            {"default_sla": 1, "name": ["!=", self.name]},
            "name",
        )
        if existing:
            frappe.db.set_value("MS Support SLA", existing, "default_sla", 0, update_modified=False)

    def _validate_priorities(self):
        if not self.priorities:
            frappe.throw(_("SLA priorities are required."))

        seen = set()
        default_count = 0
        for row in self.priorities:
            priority = str(row.priority or "").strip()
            if not priority:
                frappe.throw(_("Priority is required in SLA row."))
            if priority in seen:
                frappe.throw(_("Duplicate priority in SLA rows."))
            seen.add(priority)

            response_seconds = frappe.utils.cint(row.response_time or 0)
            resolution_seconds = frappe.utils.cint(row.resolution_time or 0)
            if response_seconds <= 0:
                frappe.throw(_("First response time must be greater than zero."))

            if self.apply_sla_for_resolution and resolution_seconds <= 0:
                frappe.throw(_("Resolution time is required when resolution SLA is enabled."))

            if self.apply_sla_for_resolution and resolution_seconds and resolution_seconds < response_seconds:
                frappe.throw(_("Resolution time cannot be less than first response time."))

            if row.default_priority:
                default_count += 1

        if default_count > 1:
            frappe.throw(_("Only one default priority is allowed."))

    def _validate_workdays(self):
        seen = set()
        for row in self.support_and_resolution or []:
            key = str(row.workday or "").strip()
            if not key:
                continue
            if key in seen:
                frappe.throw(_("Duplicate workday in SLA schedule."))
            seen.add(key)
