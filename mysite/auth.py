import frappe


def on_login(login_manager):
    """Redirect admin users to /management after login instead of Desk."""
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            return

        roles = set(frappe.get_roles(user))
        skip_roles = {"System Manager", "Administrator", "Manager"}
        if not skip_roles.intersection(roles):
            return

        # Check if user came from a management page or just logged in
        referer = frappe.request.headers.get("Referer", "") if frappe.request else ""
        redirect_to = frappe.local.form_dict.get("redirect-to", "") if hasattr(frappe.local, "form_dict") else ""

        # Always redirect admin users to management after login
        if "/login" in referer or "/management" in referer or "/management" in redirect_to or not referer:
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = "/management"
    except Exception:
        # Never break login flow
        pass
