from __future__ import annotations

from dataclasses import dataclass

import frappe
from frappe import _

SUPER_ADMIN_ROLES = {"System Manager"}
LEGACY_MANAGER_ROLES = {"Website Manager"}

CAPABILITY_ROLE_MAP = {
    "management.access": {
        "Mysite Content Editor",
        "Mysite Content Reviewer",
        "Mysite Content Publisher",
        "Mysite Product Editor",
        "Mysite Product Reviewer",
        "Mysite Product Publisher",
        "Mysite Support Manager",
        "Mysite Analytics Manager",
        "Mysite Audit Viewer",
    },
    "content.edit": {"Mysite Content Editor", "Mysite Content Reviewer", "Mysite Content Publisher"},
    "content.review": {"Mysite Content Reviewer", "Mysite Content Publisher"},
    "content.publish": {"Mysite Content Publisher"},
    "product.edit": {"Mysite Product Editor", "Mysite Product Reviewer", "Mysite Product Publisher"},
    "product.review": {"Mysite Product Reviewer", "Mysite Product Publisher"},
    "product.publish": {"Mysite Product Publisher"},
    "support.manage": {"Mysite Support Manager"},
    "analytics.view": {"Mysite Analytics Manager"},
    "analytics.manage": {"Mysite Analytics Manager"},
    "audit.view": {"Mysite Audit Viewer"},
}


@dataclass
class PermissionContext:
    user: str
    roles: set[str]
    capabilities: set[str]


def _target_user(user: str | None = None) -> str:
    candidate = (user or frappe.session.user or "").strip()
    return candidate or "Guest"


def get_roles(user: str | None = None) -> set[str]:
    target = _target_user(user)
    if target == "Guest":
        return set()
    try:
        return set(frappe.get_roles(target) or [])
    except Exception:
        return set()


def is_super_admin(user: str | None = None) -> bool:
    roles = get_roles(user=user)
    return bool(roles & SUPER_ADMIN_ROLES)


def capability_roles(capability: str) -> set[str]:
    return set(CAPABILITY_ROLE_MAP.get(str(capability or "").strip(), set()))


def get_capabilities(user: str | None = None) -> set[str]:
    roles = get_roles(user=user)
    if not roles:
        return set()

    if roles & SUPER_ADMIN_ROLES:
        return set(CAPABILITY_ROLE_MAP)
    if roles & LEGACY_MANAGER_ROLES:
        return set(CAPABILITY_ROLE_MAP)

    capabilities = set()
    for key, allowed_roles in CAPABILITY_ROLE_MAP.items():
        if roles & set(allowed_roles):
            capabilities.add(key)
    return capabilities


def context(user: str | None = None) -> PermissionContext:
    target = _target_user(user)
    roles = get_roles(target)
    capabilities = get_capabilities(target)
    return PermissionContext(user=target, roles=roles, capabilities=capabilities)


def has_capability(capability: str, user: str | None = None) -> bool:
    target = _target_user(user)
    if target == "Guest":
        return False
    if is_super_admin(target):
        return True
    return str(capability or "").strip() in get_capabilities(target)


def require_capability(capability: str, user: str | None = None, message: str | None = None):
    target = _target_user(user)
    if target == "Guest":
        frappe.throw(_("ابتدا وارد حساب کاربری شوید."), frappe.PermissionError)
    if has_capability(capability, target):
        return
    msg = message or _("دسترسی لازم برای انجام این عملیات را ندارید.")
    frappe.throw(msg, frappe.PermissionError)


def can_access_management(user: str | None = None) -> bool:
    return has_capability("management.access", user=user)
