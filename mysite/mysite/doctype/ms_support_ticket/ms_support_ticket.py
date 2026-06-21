import json

import frappe
from frappe import _
from frappe.model.document import Document

from mysite import support_service


class MSSupportTicket(Document):
    def before_validate(self):
        support_service.prepare_ticket_defaults(self)

    def validate(self):
        self._sync_feedback()
        support_service.sync_ticket_state(self)

    def on_update(self):
        if self.has_value_changed("status"):
            support_service.create_ticket_activity(self.name, f"set status to {self.status}")
        if self.has_value_changed("priority"):
            support_service.create_ticket_activity(self.name, f"set priority to {self.priority}")
        if self.has_value_changed("team"):
            support_service.create_ticket_activity(self.name, f"set team to {self.team}")
        if self.has_value_changed("assigned_to"):
            support_service.create_ticket_activity(self.name, f"assigned to {self.assigned_to or 'unassigned'}")

    def _sync_feedback(self):
        if not self.feedback:
            self.feedback_rating = 0
            return
        rating = frappe.db.get_value("MS Support Ticket Feedback Option", self.feedback, "rating")
        self.feedback_rating = frappe.utils.cint(rating or 0)


# Hooked via hooks.has_permission / hooks.permission_query_conditions

def has_permission(doc, user=None):
    target = user or frappe.session.user
    if support_service.has_management_access(target):
        return True

    if not target or target == "Guest":
        return False

    if str(doc.raised_by or "") == target:
        return True

    try:
        allowed_customers = support_service.get_allowed_customers(target)
    except Exception:
        allowed_customers = []

    return bool(doc.customer and doc.customer in allowed_customers)


def permission_query(user):
    if not user:
        user = frappe.session.user

    if support_service.has_management_access(user):
        return None

    if not user or user == "Guest":
        return "1=0"

    try:
        customers = support_service.get_allowed_customers(user)
    except Exception:
        customers = []

    parts = [f"`tabMS Support Ticket`.raised_by={frappe.db.escape(user)}"]
    for customer in customers:
        parts.append(f"`tabMS Support Ticket`.customer={frappe.db.escape(customer)}")

    if not parts:
        return "1=0"
    return "(" + " OR ".join(parts) + ")"
