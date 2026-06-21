from __future__ import annotations

import json

import frappe


DEFAULT_SAVE_ERROR_MESSAGE = "ذخیره انجام نشد. لطفاً یک‌بار صفحه را رفرش کنید و دوباره تلاش کنید."


def set_json_http_200() -> None:
    # Keep legacy frontend contract: transport success with structured application error payload.
    frappe.local.response["http_status_code"] = 200


def json_error_payload(message: str, exc_type: str = "Error", exception: str | None = None) -> dict:
    return {
        "ok": False,
        "message": str(message or "خطای نامشخص"),
        "exception": str(exception if exception is not None else message),
        "exc_type": str(exc_type or "Error"),
    }


def json_error_from_exception(error: Exception, *, default_message: str = DEFAULT_SAVE_ERROR_MESSAGE, log_title: str = "management_editor:unexpected", context: dict | None = None) -> dict:
    context = context or {}
    try:
        frappe.log_error(
            title=log_title,
            message=f"{frappe.get_traceback()}\n\ncontext={json.dumps(context, ensure_ascii=False)}",
        )
    except Exception:
        pass
    set_json_http_200()
    message = str(default_message or DEFAULT_SAVE_ERROR_MESSAGE)
    return json_error_payload(message=message, exc_type=error.__class__.__name__, exception=str(error or message))


def json_validation_error(error: Exception, *, fallback_message: str = "ذخیره انجام نشد. ورودی ارسالی معتبر نیست.") -> dict:
    message = str(error or "").strip() or fallback_message
    set_json_http_200()
    return json_error_payload(message=message, exc_type=error.__class__.__name__, exception=message)
