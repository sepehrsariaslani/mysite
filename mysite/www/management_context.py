from __future__ import annotations

import frappe

from mysite.management_permissions import (
    can_access_management as can_access_management_permission,
    context as permission_context,
    has_capability,
)


def apply_management_context(context, required_capability: str = "management.access"):
    required_capability = str(required_capability or "management.access").strip() or "management.access"
    permissions = permission_context()
    allowed = can_access_management_permission()
    required_allowed = has_capability(required_capability)
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""

    context.no_cache = 1
    context.csrf_token = csrf_token
    context.management_allowed = allowed
    context.management_roles = sorted(permissions.roles)
    context.management_capabilities = sorted(permissions.capabilities)
    context.required_capability = required_capability
    context.required_allowed = required_allowed
    context.management_boot = {
        "allowed": allowed,
        "required_allowed": required_allowed,
        "required_capability": required_capability,
        "roles": sorted(permissions.roles),
        "capabilities": sorted(permissions.capabilities),
        "user": frappe.session.user,
        "csrf_token": csrf_token,
    }
    if not isinstance(getattr(context, "boot", None), dict):
        context.boot = {}
    context.boot["csrf_token"] = csrf_token
    return context
