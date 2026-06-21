import json
from datetime import datetime, time
from collections import defaultdict
from email.utils import parseaddr

import frappe
from frappe import _
from frappe.utils import (
    add_to_date,
    cint,
    flt,
    get_datetime,
    getdate,
    now_datetime,
    nowdate,
    time_diff_in_seconds,
)

from erpnext.controllers.website_list_for_contact import get_parents_for_user

from mysite.management_permissions import has_capability, require_capability

SUPPORT_MANAGER_ROLES = {"System Manager", "Website Manager", "Mysite Support Manager"}
SUPPORT_CORE_DOCTYPES = [
    "MS Support Settings",
    "MS Support Ticket Status",
    "MS Support Ticket Priority",
    "MS Support Ticket Type",
    "MS Support Team",
    "MS Support Team Member",
    "MS Support SLA",
    "MS Support SLA Priority",
    "MS Support SLA Workday",
    "MS Support Ticket",
    "MS Support Ticket Comment",
    "MS Support Ticket Activity",
    "MS Support Ticket Feedback Option",
]
SUPPORT_PHASE2_DOCTYPES = [
    "MS Support Chat Link",
    "MS Support Shift",
    "MS Support Shift Member",
    "MS Support Shift Exception",
    "MS Support Automation Rule",
    "MS Support Automation Rule Condition",
    "MS Support Automation Rule Action",
    "MS Support Macro",
    "MS Support Notification Preference",
]


def _doctype_exists(doctype):
    return bool(frappe.db.exists("DocType", doctype))


def support_runtime_health(include_phase2=False):
    required = list(SUPPORT_CORE_DOCTYPES)
    if include_phase2:
        required.extend(SUPPORT_PHASE2_DOCTYPES)

    missing_doctypes = [doctype for doctype in required if not _doctype_exists(doctype)]

    def _needs_table(doctype):
        if not _doctype_exists(doctype):
            return False
        try:
            meta = frappe.get_meta(doctype)
            if cint(meta.get("issingle")) == 1:
                return False
            if cint(meta.get("is_virtual")) == 1:
                return False
        except Exception:
            pass
        return True

    missing_tables = [doctype for doctype in required if _needs_table(doctype) and not frappe.db.table_exists(doctype)]

    ready = not missing_doctypes and not missing_tables
    if ready:
        message = _("زیرساخت پشتیبانی آماده است.")
    else:
        site = frappe.local.site if getattr(frappe, "local", None) else "site-name"
        message = _(
            "ساختار پشتیبانی آماده نیست. دستورهای `bench --site {0} migrate` و `bench --site {0} clear-cache` را اجرا کنید."
        ).format(site)

    return {
        "ready": ready,
        "missing_doctypes": missing_doctypes,
        "missing_tables": missing_tables,
        "message": message,
    }


def ensure_support_runtime_ready(include_phase2=False, throw=True):
    health = support_runtime_health(include_phase2=include_phase2)
    if health.get("ready"):
        return health
    if throw:
        frappe.throw(health.get("message"), frappe.ValidationError)
    return health


def management_roles(user=None):
    target = user or frappe.session.user
    if not target or target == "Guest":
        return set()
    try:
        return set(frappe.get_roles(target) or [])
    except Exception:
        return set()


def has_management_access(user=None):
    return has_capability("support.manage", user=user)


def require_management_access():
    require_capability("support.manage", message=_("دسترسی لازم برای مدیریت پشتیبانی را ندارید."))


def require_authenticated_user():
    if frappe.session.user == "Guest":
        frappe.throw(_("برای ثبت یا مشاهده تیکت باید وارد شوید."), frappe.PermissionError)
    return frappe.session.user


def get_allowed_customers(user=None):
    target = user or require_authenticated_user()
    if target == frappe.session.user:
        customers = get_parents_for_user("Customer") or []
    else:
        current_user = frappe.session.user
        try:
            frappe.set_user(target)
            customers = get_parents_for_user("Customer") or []
        except Exception:
            customers = []
        finally:
            frappe.set_user(current_user)
    unique = []
    seen = set()
    for customer in customers:
        if customer and customer not in seen:
            seen.add(customer)
            unique.append(customer)
    return unique


def resolve_customer_scope(customer=None, user=None):
    allowed = get_allowed_customers(user=user)
    if customer:
        if customer not in allowed:
            frappe.throw(_("به مشتری انتخاب‌شده دسترسی ندارید."), frappe.PermissionError)
        return [customer], allowed
    return allowed, allowed


def _status_meta(status_name):
    if not status_name:
        return {}
    return frappe.db.get_value(
        "MS Support Ticket Status",
        status_name,
        ["category", "label_agent", "enabled"],
        as_dict=True,
    ) or {}


def get_status_category(status_name):
    return (_status_meta(status_name).get("category") or "Open").strip() or "Open"


def _get_settings():
    if not _doctype_exists("MS Support Settings"):
        return {}
    try:
        return frappe.get_cached_doc("MS Support Settings", "MS Support Settings")
    except Exception:
        return {}


def _settings_value(key, default=None):
    settings = _get_settings()
    if not settings:
        return default
    value = settings.get(key)
    if value in (None, ""):
        return default
    return value


def _default_status():
    configured = _settings_value("default_ticket_status")
    if configured and frappe.db.exists("MS Support Ticket Status", configured):
        return configured

    first_open = frappe.db.get_value(
        "MS Support Ticket Status",
        {"enabled": 1, "category": "Open"},
        "name",
        order_by="modified asc",
    )
    if first_open:
        return first_open

    return frappe.db.get_value("MS Support Ticket Status", {"enabled": 1}, "name")


def _reopen_status():
    configured = _settings_value("ticket_reopen_status")
    if configured and frappe.db.exists("MS Support Ticket Status", configured):
        return configured
    return _default_status()


def _default_priority():
    configured = _settings_value("default_priority")
    if configured and frappe.db.exists("MS Support Ticket Priority", configured):
        return configured
    return frappe.db.get_value("MS Support Ticket Priority", {"enabled": 1}, "name")


def _default_ticket_type():
    configured = _settings_value("default_ticket_type")
    if configured and frappe.db.exists("MS Support Ticket Type", configured):
        return configured
    return frappe.db.get_value("MS Support Ticket Type", {"enabled": 1}, "name")


def _default_team():
    configured = _settings_value("default_team")
    if configured and frappe.db.exists("MS Support Team", configured):
        return configured
    return frappe.db.get_value("MS Support Team", {"enabled": 1}, "name", order_by="modified asc")


def _auto_assign_enabled():
    return cint(_settings_value("auto_assign_tickets", 1)) == 1


def _team_members(team_name):
    if not team_name or not _doctype_exists("MS Support Team Member"):
        return []

    rows = frappe.get_all(
        "MS Support Team Member",
        filters={"parent": team_name, "parenttype": "MS Support Team"},
        fields=["user", "idx"],
        order_by="idx asc",
        ignore_permissions=True,
        limit_page_length=0,
    )
    users = []
    seen = set()
    for row in rows:
        user = str(row.get("user") or "").strip()
        if not user or user in seen:
            continue
        if not frappe.db.exists("User", user):
            continue
        enabled = cint(frappe.db.get_value("User", user, "enabled") or 0)
        if enabled != 1:
            continue
        seen.add(user)
        users.append(user)
    return users


def _pick_round_robin_member(team_name):
    members = _team_members(team_name)
    if not members:
        return ""

    if not frappe.db.exists("MS Support Team", team_name):
        return members[0]

    team_doc = frappe.get_doc("MS Support Team", team_name)
    counter = cint(team_doc.get("round_robin_counter") or 0)
    idx = counter % len(members)
    selected = members[idx]
    team_doc.round_robin_counter = counter + 1
    team_doc.save(ignore_permissions=True)
    return selected


def _apply_ticket_assignment_defaults(ticket_doc):
    if not _doctype_exists("MS Support Team"):
        return

    if ticket_doc.team and not frappe.db.exists("MS Support Team", ticket_doc.team):
        ticket_doc.team = ""
    if ticket_doc.assigned_to and not frappe.db.exists("User", ticket_doc.assigned_to):
        ticket_doc.assigned_to = ""

    if not ticket_doc.team:
        ticket_doc.team = _default_team() or ""

    if ticket_doc.assigned_to:
        return

    if not _auto_assign_enabled() or not ticket_doc.team:
        return

    ticket_doc.assigned_to = _pick_round_robin_member(ticket_doc.team) or ""
    ticket_doc.auto_assigned = 1 if ticket_doc.assigned_to else 0


def _safe_seconds(value):
    try:
        numeric = flt(value or 0)
    except Exception:
        numeric = 0
    if numeric < 0:
        numeric = 0
    return numeric


