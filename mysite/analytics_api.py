import json

import frappe

from mysite import analytics_service


def _payload_from_request(default=None):
    if getattr(frappe, "request", None) and frappe.request.data:
        try:
            payload = frappe.parse_json(frappe.request.data)
        except Exception:
            try:
                payload = json.loads(frappe.request.data)
            except Exception:
                return default or {}

        # Normalize non-dict payloads to avoid runtime type errors downstream.
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, bytes):
            try:
                decoded = payload.decode("utf-8")
                normalized = frappe.parse_json(decoded)
                return normalized if isinstance(normalized, dict) else (default or {})
            except Exception:
                return default or {}
        if isinstance(payload, str):
            try:
                normalized = frappe.parse_json(payload)
                return normalized if isinstance(normalized, dict) else (default or {})
            except Exception:
                return default or {}
        return default or {}

    return default or {}


def _safe_track_call(fn, payload):
    try:
        return fn(payload)
    except frappe.ValidationError as err:
        frappe.local.response["http_status_code"] = 200
        message = str(err or "").strip() or "درخواست آنالیتیکس معتبر نبود."
        return {
            "ok": False,
            "skipped": True,
            "message": message,
            "exc_type": err.__class__.__name__,
        }
    except Exception as err:
        frappe.local.response["http_status_code"] = 200
        return {
            "ok": False,
            "skipped": True,
            "message": "ثبت رویداد آنالیتیکس موقتاً انجام نشد.",
            "exc_type": err.__class__.__name__,
        }


@frappe.whitelist(allow_guest=True)
def track_event():
    payload = _payload_from_request(default={})
    if not isinstance(payload, dict):
        payload = {}
    for key, value in frappe.form_dict.items():
        if key not in payload:
            payload[key] = value
    return _safe_track_call(analytics_service.track_event_payload, payload)


@frappe.whitelist(allow_guest=True)
def track_page_view():
    payload = _payload_from_request(default={})
    if not isinstance(payload, dict):
        payload = {}
    for key, value in frappe.form_dict.items():
        if key not in payload:
            payload[key] = value
    return _safe_track_call(analytics_service.track_page_view_payload, payload)


@frappe.whitelist()
def get_overview(range_key=None, from_date=None, to_date=None):
    return analytics_service.get_overview_payload(range_key=range_key, from_date=from_date, to_date=to_date)


@frappe.whitelist()
def get_conversion_funnel(range_key=None, from_date=None, to_date=None, category=None, device_type=None, source_channel=None):
    return analytics_service.get_conversion_funnel_payload(
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
        category=category,
        device_type=device_type,
        source_channel=source_channel,
    )


@frappe.whitelist()
def get_user_behavior(range_key=None, from_date=None, to_date=None, limit=10):
    return analytics_service.get_user_behavior_payload(
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@frappe.whitelist()
def get_site_traffic(range_key=None, from_date=None, to_date=None, group_key=None, page_path=None, limit=20):
    return analytics_service.get_site_traffic_payload(
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
        group_key=group_key,
        page_path=page_path,
        limit=limit,
    )


@frappe.whitelist()
def get_products_report(range_key=None, from_date=None, to_date=None, category=None, sort_by="views", sort_order="desc", page=1, page_size=20):
    return analytics_service.get_products_report_payload(
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@frappe.whitelist()
def export_products_report(file_type="xlsx", range_key=None, from_date=None, to_date=None, category=None, sort_by="views", sort_order="desc"):
    return analytics_service.export_products_report_payload(
        file_type=file_type,
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@frappe.whitelist()
def get_time_comparison(left_from=None, left_to=None, right_from=None, right_to=None, preset="week_vs_previous"):
    return analytics_service.get_time_comparison_payload(
        left_from=left_from,
        left_to=left_to,
        right_from=right_from,
        right_to=right_to,
        preset=preset,
    )


@frappe.whitelist()
def get_tracking_settings():
    return analytics_service.get_tracking_settings_payload()


@frappe.whitelist()
def get_advanced_insights(range_key=None, from_date=None, to_date=None, segment_key=None):
    return analytics_service.get_advanced_insights_payload(
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
        segment_key=segment_key,
    )


@frappe.whitelist()
def get_technical_dashboard(range_key=None, from_date=None, to_date=None):
    return analytics_service.get_technical_dashboard_payload(
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
    )


@frappe.whitelist()
def get_external_analytics_settings():
    return analytics_service.get_external_analytics_settings_payload()


@frappe.whitelist()
def update_external_analytics_settings(payload=None):
    if isinstance(payload, str):
        payload = json.loads(payload)
    if payload is None:
        payload = _payload_from_request(default={})
    return analytics_service.update_external_analytics_settings_payload(payload)


@frappe.whitelist()
def update_tracking_settings(payload=None):
    if isinstance(payload, str):
        payload = json.loads(payload)
    if payload is None:
        payload = _payload_from_request(default={})
    return analytics_service.update_tracking_settings_payload(payload)


@frappe.whitelist()
def get_funnel_drop_diagnosis(step=None, range_key=None, from_date=None, to_date=None):
    return analytics_service.get_funnel_drop_diagnosis_payload(
        step=step,
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
    )


@frappe.whitelist()
def get_payment_gateway_success(range_key=None, from_date=None, to_date=None):
    return analytics_service.get_payment_gateway_success_payload(
        range_key=range_key,
        from_date=from_date,
        to_date=to_date,
    )