def _get_sla_priority_row(sla_name, priority_name):
    rows = frappe.get_all(
        "MS Support SLA Priority",
        filters={"parent": sla_name},
        fields=["priority", "default_priority", "response_time", "resolution_time"],
        order_by="idx asc",
        limit_page_length=0,
    )
    if not rows:
        return None

    if priority_name:
        for row in rows:
            if row.get("priority") == priority_name:
                return row

    for row in rows:
        if cint(row.get("default_priority")):
            return row

    return rows[0]


def _pick_sla(priority_name=None):
    if not _doctype_exists("MS Support SLA"):
        return None

    now = now_datetime()
    candidates = frappe.get_all(
        "MS Support SLA",
        filters={"enabled": 1},
        fields=["name", "default_sla", "start_date", "end_date", "apply_sla_for_resolution"],
        order_by="default_sla asc, modified desc",
        limit_page_length=0,
    )

    valid = []
    for row in candidates:
        start = row.get("start_date")
        end = row.get("end_date")
        if start and get_datetime(start) > now:
            continue
        if end and get_datetime(end) < now:
            continue

        priority_row = _get_sla_priority_row(row.get("name"), priority_name)
        if not priority_row:
            continue

        valid.append((row, priority_row))

    if not valid:
        return None, None

    for row, p_row in valid:
        if not cint(row.get("default_sla")):
            return row, p_row

    return valid[0]


def apply_sla_targets(ticket_doc, reset_from_creation=False):
    if not _doctype_exists("MS Support SLA"):
        ticket_doc.sla = ""
        ticket_doc.response_by = None
        ticket_doc.resolution_by = None
        return

    if reset_from_creation or not ticket_doc.service_level_agreement_creation:
        ticket_doc.service_level_agreement_creation = now_datetime()

    sla_row = None
    priority_row = None

    if ticket_doc.sla and frappe.db.exists("MS Support SLA", ticket_doc.sla):
        sla_row = frappe.db.get_value(
            "MS Support SLA",
            ticket_doc.sla,
            ["name", "default_sla", "apply_sla_for_resolution"],
            as_dict=True,
        )
        priority_row = _get_sla_priority_row(ticket_doc.sla, ticket_doc.priority)

    if not sla_row or not priority_row:
        sla_row, priority_row = _pick_sla(priority_name=ticket_doc.priority)

    if not sla_row or not priority_row:
        ticket_doc.sla = ""
        ticket_doc.response_by = None
        ticket_doc.resolution_by = None
        return

    ticket_doc.sla = sla_row.get("name")
    hold_seconds = _safe_seconds(ticket_doc.total_hold_time)
    base = add_to_date(
        ticket_doc.service_level_agreement_creation,
        seconds=hold_seconds,
        as_datetime=True,
    )

    response_seconds = _safe_seconds(priority_row.get("response_time"))
    resolution_seconds = _safe_seconds(priority_row.get("resolution_time"))

    ticket_doc.response_by = (
        add_to_date(base, seconds=response_seconds, as_datetime=True)
        if response_seconds > 0
        else None
    )

    if cint(sla_row.get("apply_sla_for_resolution")) and resolution_seconds > 0:
        ticket_doc.resolution_by = add_to_date(base, seconds=resolution_seconds, as_datetime=True)
    else:
        ticket_doc.resolution_by = None


def _sync_agreement_status(ticket_doc):
    category = get_status_category(ticket_doc.status)
    now = now_datetime()

    if category == "Paused":
        ticket_doc.agreement_status = "Paused"
        return

    response_by = get_datetime(ticket_doc.response_by) if ticket_doc.response_by else None
    resolution_by = get_datetime(ticket_doc.resolution_by) if ticket_doc.resolution_by else None
    first_responded_on = get_datetime(ticket_doc.first_responded_on) if ticket_doc.first_responded_on else None
    resolution_date = get_datetime(ticket_doc.resolution_date) if ticket_doc.resolution_date else None

    if resolution_date:
        if resolution_by and resolution_date > resolution_by:
            ticket_doc.agreement_status = "Failed"
        else:
            ticket_doc.agreement_status = "Fulfilled"
        return

    if not first_responded_on:
        if response_by and now > response_by:
            ticket_doc.agreement_status = "Failed"
        else:
            ticket_doc.agreement_status = "First Response Due"
        return

    if response_by and first_responded_on > response_by:
        ticket_doc.agreement_status = "Failed"
        return

    if resolution_by:
        if now > resolution_by:
            ticket_doc.agreement_status = "Failed"
        else:
            ticket_doc.agreement_status = "Resolution Due"
        return

    ticket_doc.agreement_status = "Fulfilled"


def prepare_ticket_defaults(ticket_doc):
    if not ticket_doc.raised_by:
        ticket_doc.raised_by = frappe.session.user if frappe.session.user != "Guest" else "Guest"

    if not ticket_doc.status:
        ticket_doc.status = _default_status()

    ticket_doc.status_category = get_status_category(ticket_doc.status)

    if not ticket_doc.priority:
        ticket_doc.priority = _default_priority() or ""

    if not ticket_doc.ticket_type:
        ticket_doc.ticket_type = _default_ticket_type() or ""

    _apply_ticket_assignment_defaults(ticket_doc)

    if ticket_doc.is_new():
        if not ticket_doc.opening_date:
            ticket_doc.opening_date = nowdate()
        if not ticket_doc.opening_time:
            ticket_doc.opening_time = now_datetime().time()
        if not ticket_doc.last_customer_reply_on:
            ticket_doc.last_customer_reply_on = now_datetime()

    if ticket_doc.has_value_changed("priority") or ticket_doc.is_new():
        apply_sla_targets(ticket_doc, reset_from_creation=ticket_doc.is_new())


def sync_ticket_state(ticket_doc):
    ticket_doc.status_category = get_status_category(ticket_doc.status)

    old_doc = ticket_doc.get_doc_before_save() if not ticket_doc.is_new() else None
    if old_doc and old_doc.status != ticket_doc.status:
        old_category = get_status_category(old_doc.status)
        new_category = ticket_doc.status_category
        now_dt = now_datetime()

        if new_category == "Paused" and old_category != "Paused":
            ticket_doc.on_hold_since = now_dt

        if old_category == "Paused" and new_category != "Paused" and ticket_doc.on_hold_since:
            hold_diff = max(time_diff_in_seconds(now_dt, ticket_doc.on_hold_since), 0)
            ticket_doc.total_hold_time = _safe_seconds(ticket_doc.total_hold_time) + hold_diff
            ticket_doc.on_hold_since = None
            apply_sla_targets(ticket_doc, reset_from_creation=False)

        if new_category in {"Resolved", "Closed"} and not ticket_doc.resolution_date:
            ticket_doc.resolution_date = now_dt
            if ticket_doc.service_level_agreement_creation:
                elapsed = max(
                    time_diff_in_seconds(now_dt, ticket_doc.service_level_agreement_creation)
                    - _safe_seconds(ticket_doc.total_hold_time),
                    0,
                )
                ticket_doc.resolution_time = elapsed
        elif new_category not in {"Resolved", "Closed"}:
            ticket_doc.resolution_date = None
            ticket_doc.resolution_time = 0

    _sync_agreement_status(ticket_doc)


def create_ticket_activity(ticket_name, action, owner=None):
    if not _doctype_exists("MS Support Ticket Activity"):
        return
    try:
        frappe.get_doc(
            {
                "doctype": "MS Support Ticket Activity",
                "ticket": ticket_name,
                "action": action,
                "owner": owner or frappe.session.user,
            }
        ).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "MS Support Activity Log Failed")


def _ticket_doc(ticket_name):
    if not frappe.db.exists("MS Support Ticket", ticket_name):
        frappe.throw(_("تیکت پیدا نشد."), frappe.DoesNotExistError)
    return frappe.get_doc("MS Support Ticket", ticket_name)


def _customer_can_access_ticket(ticket_doc, user=None):
    target = user or frappe.session.user
    if target == "Guest":
        return False
    if has_management_access(target):
        return True
    if str(ticket_doc.raised_by or "") == target:
        return True

    allowed = get_allowed_customers(target)
    return bool(ticket_doc.customer and ticket_doc.customer in allowed)


def _serialize_communication(row):
    return {
        "name": row.get("name"),
        "creation": row.get("creation"),
        "sender": row.get("sender"),
        "recipients": row.get("recipients"),
        "sent_or_received": row.get("sent_or_received"),
        "content": row.get("content"),
        "subject": row.get("subject"),
    }


def get_ticket_detail(ticket_name, for_management=False):
    ensure_support_runtime_ready()
    ticket_doc = _ticket_doc(ticket_name)
    if for_management:
        require_management_access()
    elif not _customer_can_access_ticket(ticket_doc):
        frappe.throw(_("به این تیکت دسترسی ندارید."), frappe.PermissionError)

    comments = frappe.get_all(
        "MS Support Ticket Comment",
        filters={"reference_ticket": ticket_doc.name},
        fields=["name", "commented_by", "content", "creation", "is_pinned"],
        order_by="creation asc",
        ignore_permissions=True,
    )

    communications = frappe.get_all(
        "Communication",
        filters={"reference_doctype": "MS Support Ticket", "reference_name": ticket_doc.name},
        fields=["name", "creation", "sender", "recipients", "sent_or_received", "content", "subject"],
        order_by="creation asc",
        ignore_permissions=True,
    )

    activities = frappe.get_all(
        "MS Support Ticket Activity",
        filters={"ticket": ticket_doc.name},
        fields=["name", "action", "owner", "creation"],
        order_by="creation desc",
        ignore_permissions=True,
    )

    return {
        "ticket": ticket_doc.as_dict(),
        "comments": comments,
        "communications": [_serialize_communication(row) for row in communications],
        "activities": activities,
    }


def _update_response_metrics(ticket_doc, response_at=None):
    response_at = get_datetime(response_at) if response_at else now_datetime()
    base_dt = (
        get_datetime(ticket_doc.last_customer_reply_on)
        if ticket_doc.last_customer_reply_on
        else get_datetime(ticket_doc.service_level_agreement_creation or ticket_doc.creation)
    )
    elapsed = max(time_diff_in_seconds(response_at, base_dt), 0)

    if not ticket_doc.first_responded_on:
        ticket_doc.first_responded_on = response_at
        ticket_doc.first_response_time = elapsed

    total_response_time = _safe_seconds(ticket_doc.total_response_time) + elapsed
    response_count = cint(ticket_doc.response_count) + 1

    ticket_doc.total_response_time = total_response_time
    ticket_doc.response_count = response_count
    ticket_doc.avg_response_time = total_response_time / max(response_count, 1)
    ticket_doc.last_agent_reply_on = response_at


def _send_ticket_email(ticket_doc, message, recipients=None, cc=None, bcc=None):
    recipients = _resolve_email_recipients(recipients or ticket_doc.raised_by)
    if not recipients:
        return {"sent": False, "reason": "missing_recipient"}
    cc_recipients = _resolve_email_recipients(cc)
    bcc_recipients = _resolve_email_recipients(bcc)

    try:
        frappe.sendmail(
            recipients=recipients,
            cc=cc_recipients,
            bcc=bcc_recipients,
            subject=f"Re: {ticket_doc.subject}",
            message=message,
            reference_doctype="MS Support Ticket",
            reference_name=ticket_doc.name,
            now=True,
        )
        return {"sent": True}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "MS Support Email Send Failed")
        return {"sent": False, "reason": "send_failed"}


def _resolve_email_recipients(raw_value):
    if raw_value is None:
        return []

    values = []
    if isinstance(raw_value, (list, tuple, set)):
        values.extend(raw_value)
    else:
        values.extend(str(raw_value).replace(";", ",").split(","))

    emails = []
    seen = set()
    for value in values:
        token = str(value or "").strip()
        if not token:
            continue

        resolved = ""
        if frappe.db.exists("User", token):
            resolved = str(frappe.db.get_value("User", token, "email") or "").strip()
        else:
            parsed = parseaddr(token)[1] if token else ""
            resolved = parsed or token

        if not resolved or "@" not in resolved:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        emails.append(resolved)

    return emails


def add_agent_reply(ticket_name, message, status_after_reply=None, to=None, cc=None, bcc=None, send_email=True):
    ensure_support_runtime_ready()
    require_management_access()
    ticket_doc = _ticket_doc(ticket_name)

    content = frappe.utils.sanitize_html(message or "").strip()
    if not content:
        frappe.throw(_("متن پاسخ خالی است."), frappe.ValidationError)

    resolved_recipients = _resolve_email_recipients(to or ticket_doc.raised_by)
    recipients_display = ", ".join(resolved_recipients)

    comm = frappe.get_doc(
        {
            "doctype": "Communication",
            "communication_type": "Communication",
            "communication_medium": "Email" if send_email else "",
            "sent_or_received": "Sent",
            "reference_doctype": "MS Support Ticket",
            "reference_name": ticket_doc.name,
            "subject": f"Re: {ticket_doc.subject}",
            "content": content,
            "sender": frappe.session.user,
            "recipients": recipients_display,
            "cc": ", ".join(_resolve_email_recipients(cc)),
            "bcc": ", ".join(_resolve_email_recipients(bcc)),
            "status": "Linked",
            "email_status": "Open",
        }
    ).insert(ignore_permissions=True)
    ticket_doc.reload()

    _update_response_metrics(ticket_doc, response_at=comm.creation)

    if status_after_reply:
        if not frappe.db.exists("MS Support Ticket Status", status_after_reply):
            frappe.throw(_("وضعیت انتخاب‌شده معتبر نیست."), frappe.ValidationError)
        ticket_doc.status = status_after_reply

    current_category = get_status_category(ticket_doc.status)
    if current_category == "Paused":
        reopen = _reopen_status()
        if reopen:
            ticket_doc.status = reopen

    ticket_doc.save(ignore_permissions=True)
    create_ticket_activity(ticket_doc.name, "agent_replied")
    run_support_automation(ticket_doc, trigger_event="Agent Reply", context={"communication": comm.name})

    email_result = {"sent": False, "reason": "disabled"}
    if send_email:
        email_result = _send_ticket_email(ticket_doc, content, recipients=resolved_recipients, cc=cc, bcc=bcc)

    notify_users(
        [ticket_doc.raised_by],
        event_key="ticket_agent_reply",
        title=f"پاسخ جدید روی تیکت {ticket_doc.name}",
        body=frappe.utils.strip_html(content)[:240],
        ticket_name=ticket_doc.name,
    )

    frappe.db.commit()
    return {
        "ok": True,
        "communication": comm.name,
        "ticket": ticket_doc.name,
        "email": email_result,
    }


def add_customer_reply(ticket_name, message, user=None):
    ensure_support_runtime_ready()
    target_user = user or require_authenticated_user()
    ticket_doc = _ticket_doc(ticket_name)

    if not _customer_can_access_ticket(ticket_doc, user=target_user):
        frappe.throw(_("به این تیکت دسترسی ندارید."), frappe.PermissionError)

    content = frappe.utils.sanitize_html(message or "").strip()
    if not content:
        frappe.throw(_("متن پاسخ خالی است."), frappe.ValidationError)

    comm = frappe.get_doc(
        {
            "doctype": "Communication",
            "communication_type": "Communication",
            "communication_medium": "",
            "sent_or_received": "Received",
            "reference_doctype": "MS Support Ticket",
            "reference_name": ticket_doc.name,
            "subject": f"Re: {ticket_doc.subject}",
            "content": content,
            "sender": target_user,
            "recipients": "",
            "status": "Linked",
            "email_status": "Open",
        }
    ).insert(ignore_permissions=True)
    ticket_doc.reload()

    ticket_doc.last_customer_reply_on = comm.creation
    reopen = _reopen_status()
    if reopen:
        ticket_doc.status = reopen
    ticket_doc.save(ignore_permissions=True)
    create_ticket_activity(ticket_doc.name, "customer_replied", owner=target_user)
    run_support_automation(ticket_doc, trigger_event="Customer Reply", context={"communication": comm.name})

    notify_users(
        support_agent_users(team=ticket_doc.team),
        event_key="ticket_customer_reply",
        title=f"پاسخ مشتری روی {ticket_doc.name}",
        body=frappe.utils.strip_html(content)[:240],
        ticket_name=ticket_doc.name,
    )

    frappe.db.commit()
    return {"ok": True, "communication": comm.name, "ticket": ticket_doc.name}


def create_portal_ticket(subject, description, customer=None, item_code=None, source_page=None):
    ensure_support_runtime_ready()
    user = require_authenticated_user()
    scoped_customers, _ = resolve_customer_scope(customer=customer, user=user)

    chosen_customer = scoped_customers[0] if scoped_customers else ""
    if not chosen_customer:
        frappe.throw(_("برای کاربر جاری مشتری مجاز تعریف نشده است."), frappe.PermissionError)

    subject = (subject or "").strip()
    description = frappe.utils.sanitize_html(description or "").strip()
    if len(subject) < 3:
        frappe.throw(_("عنوان تیکت باید حداقل ۳ کاراکتر باشد."), frappe.ValidationError)
    if len(description) < 3:
        frappe.throw(_("توضیحات تیکت باید حداقل ۳ کاراکتر باشد."), frappe.ValidationError)

    doc = frappe.get_doc(
        {
            "doctype": "MS Support Ticket",
            "subject": subject,
            "description": description,
            "raised_by": user,
            "customer": chosen_customer,
            "related_item_code": item_code or "",
            "source_channel": "mysite_dashboard",
            "source_page": source_page or "/dashboard",
            "via_customer_portal": 1,
        }
    )
    doc.insert(ignore_permissions=True)
    create_ticket_activity(doc.name, "ticket_created", owner=user)
    run_support_automation(doc, trigger_event="Ticket Created", context={"source": "portal"})

    notify_users(
        support_agent_users(team=doc.team),
        event_key="ticket_created",
        title=f"تیکت جدید: {doc.subject}",
        body=f"{doc.name} توسط {user}",
        ticket_name=doc.name,
    )
    if doc.assigned_to:
        notify_users(
            [doc.assigned_to],
            event_key="ticket_assigned",
            title=f"تیکت به شما اختصاص یافت: {doc.name}",
            body=doc.subject,
            ticket_name=doc.name,
        )

    frappe.db.commit()
    return {"ok": True, "ticket": doc.name}


def list_tickets_for_customer(customer=None, page=1, page_size=10, status=None):
    ensure_support_runtime_ready()
    user = require_authenticated_user()
    scoped_customers, _ = resolve_customer_scope(customer=customer, user=user)

    page = max(cint(page), 1)
    page_size = min(max(cint(page_size), 1), 50)
    start = (page - 1) * page_size

    filters = {}
    if status:
        filters["status"] = status

    or_filters = [["raised_by", "=", user]]
    if customer and scoped_customers:
        filters["customer"] = scoped_customers[0]
    elif scoped_customers:
        or_filters.append(["customer", "in", scoped_customers])

    total = len(
        frappe.get_all(
            "MS Support Ticket",
            filters=filters,
            or_filters=or_filters,
            pluck="name",
            ignore_permissions=True,
        )
    )

    rows = frappe.get_all(
        "MS Support Ticket",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "subject",
            "status",
            "status_category",
            "priority",
            "ticket_type",
            "team",
            "assigned_to",
            "agreement_status",
            "first_response_time",
            "avg_response_time",
            "response_by",
            "resolution_by",
            "creation",
            "modified",
        ],
        order_by="modified desc",
        start=start,
        page_length=page_size,
        ignore_permissions=True,
    )

    total_pages = max(int((total + page_size - 1) / page_size), 1)
    return {
        "items": rows,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def list_tickets_for_management(page=1, page_size=20, status=None, priority=None, search=None, customer=None):
    ensure_support_runtime_ready()
    require_management_access()
    page = max(cint(page), 1)
    page_size = min(max(cint(page_size), 1), 100)
    start = (page - 1) * page_size

    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if customer:
        filters["customer"] = customer

    or_filters = []
    search_value = (search or "").strip()
    if search_value:
        like_value = f"%{search_value}%"
        or_filters = [
            ["name", "like", like_value],
            ["subject", "like", like_value],
            ["raised_by", "like", like_value],
            ["customer", "like", like_value],
        ]

    total = len(
        frappe.get_all(
            "MS Support Ticket",
            filters=filters,
            or_filters=or_filters,
            pluck="name",
            ignore_permissions=True,
        )
    )

    rows = frappe.get_all(
        "MS Support Ticket",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "subject",
            "status",
            "status_category",
            "priority",
            "ticket_type",
            "team",
            "assigned_to",
            "customer",
            "raised_by",
            "agreement_status",
            "first_response_time",
            "avg_response_time",
            "response_by",
            "resolution_by",
            "creation",
            "modified",
        ],
        order_by="modified desc",
        start=start,
        page_length=page_size,
        ignore_permissions=True,
    )

    total_pages = max(int((total + page_size - 1) / page_size), 1)
    return {
        "items": rows,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def management_dashboard_payload(from_date=None, to_date=None):
    ensure_support_runtime_ready()
    require_management_access()

    from_date = str(getdate(from_date) if from_date else add_to_date(nowdate(), days=-29))
    to_date = str(getdate(to_date) if to_date else getdate(nowdate()))

    rows = frappe.get_all(
        "MS Support Ticket",
        filters={"creation": ["between", [f"{from_date} 00:00:00", f"{to_date} 23:59:59"]]},
        fields=[
            "name",
            "status",
            "status_category",
            "agreement_status",
            "first_response_time",
            "avg_response_time",
            "creation",
        ],
        order_by="creation asc",
        limit_page_length=0,
        ignore_permissions=True,
    )

    counts = defaultdict(int)
    status_counts = defaultdict(int)
    daily = defaultdict(int)
    first_response_values = []
    avg_response_values = []

    for row in rows:
        status = str(row.get("status") or "")
        agreement = str(row.get("agreement_status") or "")
        status_counts[status] += 1
        counts["total"] += 1

        category = str(row.get("status_category") or "")
        if category == "Open":
            counts["open"] += 1
        elif category == "Resolved":
            counts["resolved"] += 1
        elif category == "Closed":
            counts["closed"] += 1

        if agreement == "Failed":
            counts["sla_failed"] += 1
        if agreement == "Fulfilled":
            counts["sla_fulfilled"] += 1

        frt = _safe_seconds(row.get("first_response_time"))
        art = _safe_seconds(row.get("avg_response_time"))
        if frt > 0:
            first_response_values.append(frt)
        if art > 0:
            avg_response_values.append(art)

        day = str(row.get("creation") or "").split(" ")[0]
        if day:
            daily[day] += 1

    avg_first_response = sum(first_response_values) / len(first_response_values) if first_response_values else 0
    avg_response = sum(avg_response_values) / len(avg_response_values) if avg_response_values else 0

    daily_rows = [{"date": day, "count": count} for day, count in sorted(daily.items())]

    return {
        "range": {"from_date": from_date, "to_date": to_date},
        "counts": {
            "total": counts["total"],
            "open": counts["open"],
            "resolved": counts["resolved"],
            "closed": counts["closed"],
            "sla_failed": counts["sla_failed"],
            "sla_fulfilled": counts["sla_fulfilled"],
        },
        "status_counts": dict(status_counts),
        "averages": {
            "first_response_time": round(avg_first_response, 2),
            "avg_response_time": round(avg_response, 2),
        },
        "daily": daily_rows,
    }


def ticket_summary_rows(from_date, to_date, based_on="status"):
    ensure_support_runtime_ready()
    filters = {"creation": ["between", [f"{from_date} 00:00:00", f"{to_date} 23:59:59"]]}
    fields = [
        "name",
        "status",
        "priority",
        "ticket_type",
        "customer",
        "raised_by",
        "agreement_status",
        "first_response_time",
        "avg_response_time",
        "total_hold_time",
        "resolution_time",
        "user_resolution_time",
    ]

    rows = frappe.get_all("MS Support Ticket", filters=filters, fields=fields, limit_page_length=0, ignore_permissions=True)
    grouped = defaultdict(lambda: {"total": 0, "failed": 0, "fulfilled": 0, "first_response": [], "avg_response": []})

    for row in rows:
        key = str(row.get(based_on) or "مشخص نشده")
        grouped[key]["total"] += 1
        agreement = str(row.get("agreement_status") or "")
        if agreement == "Failed":
            grouped[key]["failed"] += 1
        if agreement == "Fulfilled":
            grouped[key]["fulfilled"] += 1

        frt = _safe_seconds(row.get("first_response_time"))
        art = _safe_seconds(row.get("avg_response_time"))
        if frt > 0:
            grouped[key]["first_response"].append(frt)
        if art > 0:
            grouped[key]["avg_response"].append(art)

    result = []
    for key, payload in grouped.items():
        avg_frt = sum(payload["first_response"]) / len(payload["first_response"]) if payload["first_response"] else 0
        avg_art = sum(payload["avg_response"]) / len(payload["avg_response"]) if payload["avg_response"] else 0
        result.append(
            {
                "group": key,
                "total_tickets": payload["total"],
                "sla_failed": payload["failed"],
                "sla_fulfilled": payload["fulfilled"],
                "avg_first_response_time": round(avg_frt, 2),
                "avg_response_time": round(avg_art, 2),
            }
        )

    result.sort(key=lambda row: (-row["total_tickets"], row["group"]))
    return result


def first_response_daily_rows(from_date, to_date):
    ensure_support_runtime_ready()
    rows = frappe.db.sql(
        """
        SELECT
            DATE(creation) AS creation_date,
            AVG(first_response_time) AS first_response_time
        FROM `tabMS Support Ticket`
        WHERE creation >= %(from_dt)s
          AND creation <= %(to_dt)s
          AND first_response_time > 0
        GROUP BY DATE(creation)
        ORDER BY creation_date DESC
        """,
        {
            "from_dt": f"{from_date} 00:00:00",
            "to_dt": f"{to_date} 23:59:59",
        },
        as_dict=True,
    )
    return rows


def analytics_timeseries_rows(from_date, to_date, based_on="status", range_key="Monthly"):
    ensure_support_runtime_ready()
    filters = {"creation": ["between", [f"{from_date} 00:00:00", f"{to_date} 23:59:59"]]}
    fields = ["creation", based_on]
    rows = frappe.get_all("MS Support Ticket", filters=filters, fields=fields, limit_page_length=0, ignore_permissions=True)

    from collections import OrderedDict
    from datetime import timedelta

    start = getdate(from_date)
    end = getdate(to_date)

    if range_key == "Weekly":
        bucket_days = 7
    elif range_key == "Quarterly":
        bucket_days = 90
    elif range_key == "Yearly":
        bucket_days = 365
    else:
        bucket_days = 30

    buckets = OrderedDict()
    current = start
    while current <= end:
        bucket_end = min(current + timedelta(days=bucket_days - 1), end)
        label = f"{current} تا {bucket_end}"
        buckets[label] = defaultdict(int)
        current = bucket_end + timedelta(days=1)

    for row in rows:
        created = getdate(str(row.get("creation") or "").split(" ")[0])
        entity = str(row.get(based_on) or "مشخص نشده")
        for label in buckets:
            start_str, end_str = label.split(" تا ")
            bucket_start = getdate(start_str)
            bucket_end = getdate(end_str)
            if bucket_start <= created <= bucket_end:
                buckets[label][entity] += 1
                break

    entities = sorted({entity for payload in buckets.values() for entity in payload.keys()})
    series = []
    for entity in entities:
        data = []
        for label, payload in buckets.items():
            data.append({"period": label, "count": payload.get(entity, 0)})
        series.append({"entity": entity, "data": data})

    return {
        "labels": list(buckets.keys()),
        "series": series,
    }


def _enabled_users(users):
    valid = []
    seen = set()
    for user in users or []:
        uid = str(user or "").strip()
        if not uid or uid in seen:
            continue
        if not frappe.db.exists("User", uid):
            continue
        if cint(frappe.db.get_value("User", uid, "enabled") or 0) != 1:
            continue
        seen.add(uid)
        valid.append(uid)
    return valid


def support_agent_users(team=None):
    users = set()

    if _doctype_exists("MS Support Team Member"):
        filters = {"parenttype": "MS Support Team"}
        if team:
            filters["parent"] = team
        rows = frappe.get_all(
            "MS Support Team Member",
            filters=filters,
            fields=["user"],
            ignore_permissions=True,
            limit_page_length=0,
        )
        for row in rows:
            user = str(row.get("user") or "").strip()
            if user:
                users.add(user)

    role_rows = frappe.get_all(
        "Has Role",
        filters={"role": ["in", sorted(SUPPORT_MANAGER_ROLES)]},
        fields=["parent"],
        ignore_permissions=True,
        limit_page_length=0,
    )
    for row in role_rows:
        user = str(row.get("parent") or "").strip()
        if user:
            users.add(user)

    return _enabled_users(sorted(users))


def _notification_pref_defaults(user):
    return {
        "user": user,
        "enable_in_app": 1,
        "enable_sound": 1,
        "notify_ticket_created": 1,
        "notify_ticket_customer_reply": 1,
        "notify_ticket_agent_reply": 1,
        "notify_ticket_status_changed": 1,
        "notify_ticket_assigned": 1,
        "notify_chat_message": 1,
    }


def get_notification_preferences(user=None, ensure_doc=True):
    target_user = user or frappe.session.user
    if not target_user or target_user == "Guest":
        frappe.throw(_("برای تنظیم اعلان‌ها باید وارد شوید."), frappe.PermissionError)

    if not _doctype_exists("MS Support Notification Preference"):
        defaults = _notification_pref_defaults(target_user)
        defaults["source"] = "default"
        return defaults

    doc_name = frappe.db.get_value("MS Support Notification Preference", {"user": target_user}, "name")
    if doc_name:
        doc = frappe.get_doc("MS Support Notification Preference", doc_name)
        payload = doc.as_dict()
        payload["source"] = "doctype"
        return payload

    defaults = _notification_pref_defaults(target_user)
    if not ensure_doc:
        defaults["source"] = "default"
        return defaults

    doc = frappe.get_doc({"doctype": "MS Support Notification Preference", **defaults})
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


def set_notification_preferences(payload, user=None):
    target_user = user or frappe.session.user
    if not target_user or target_user == "Guest":
        frappe.throw(_("برای تنظیم اعلان‌ها باید وارد شوید."), frappe.PermissionError)

    if not _doctype_exists("MS Support Notification Preference"):
        return _notification_pref_defaults(target_user)

    existing = frappe.db.get_value("MS Support Notification Preference", {"user": target_user}, "name")
    if existing:
        doc = frappe.get_doc("MS Support Notification Preference", existing)
    else:
        doc = frappe.new_doc("MS Support Notification Preference")
        doc.user = target_user

    for fieldname in [
        "enable_in_app",
        "enable_sound",
        "notify_ticket_created",
        "notify_ticket_customer_reply",
        "notify_ticket_agent_reply",
        "notify_ticket_status_changed",
        "notify_ticket_assigned",
        "notify_chat_message",
    ]:
        if fieldname in payload:
            doc.set(fieldname, 1 if cint(payload.get(fieldname)) else 0)

    doc.save(ignore_permissions=True)
    return doc.as_dict()


def _notification_event_field(event_key):
    mapping = {
        "ticket_created": "notify_ticket_created",
        "ticket_customer_reply": "notify_ticket_customer_reply",
        "ticket_agent_reply": "notify_ticket_agent_reply",
        "ticket_status_changed": "notify_ticket_status_changed",
        "ticket_assigned": "notify_ticket_assigned",
        "chat_message": "notify_chat_message",
    }
    return mapping.get(event_key)


def _can_receive_event(user, event_key):
    prefs = get_notification_preferences(user=user, ensure_doc=False)
    if cint(prefs.get("enable_in_app")) != 1:
        return False, False

    fieldname = _notification_event_field(event_key)
    if fieldname and cint(prefs.get(fieldname, 1)) != 1:
        return False, False

    return True, cint(prefs.get("enable_sound", 1)) == 1


def notify_users(users, event_key, title, body, ticket_name=None, route=None, payload=None):
    if not users:
        return

    reference_route = route or (f"/management-support?ticket={ticket_name}" if ticket_name else "/management-support")
    for user in _enabled_users(users):
        allowed, play_sound = _can_receive_event(user, event_key)
        if not allowed:
            continue
        try:
            if frappe.db.table_exists("Notification Log"):
                frappe.get_doc(
                    {
                        "doctype": "Notification Log",
                        "subject": title,
                        "for_user": user,
                        "type": "Alert",
                        "email_content": body,
                        "document_type": "MS Support Ticket" if ticket_name else "",
                        "document_name": ticket_name or "",
                        "from_user": frappe.session.user if frappe.session.user != "Guest" else "Administrator",
                        "link": reference_route,
                    }
                ).insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "MS Support Notification Log Failed")

        try:
            frappe.publish_realtime(
                "mysite_support_notification",
                {
                    "event": event_key,
                    "title": title,
                    "body": body,
                    "ticket": ticket_name,
                    "route": reference_route,
                    "play_sound": play_sound,
                    "payload": payload or {},
                },
                user=user,
                after_commit=True,
            )
        except Exception:
            pass


def mark_support_notifications_seen(user=None):
    target_user = user or frappe.session.user
    if not target_user or target_user == "Guest":
        frappe.throw(_("ابتدا وارد حساب کاربری شوید."), frappe.PermissionError)
    if not frappe.db.table_exists("Notification Log"):
        return {"ok": True, "updated": 0}

    pending = frappe.db.sql(
        """
        SELECT COUNT(*) AS total
        FROM `tabNotification Log`
        WHERE for_user = %(user)s
          AND ifnull(`read`, 0) = 0
          AND (
            document_type = 'MS Support Ticket'
            OR subject LIKE '%%تیکت%%'
            OR subject LIKE '%%پشتیبانی%%'
          )
        """,
        {"user": target_user},
        as_dict=True,
    )
    updated = cint((pending or [{}])[0].get("total") or 0)

    frappe.db.sql(
        """
        UPDATE `tabNotification Log`
        SET `read` = 1
        WHERE for_user = %(user)s
          AND ifnull(`read`, 0) = 0
          AND (
            document_type = 'MS Support Ticket'
            OR subject LIKE '%%تیکت%%'
            OR subject LIKE '%%پشتیبانی%%'
          )
        """,
        {"user": target_user},
    )
    frappe.db.commit()
    return {"ok": True, "updated": updated}


def _parse_time_value(value):
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(text, fmt).time()
        except Exception:
            continue
    return None


def _weekday_token(dt_value):
    return dt_value.strftime("%a").lower()


def _normalize_weekdays(value):
    text = str(value or "").strip()
    if not text:
        return {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
    result = set()
    tokens = [token.strip().lower() for token in text.replace("|", ",").split(",") if token.strip()]
    mapping = {
        "monday": "mon",
        "mon": "mon",
        "tuesday": "tue",
        "tue": "tue",
        "wednesday": "wed",
        "wed": "wed",
        "thursday": "thu",
        "thu": "thu",
        "friday": "fri",
        "fri": "fri",
        "saturday": "sat",
        "sat": "sat",
        "sunday": "sun",
        "sun": "sun",
    }
    for token in tokens:
        normalized = mapping.get(token)
        if normalized:
            result.add(normalized)
    return result or {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


def _is_time_in_window(now_time, start_time, end_time):
    if not start_time or not end_time:
        return True
    if start_time <= end_time:
        return start_time <= now_time <= end_time
    return now_time >= start_time or now_time <= end_time


def _shift_member_users(shift_doc):
    users = []
    if shift_doc.get("members"):
        users.extend([row.user for row in shift_doc.members if row.user and cint(row.get("enabled", 1)) == 1])
    elif shift_doc.get("team"):
        users.extend(_team_members(shift_doc.team))
    return _enabled_users(users)


def _get_shift_exception_window(shift_doc, target_date):
    for row in shift_doc.get("exceptions") or []:
        if not row.get("date"):
            continue
        if getdate(row.date) != target_date:
            continue
        if cint(row.get("is_off_day")) == 1:
            return "off", None, None
        return "custom", _parse_time_value(row.get("start_time")), _parse_time_value(row.get("end_time"))
    return "none", None, None


def _is_shift_active(shift_doc, now_dt=None):
    current_dt = now_dt or now_datetime()
    current_date = getdate(current_dt.date())
    current_time = current_dt.time()

    exception_mode, ex_start, ex_end = _get_shift_exception_window(shift_doc, current_date)
    if exception_mode == "off":
        return False
    if exception_mode == "custom":
        return _is_time_in_window(current_time, ex_start, ex_end)

    weekdays = _normalize_weekdays(shift_doc.get("weekdays"))
    if _weekday_token(current_dt) not in weekdays:
        return False

    start_time = _parse_time_value(shift_doc.get("start_time"))
    end_time = _parse_time_value(shift_doc.get("end_time"))
    return _is_time_in_window(current_time, start_time, end_time)


def get_online_agents(team=None):
    if not _doctype_exists("MS Support Shift"):
        return support_agent_users(team=team)

    filters = {"enabled": 1}
    if team:
        filters["team"] = team
    shifts = frappe.get_all(
        "MS Support Shift",
        filters=filters,
        fields=["name"],
        ignore_permissions=True,
        limit_page_length=0,
    )

    if not shifts:
        return support_agent_users(team=team)

    users = []
    for row in shifts:
        shift_doc = frappe.get_doc("MS Support Shift", row.name)
        if not _is_shift_active(shift_doc):
            continue
        users.extend(_shift_member_users(shift_doc))
    return _enabled_users(users)


def get_shift_status(team=None):
    online_agents = get_online_agents(team=team)
    active_shifts = []
    if _doctype_exists("MS Support Shift"):
        filters = {"enabled": 1}
        if team:
            filters["team"] = team
        rows = frappe.get_all(
            "MS Support Shift",
            filters=filters,
            fields=["name", "shift_name", "team"],
            order_by="modified desc",
            ignore_permissions=True,
            limit_page_length=0,
        )
        for row in rows:
            shift_doc = frappe.get_doc("MS Support Shift", row.name)
            if _is_shift_active(shift_doc):
                active_shifts.append(
                    {
                        "name": row.get("name"),
                        "shift_name": row.get("shift_name"),
                        "team": row.get("team"),
                    }
                )
    return {
        "online": bool(online_agents),
        "online_agents": online_agents,
        "active_shifts": active_shifts,
        "team": team or "",
    }


def set_shift_assignment(ticket_name, agent_user=None, team=None):
    ensure_support_runtime_ready()
    require_management_access()
    ticket_doc = _ticket_doc(ticket_name)

    if team and not frappe.db.exists("MS Support Team", team):
        frappe.throw(_("تیم پشتیبانی انتخاب‌شده معتبر نیست."), frappe.ValidationError)

    selected_team = team or ticket_doc.team or _default_team() or ""
    selected_agent = str(agent_user or "").strip()

    if selected_agent:
        if not frappe.db.exists("User", selected_agent):
            frappe.throw(_("کاربر پشتیبان انتخاب‌شده معتبر نیست."), frappe.ValidationError)
    else:
        online = get_online_agents(team=selected_team)
        selected_agent = online[0] if online else ""

    if selected_team:
        ticket_doc.team = selected_team
    ticket_doc.assigned_to = selected_agent
    ticket_doc.auto_assigned = 0
    ticket_doc.save(ignore_permissions=True)
    create_ticket_activity(ticket_doc.name, f"تخصیص به {selected_agent or 'صف'}")

    if selected_agent:
        notify_users(
            [selected_agent],
            event_key="ticket_assigned",
            title=f"تیکت {ticket_doc.name} به شما تخصیص داده شد",
            body=ticket_doc.subject,
            ticket_name=ticket_doc.name,
        )

    frappe.db.commit()
    return {
        "ok": True,
        "ticket": ticket_doc.name,
        "team": ticket_doc.team,
        "assigned_to": ticket_doc.assigned_to,
    }


def _rule_conditions_match(rule_doc, ticket_doc, context=None):
    conditions = rule_doc.get("conditions") or []
    if not conditions:
        return True
    context = context or {}

    for row in conditions:
        condition_type = str(row.get("condition_type") or "").strip()
        fieldname = str(row.get("fieldname") or "").strip()
        value = str(row.get("value") or "").strip()
        numeric_value = flt(row.get("numeric_value") or 0)

        if condition_type == "Field Equals":
            if not fieldname:
                return False
            if str(ticket_doc.get(fieldname) or "") != value:
                return False
        elif condition_type == "Field Contains":
            if not fieldname:
                return False
            if value.lower() not in str(ticket_doc.get(fieldname) or "").lower():
                return False
        elif condition_type == "Ticket Age Minutes >=":
            age_minutes = max(time_diff_in_seconds(now_datetime(), get_datetime(ticket_doc.creation)) / 60, 0)
            if age_minutes < numeric_value:
                return False
        elif condition_type == "Status Category Equals":
            if str(ticket_doc.get("status_category") or "") != value:
                return False
        elif condition_type == "Agreement Status Equals":
            if str(ticket_doc.get("agreement_status") or "") != value:
                return False
        elif condition_type == "Trigger Event Equals":
            if str(context.get("trigger_event") or "") != value:
                return False
        else:
            return False
    return True


def _perform_rule_action(ticket_doc, row):
    action_type = str(row.get("action_type") or "").strip()
    value = str(row.get("value") or "").strip()
    extra = str(row.get("extra_json") or "").strip()
    changed = False

    if action_type == "Set Status" and value and frappe.db.exists("MS Support Ticket Status", value):
        if ticket_doc.status != value:
            ticket_doc.status = value
            changed = True
    elif action_type == "Set Priority" and value and frappe.db.exists("MS Support Ticket Priority", value):
        if ticket_doc.priority != value:
            ticket_doc.priority = value
            changed = True
    elif action_type == "Set Team" and value and frappe.db.exists("MS Support Team", value):
        if ticket_doc.team != value:
            ticket_doc.team = value
            changed = True
        if not ticket_doc.assigned_to and _auto_assign_enabled():
            member = _pick_round_robin_member(value)
            if member and ticket_doc.assigned_to != member:
                ticket_doc.assigned_to = member
                ticket_doc.auto_assigned = 1
                changed = True
    elif action_type == "Assign Agent" and value and frappe.db.exists("User", value):
        if ticket_doc.assigned_to != value:
            ticket_doc.assigned_to = value
            ticket_doc.auto_assigned = 0
            changed = True
    elif action_type == "Add Activity":
        create_ticket_activity(ticket_doc.name, value or "automation_activity")
    elif action_type == "Escalate":
        top_priority = frappe.db.get_value(
            "MS Support Ticket Priority",
            {"enabled": 1},
            "name",
            order_by="weight asc",
        )
        if top_priority and ticket_doc.priority != top_priority:
            ticket_doc.priority = top_priority
            changed = True
        create_ticket_activity(ticket_doc.name, f"automation_escalate {extra}".strip())

    return changed


def run_support_automation(ticket_doc, trigger_event, context=None):
    if not _doctype_exists("MS Support Automation Rule"):
        return []

    rows = frappe.get_all(
        "MS Support Automation Rule",
        filters={"enabled": 1},
        fields=["name"],
        order_by="priority asc, modified asc",
        ignore_permissions=True,
        limit_page_length=0,
    )
    if not rows:
        return []

    context_payload = dict(context or {})
    context_payload["trigger_event"] = trigger_event
    applied = []

    for row in rows:
        rule_doc = frappe.get_doc("MS Support Automation Rule", row.name)
        trigger = str(rule_doc.get("trigger_event") or "").strip()
        if trigger and trigger != trigger_event:
            continue
        if not _rule_conditions_match(rule_doc, ticket_doc, context=context_payload):
            continue

        changed = False
        for action_row in rule_doc.get("actions") or []:
            changed = _perform_rule_action(ticket_doc, action_row) or changed

        if changed:
            ticket_doc.save(ignore_permissions=True)
        create_ticket_activity(ticket_doc.name, f"automation_rule {rule_doc.name}")
        applied.append(rule_doc.name)
        if cint(rule_doc.get("stop_after_first_match")) == 1:
            break

    return applied


def list_macros():
    if not _doctype_exists("MS Support Macro"):
        return []
    return frappe.get_all(
        "MS Support Macro",
        filters={"enabled": 1},
        fields=["name", "macro_name", "category", "content", "default_status", "send_email"],
        order_by="modified desc",
        ignore_permissions=True,
        limit_page_length=0,
    )


def apply_macro(ticket_name, macro_name, notify=True):
    require_management_access()
    if not _doctype_exists("MS Support Macro"):
        frappe.throw(_("ماکروی پشتیبانی فعال نیست."), frappe.ValidationError)
    if not frappe.db.exists("MS Support Macro", macro_name):
        frappe.throw(_("ماکرو پیدا نشد."), frappe.DoesNotExistError)

    macro = frappe.get_doc("MS Support Macro", macro_name)
    return add_agent_reply(
        ticket_name=ticket_name,
        message=macro.content,
        status_after_reply=macro.default_status or None,
        send_email=bool(cint(notify)) if notify is not None else bool(cint(macro.send_email)),
    )


def _raven_runtime_ready():
    required = ["Raven Channel", "Raven Message", "Raven Channel Member"]
    return all(_doctype_exists(doctype) and frappe.db.table_exists(doctype) for doctype in required)


def _resolve_chat_link(ticket_name=None, channel_id=None, customer_user=None):
    if not _doctype_exists("MS Support Chat Link"):
        return None

    filters = {}
    if channel_id:
        filters["raven_channel"] = channel_id
    if ticket_name:
        filters["ticket"] = ticket_name
    if customer_user:
        filters["customer_user"] = customer_user
    if not filters:
        return None

    name = frappe.db.get_value("MS Support Chat Link", filters, "name", order_by="modified desc")
    if not name:
        return None
    return frappe.get_doc("MS Support Chat Link", name)


def _ensure_chat_link(ticket_doc, channel_id, customer_user, agent_user=None, source_page=None):
    existing = _resolve_chat_link(
        ticket_name=ticket_doc.name,
        channel_id=channel_id,
        customer_user=customer_user,
    )
    if existing:
        return existing

    if not _doctype_exists("MS Support Chat Link"):
        return None

    doc = frappe.get_doc(
        {
            "doctype": "MS Support Chat Link",
            "ticket": ticket_doc.name,
            "raven_channel": channel_id,
            "customer_user": customer_user,
            "agent_user": agent_user or "",
            "status": "Open",
            "opened_on": now_datetime(),
            "source_page": source_page or "",
        }
    )
    doc.insert(ignore_permissions=True)
    return doc


def _update_chat_link_activity(chat_link, message_text=None, message_user=None):
    if not chat_link:
        return
    chat_link.last_message = frappe.utils.strip_html(str(message_text or ""))[:280]
    chat_link.last_message_by = message_user or frappe.session.user
    chat_link.last_message_at = now_datetime()
    chat_link.save(ignore_permissions=True)


def _log_chat_to_ticket(ticket_doc, channel_id, message, owner=None):
    text = frappe.utils.sanitize_html(message or "").strip()
    if not text:
        return None
    sent_or_received = "Received"
    sender = owner or frappe.session.user
    if sender != ticket_doc.raised_by:
        sent_or_received = "Sent"
    comm = frappe.get_doc(
        {
            "doctype": "Communication",
            "communication_type": "Communication",
            "communication_medium": "Chat",
            "sent_or_received": sent_or_received,
            "reference_doctype": "MS Support Ticket",
            "reference_name": ticket_doc.name,
            "subject": f"Chat: {ticket_doc.subject}",
            "content": text,
            "sender": sender,
            "recipients": "",
            "status": "Linked",
            "email_status": "Open",
        }
    ).insert(ignore_permissions=True)
    create_ticket_activity(ticket_doc.name, f"chat_message {channel_id}", owner=sender)
    return comm


def _send_raven_message(channel_id, text):
    from raven.api.raven_message import send_message

    clean_text = frappe.utils.sanitize_html(text or "").strip()
    if not clean_text:
        frappe.throw(_("متن پیام خالی است."), frappe.ValidationError)
    return send_message(channel_id=channel_id, text=clean_text)


def open_portal_support_chat(customer=None, ticket_name=None, subject=None, initial_message=None, source_page=None):
    ensure_support_runtime_ready(include_phase2=False)
    user = require_authenticated_user()

    if ticket_name:
        ticket_doc = _ticket_doc(ticket_name)
        if not _customer_can_access_ticket(ticket_doc, user=user):
            frappe.throw(_("به این تیکت دسترسی ندارید."), frappe.PermissionError)
    else:
        initial_text = str(initial_message or "").strip()
        created = create_portal_ticket(
            subject=subject or _("درخواست گفتگوی پشتیبانی"),
            description=initial_text or _("کاربر درخواست گفتگوی آنلاین ثبت کرد."),
            customer=customer,
            source_page=source_page or "/dashboard",
        )
        ticket_doc = _ticket_doc(created.get("ticket"))
        ticket_name = ticket_doc.name

    shift = get_shift_status(team=ticket_doc.team or None)
    if not shift.get("online"):
        if initial_message:
            add_customer_reply(ticket_doc.name, initial_message, user=user)
        return {
            "ok": True,
            "online": False,
            "ticket": ticket_doc.name,
            "message": _("تیم پشتیبانی آنلاین نیست. پیام شما به‌عنوان تیکت ثبت شد."),
        }

    if not _raven_runtime_ready():
        if initial_message:
            add_customer_reply(ticket_doc.name, initial_message, user=user)
        return {
            "ok": True,
            "online": False,
            "ticket": ticket_doc.name,
            "message": _("چت زنده در حال حاضر در دسترس نیست. پیام شما به‌عنوان تیکت ثبت شد."),
        }

    preferred_agent = ticket_doc.assigned_to if ticket_doc.assigned_to in shift.get("online_agents", []) else ""
    agent = preferred_agent or (shift.get("online_agents") or [""])[0]
    if not agent:
        return {
            "ok": True,
            "online": False,
            "ticket": ticket_doc.name,
            "message": _("عامل آنلاین در دسترس نیست. لطفاً از طریق تیکت ادامه دهید."),
        }

    from raven.api.raven_channel import create_direct_message_channel

    channel_id = create_direct_message_channel(user_id=agent)
    chat_link = _ensure_chat_link(
        ticket_doc=ticket_doc,
        channel_id=channel_id,
        customer_user=user,
        agent_user=agent,
        source_page=source_page,
    )
    if not ticket_doc.assigned_to:
        ticket_doc.assigned_to = agent
        ticket_doc.auto_assigned = 1
        ticket_doc.save(ignore_permissions=True)

    if initial_message:
        _send_raven_message(channel_id, initial_message)
        _log_chat_to_ticket(ticket_doc, channel_id, initial_message, owner=user)
        _update_chat_link_activity(chat_link, message_text=initial_message, message_user=user)
        notify_users(
            [agent],
            event_key="chat_message",
            title=f"پیام چت جدید روی {ticket_doc.name}",
            body=frappe.utils.strip_html(initial_message)[:240],
            ticket_name=ticket_doc.name,
            route=f"/management-support?ticket={ticket_doc.name}&chat={channel_id}",
            payload={"channel_id": channel_id, "chat_link": chat_link.name if chat_link else ""},
        )

    frappe.db.commit()
    return {
        "ok": True,
        "online": True,
        "ticket": ticket_doc.name,
        "channel_id": channel_id,
        "chat_link": chat_link.name if chat_link else "",
        "agent_user": agent,
    }


def portal_send_support_chat_message(channel_id=None, ticket_name=None, message=None):
    ensure_support_runtime_ready(include_phase2=False)
    user = require_authenticated_user()

    ticket_doc = None
    chat_link = None
    if ticket_name:
        ticket_doc = _ticket_doc(ticket_name)
        if not _customer_can_access_ticket(ticket_doc, user=user):
            frappe.throw(_("به این تیکت دسترسی ندارید."), frappe.PermissionError)
    if channel_id:
        chat_link = _resolve_chat_link(channel_id=channel_id, customer_user=user)
        if chat_link and not ticket_doc:
            ticket_doc = _ticket_doc(chat_link.ticket)
    if not ticket_doc:
        frappe.throw(_("تیکت یا کانال معتبر ارسال نشده است."), frappe.ValidationError)

    text = frappe.utils.sanitize_html(message or "").strip()
    if not text:
        frappe.throw(_("متن پیام خالی است."), frappe.ValidationError)

    sent_message_name = ""
    if channel_id and _raven_runtime_ready():
        sent = _send_raven_message(channel_id, text)
        sent_message_name = getattr(sent, "name", "") if sent else ""

    chat_comm = _log_chat_to_ticket(ticket_doc, channel_id or "", text, owner=user)
    if chat_link:
        _update_chat_link_activity(chat_link, message_text=text, message_user=user)
    ticket_doc.last_customer_reply_on = chat_comm.creation if chat_comm else now_datetime()
    reopen = _reopen_status()
    if reopen:
        ticket_doc.status = reopen
    ticket_doc.save(ignore_permissions=True)
    create_ticket_activity(ticket_doc.name, "customer_replied_chat", owner=user)
    run_support_automation(ticket_doc, trigger_event="Customer Reply", context={"source": "chat"})

    targets = [chat_link.agent_user] if chat_link and chat_link.agent_user else support_agent_users(team=ticket_doc.team)
    notify_users(
        targets,
        event_key="chat_message",
        title=f"پیام چت جدید از مشتری ({ticket_doc.name})",
        body=frappe.utils.strip_html(text)[:240],
        ticket_name=ticket_doc.name,
        route=f"/management-support?ticket={ticket_doc.name}&chat={channel_id or ''}",
        payload={"channel_id": channel_id or "", "from": user},
    )

    frappe.db.commit()
    return {
        "ok": True,
        "ticket": ticket_doc.name,
        "channel_id": channel_id or (chat_link.raven_channel if chat_link else ""),
        "message_name": sent_message_name,
    }


def portal_list_support_chats(page=1, page_size=20):
    require_authenticated_user()
    user = frappe.session.user
    if not _doctype_exists("MS Support Chat Link"):
        return {"items": [], "page": 1, "page_size": page_size, "total": 0, "total_pages": 1, "has_next": False, "has_prev": False}

    page = max(cint(page), 1)
    page_size = min(max(cint(page_size), 1), 100)
    start = (page - 1) * page_size

    filters = {"customer_user": user}
    total = frappe.db.count("MS Support Chat Link", filters=filters)
    rows = frappe.get_all(
        "MS Support Chat Link",
        filters=filters,
        fields=[
            "name",
            "ticket",
            "raven_channel",
            "status",
            "agent_user",
            "last_message",
            "last_message_at",
            "last_message_by",
            "opened_on",
            "closed_on",
        ],
        order_by="modified desc",
        start=start,
        page_length=page_size,
        ignore_permissions=True,
    )

    for row in rows:
        ticket_meta = frappe.db.get_value(
            "MS Support Ticket",
            row.get("ticket"),
            ["subject", "status", "team"],
            as_dict=True,
        ) or {}
        row["ticket_subject"] = ticket_meta.get("subject") or ""
        row["ticket_status"] = ticket_meta.get("status") or ""
        row["team"] = ticket_meta.get("team") or ""

    total_pages = max(int((total + page_size - 1) / page_size), 1)
    return {
        "items": rows,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def management_list_support_live_chats(page=1, page_size=100, status=None, search=None):
    ensure_support_runtime_ready()
    require_management_access()

    if not _doctype_exists("MS Support Chat Link"):
        return {"items": [], "page": 1, "page_size": page_size, "total": 0, "total_pages": 1, "has_next": False, "has_prev": False}

    page = max(cint(page), 1)
    page_size = min(max(cint(page_size), 1), 200)
    start = (page - 1) * page_size

    filters = {}
    if status:
        filters["status"] = status

    rows = frappe.get_all(
        "MS Support Chat Link",
        filters=filters,
        fields=[
            "name",
            "ticket",
            "raven_channel",
            "status",
            "customer_user",
            "agent_user",
            "last_message",
            "last_message_at",
            "last_message_by",
            "opened_on",
            "closed_on",
        ],
        order_by="modified desc",
        ignore_permissions=True,
        limit_page_length=0,
    )

    term = str(search or "").strip().lower()
    filtered = []
    for row in rows:
        ticket_meta = frappe.db.get_value(
            "MS Support Ticket",
            row.get("ticket"),
            ["subject", "status", "priority", "team", "customer"],
            as_dict=True,
        ) or {}
        payload = {
            **row,
            "ticket_subject": ticket_meta.get("subject") or "",
            "ticket_status": ticket_meta.get("status") or "",
            "ticket_priority": ticket_meta.get("priority") or "",
            "team": ticket_meta.get("team") or "",
            "customer": ticket_meta.get("customer") or "",
        }
        if term:
            stack = " ".join(
                [
                    str(payload.get("ticket") or ""),
                    str(payload.get("ticket_subject") or ""),
                    str(payload.get("customer_user") or ""),
                    str(payload.get("agent_user") or ""),
                    str(payload.get("customer") or ""),
                    str(payload.get("last_message") or ""),
                ]
            ).lower()
            if term not in stack:
                continue
        filtered.append(payload)

    total = len(filtered)
    items = filtered[start : start + page_size]
    total_pages = max(int((total + page_size - 1) / page_size), 1)
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def management_reply_support_chat(chat_link_name=None, channel_id=None, ticket_name=None, message=None):
    ensure_support_runtime_ready()
    require_management_access()

    text = frappe.utils.sanitize_html(message or "").strip()
    if not text:
        frappe.throw(_("متن پاسخ خالی است."), frappe.ValidationError)

    chat_link = None
    if chat_link_name and _doctype_exists("MS Support Chat Link") and frappe.db.exists("MS Support Chat Link", chat_link_name):
        chat_link = frappe.get_doc("MS Support Chat Link", chat_link_name)
    elif channel_id:
        chat_link = _resolve_chat_link(channel_id=channel_id)
    elif ticket_name:
        chat_link = _resolve_chat_link(ticket_name=ticket_name)

    if chat_link:
        ticket_doc = _ticket_doc(chat_link.ticket)
        channel_id = chat_link.raven_channel
    else:
        if not ticket_name:
            frappe.throw(_("شناسه چت یا تیکت معتبر ارسال نشده است."), frappe.ValidationError)
        ticket_doc = _ticket_doc(ticket_name)

    message_name = ""
    if channel_id and _raven_runtime_ready():
        try:
            sent = _send_raven_message(channel_id, text)
            message_name = getattr(sent, "name", "") if sent else ""
        except Exception:
            frappe.log_error(frappe.get_traceback(), "MS Support Chat Reply Send Failed")

    chat_comm = _log_chat_to_ticket(ticket_doc, channel_id or "", text, owner=frappe.session.user)
    _update_response_metrics(ticket_doc, response_at=chat_comm.creation if chat_comm else now_datetime())
    if get_status_category(ticket_doc.status) == "Paused":
        reopen = _reopen_status()
        if reopen:
            ticket_doc.status = reopen
    ticket_doc.save(ignore_permissions=True)
    create_ticket_activity(ticket_doc.name, "agent_replied_chat")
    run_support_automation(ticket_doc, trigger_event="Agent Reply", context={"source": "chat"})
    if chat_link:
        _update_chat_link_activity(chat_link, message_text=text, message_user=frappe.session.user)

    notify_users(
        [ticket_doc.raised_by],
        event_key="chat_message",
        title=f"پاسخ پشتیبانی در چت ({ticket_doc.name})",
        body=frappe.utils.strip_html(text)[:240],
        ticket_name=ticket_doc.name,
        route=f"/dashboard?tab=support_tickets&ticket={ticket_doc.name}",
        payload={"channel_id": channel_id or ""},
    )

    frappe.db.commit()
    return {
        "ok": True,
        "ticket": ticket_doc.name,
        "chat_link": chat_link.name if chat_link else "",
        "channel_id": channel_id or "",
        "message_name": message_name,
    }
