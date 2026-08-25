import json
from typing import Any

import frappe
import requests
from frappe import _
from frappe.integrations.utils import create_request_log
from frappe.utils import cint, flt, get_url

REQUEST_TIMEOUT_SECONDS = 20
ZARINPAL_SERVICE_NAME = "Zarinpal"


def _safe_json_loads(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _parse_json_arg(value: Any, fieldname: str):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            frappe.throw(_("فرمت داده \"{0}\" نامعتبر است.").format(fieldname), frappe.ValidationError)
    return value


def _normalize_items(items):
    rows = []
    for item in items or []:
        qty = max(flt((item or {}).get("qty") or 1), 1)

        config = (item or {}).get("configuration")
        if not config:
            config = (item or {}).get("config")
        if isinstance(config, (dict, list)):
            config = json.dumps(config, ensure_ascii=False)

        price = flt((item or {}).get("price"))
        if not price:
            price = flt((item or {}).get("total_price") or (item or {}).get("totalPrice"))
        if not price and isinstance((item or {}).get("config"), dict):
            price = flt(((item or {}).get("config") or {}).get("totalPrice"))

        rows.append(
            {
                "item_name": (item or {}).get("item_name") or (item or {}).get("name") or (item or {}).get("item_code") or _("Item"),
                "item_code": (item or {}).get("item_code") or (item or {}).get("name") or "",
                "qty": qty,
                "price": price,
                "configuration": config or "",
            }
        )
    return rows


def _get_amount_toman(items):
    return flt(sum(flt((row or {}).get("price") or 0) for row in (items or [])))


def _get_zarinpal_settings():
    site_config = frappe.get_site_config() or {}
    merchant_id = str(site_config.get("zarinpal_merchant_id") or "").strip()
    sandbox = cint(site_config.get("zarinpal_sandbox") or 0) == 1
    callback_url = str(site_config.get("zarinpal_callback_url") or "").strip() or get_url("/mysite/payment-callback")

    if not merchant_id:
        frappe.throw(
            _("تنظیمات زرین‌پال کامل نیست. مقدار `zarinpal_merchant_id` را در Site Config تنظیم کنید."),
            frappe.ValidationError,
        )

    api_base = "https://sandbox.zarinpal.com" if sandbox else "https://api.zarinpal.com"
    startpay_base = "https://sandbox.zarinpal.com" if sandbox else "https://www.zarinpal.com"

    return {
        "merchant_id": merchant_id,
        "sandbox": sandbox,
        "callback_url": callback_url,
        "request_url": f"{api_base}/pg/v4/payment/request.json",
        "verify_url": f"{api_base}/pg/v4/payment/verify.json",
        "startpay_base": startpay_base,
    }


def _extract_gateway_error(payload):
    payload = payload or {}
    errors = payload.get("errors")
    if isinstance(errors, dict):
        message = str(errors.get("message") or "").strip()
        if message:
            return message
        for value in errors.values():
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, list):
                for row in value:
                    if isinstance(row, str) and row.strip():
                        return row.strip()
    if isinstance(errors, list):
        for row in errors:
            if isinstance(row, str) and row.strip():
                return row.strip()
            if isinstance(row, dict):
                message = str(row.get("message") or "").strip()
                if message:
                    return message
    return ""


def _build_metadata(phone=None, email=None):
    metadata = {}
    phone = str(phone or "").strip()
    email = str(email or "").strip()
    if phone:
        metadata["mobile"] = phone
    if email:
        metadata["email"] = email
    return metadata


def _get_customer_contact(customer_name):
    if not customer_name:
        return {}
    return (
        frappe.db.get_value(
            "Customer",
            customer_name,
            ["customer_name", "email_id", "mobile_no"],
            as_dict=True,
        )
        or {}
    )


def _build_startpay_url(settings, authority):
    return f"{settings['startpay_base']}/pg/StartPay/{authority}"


def _call_payment_request(settings, amount_rial, description, metadata):
    payload = {
        "merchant_id": settings["merchant_id"],
        "amount": cint(amount_rial),
        "callback_url": settings["callback_url"],
        "description": description,
    }
    if metadata:
        payload["metadata"] = metadata

    response = requests.post(
        settings["request_url"],
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json() or {}


def _call_payment_verify(settings, amount_rial, authority):
    payload = {
        "merchant_id": settings["merchant_id"],
        "amount": cint(amount_rial),
        "authority": authority,
    }
    response = requests.post(
        settings["verify_url"],
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json() or {}


def _append_payment_note_to_quotation_request(quotation_name, authority, ref_id, amount_toman):
    quotation_name = str(quotation_name or "").strip()
    if not quotation_name or not frappe.db.exists("Quotation Request", quotation_name):
        return

    doc = frappe.get_doc("Quotation Request", quotation_name)
    marker = f"Authority: {authority}"
    existing_note = str(doc.request_note or "")
    if marker in existing_note:
        return

    payment_note = (
        f"پرداخت زرین‌پال تایید شد | مبلغ: {int(flt(amount_toman)):,} تومان | RefID: {ref_id or '-'} | {marker}"
    )

    doc.request_note = f"{existing_note}\n{payment_note}".strip()
    if doc.status == "Submitted":
        doc.status = "In Progress"
    doc.save(ignore_permissions=True)
    frappe.db.commit()


def _create_zarinpal_integration_request(
    quotation_name,
    customer_name,
    amount_toman,
    amount_rial,
    mode,
    metadata,
    callback_url,
):
    return create_request_log(
        data={
            "reference_doctype": "Quotation Request",
            "reference_docname": quotation_name,
            "quotation_request": quotation_name,
            "customer": customer_name,
            "amount_toman": flt(amount_toman),
            "amount_rial": cint(amount_rial),
            "mode": mode,
            "callback_url": callback_url,
            "metadata": metadata or {},
            "payment_status": "queued",
        },
        service_name=ZARINPAL_SERVICE_NAME,
    )


def _initiate_payment(settings, quotation_name, customer_name, amount_toman, metadata, mode):
    amount_toman = flt(amount_toman)
    if amount_toman <= 0:
        frappe.throw(_("برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد."), frappe.ValidationError)

    amount_rial = cint(round(amount_toman * 10))
    description = f"پرداخت سفارش {quotation_name}"

    integration_request = _create_zarinpal_integration_request(
        quotation_name=quotation_name,
        customer_name=customer_name,
        amount_toman=amount_toman,
        amount_rial=amount_rial,
        mode=mode,
        metadata=metadata,
        callback_url=settings.get("callback_url"),
    )

    try:
        gateway_response = _call_payment_request(
            settings=settings,
            amount_rial=amount_rial,
            description=description,
            metadata=metadata,
        )
    except Exception:
        integration_request.update_status(
            {
                "payment_status": "failed",
                "gateway_error": "request_failed",
            },
            "Failed",
        )
        integration_request.db_set("error", frappe.as_json({"traceback": frappe.get_traceback()}, indent=1))
        frappe.throw(_("اتصال به زرین‌پال برقرار نشد. لطفاً دوباره تلاش کنید."), frappe.ValidationError)

    data = (gateway_response or {}).get("data") or {}
    authority = str(data.get("authority") or "").strip()
    code = cint(data.get("code") or 0)

    if code == 100 and authority:
        integration_request.db_set("request_id", authority)
        integration_request.update_status(
            {
                "authority": authority,
                "request_code": code,
                "payment_status": "authorized",
            },
            "Authorized",
        )
        integration_request.db_set("output", frappe.as_json(gateway_response, indent=1))

        return {
            "status": "success",
            "payment_url": _build_startpay_url(settings, authority),
            "authority": authority,
            "quotation_request": quotation_name,
            "customer_name": customer_name,
            "integration_request": integration_request.name,
        }

    message = _extract_gateway_error(gateway_response) or _("درخواست پرداخت توسط زرین‌پال تایید نشد.")
    integration_request.update_status(
        {
            "payment_status": "failed",
            "request_code": code,
            "gateway_error": message,
        },
        "Failed",
    )
    integration_request.db_set("error", frappe.as_json(gateway_response, indent=1))
    frappe.throw(message, frappe.ValidationError)


def _find_integration_request_by_authority(authority):
    authority = str(authority or "").strip()
    if not authority:
        return None

    rows = frappe.get_all(
        "Integration Request",
        filters={
            "integration_request_service": ZARINPAL_SERVICE_NAME,
            "request_id": authority,
        },
        fields=["name"],
        order_by="creation desc",
        limit_page_length=1,
        ignore_permissions=True,
    )
    if not rows:
        return None
    return frappe.get_doc("Integration Request", rows[0]["name"])


def verify_payment_status(authority=None, status=None):
    authority = str(authority or "").strip()
    status = str(status or "").strip().upper()

    if not authority:
        return {
            "ok": False,
            "message": _("شناسه Authority ارسال نشده است."),
        }

    integration_request = _find_integration_request_by_authority(authority)
    if not integration_request:
        return {
            "ok": False,
            "message": _("تراکنش مرتبط با این پرداخت پیدا نشد."),
            "authority": authority,
        }

    request_data = _safe_json_loads(integration_request.data)
    quotation_name = str(request_data.get("quotation_request") or request_data.get("reference_docname") or "").strip()
    amount_toman = flt(request_data.get("amount_toman") or 0)
    amount_rial = cint(request_data.get("amount_rial") or 0)

    if integration_request.status == "Completed":
        output_data = _safe_json_loads(integration_request.output)
        output_payload = output_data.get("data") or {}
        return {
            "ok": True,
            "message": _("این پرداخت قبلاً تایید شده است."),
            "authority": authority,
            "ref_id": output_payload.get("ref_id") or output_payload.get("RefID"),
            "quotation_request": quotation_name,
            "amount_toman": amount_toman,
        }

    if status != "OK":
        integration_request.update_status(
            {
                "payment_status": "cancelled",
                "callback_status": status or "NOK",
            },
            "Cancelled",
        )
        return {
            "ok": False,
            "message": _("پرداخت توسط کاربر لغو شد یا ناموفق بود."),
            "authority": authority,
            "quotation_request": quotation_name,
            "amount_toman": amount_toman,
        }

    settings = _get_zarinpal_settings()

    try:
        verify_response = _call_payment_verify(
            settings=settings,
            amount_rial=amount_rial,
            authority=authority,
        )
    except Exception:
        integration_request.update_status(
            {
                "payment_status": "failed",
                "verify_error": "request_failed",
            },
            "Failed",
        )
        integration_request.db_set("error", frappe.as_json({"traceback": frappe.get_traceback()}, indent=1))
        return {
            "ok": False,
            "message": _("ارتباط با زرین‌پال برای تایید پرداخت برقرار نشد."),
            "authority": authority,
            "quotation_request": quotation_name,
            "amount_toman": amount_toman,
        }

    data = (verify_response or {}).get("data") or {}
    code = cint(data.get("code") or 0)
    ref_id = data.get("ref_id") or data.get("RefID")

    if code in {100, 101}:
        integration_request.update_status(
            {
                "payment_status": "completed",
                "verify_code": code,
                "ref_id": ref_id,
                "card_pan": data.get("card_pan"),
                "card_hash": data.get("card_hash"),
            },
            "Completed",
        )
        integration_request.db_set("output", frappe.as_json(verify_response, indent=1))
        _append_payment_note_to_quotation_request(
            quotation_name=quotation_name,
            authority=authority,
            ref_id=ref_id,
            amount_toman=amount_toman,
        )
        return {
            "ok": True,
            "message": _("پرداخت با موفقیت تایید شد."),
            "authority": authority,
            "ref_id": ref_id,
            "quotation_request": quotation_name,
            "amount_toman": amount_toman,
        }

    message = _extract_gateway_error(verify_response) or _("تایید پرداخت توسط زرین‌پال انجام نشد.")
    integration_request.update_status(
        {
            "payment_status": "failed",
            "verify_code": code,
            "verify_error": message,
        },
        "Failed",
    )
    integration_request.db_set("error", frappe.as_json(verify_response, indent=1))
    return {
        "ok": False,
        "message": message,
        "authority": authority,
        "quotation_request": quotation_name,
        "amount_toman": amount_toman,
    }


@frappe.whitelist(allow_guest=True)
def start_guest_checkout(customer_info, items, note=None):
    del note
    settings = _get_zarinpal_settings()

    customer_info = _parse_json_arg(customer_info, "customer_info") or {}
    items = _parse_json_arg(items, "items") or []

    normalized_items = _normalize_items(items)
    if not normalized_items:
        frappe.throw(_("سبد خرید خالی است."), frappe.ValidationError)

    amount_toman = _get_amount_toman(normalized_items)
    if amount_toman <= 0:
        frappe.throw(_("برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد."), frappe.ValidationError)

    customer_name = str((customer_info or {}).get("name") or "").strip()
    customer_phone = str((customer_info or {}).get("phone") or "").strip()
    customer_email = str((customer_info or {}).get("email") or "").strip()

    if not customer_name or not customer_phone:
        frappe.throw(_("برای پرداخت آنلاین، نام و شماره همراه الزامی است."), frappe.ValidationError)

    from mysite.www.mysite.product import submit_quotation_request

    quotation_result = submit_quotation_request(customer_info=customer_info, items=items)
    if (quotation_result or {}).get("status") != "success":
        frappe.throw(_("ثبت درخواست پیش‌فاکتور ناموفق بود."), frappe.ValidationError)

    quotation_name = quotation_result.get("name")

    return _initiate_payment(
        settings=settings,
        quotation_name=quotation_name,
        customer_name=customer_name,
        amount_toman=amount_toman,
        metadata=_build_metadata(phone=customer_phone, email=customer_email),
        mode="guest",
    )


@frappe.whitelist()
def start_portal_checkout(customer=None, items=None, note=None):
    settings = _get_zarinpal_settings()

    from mysite.portal_api import (
        _get_allowed_customers_for_session_user,
        _resolve_customer_scope,
        portal_submit_quotation_request,
    )

    items = _parse_json_arg(items, "items") or []
    normalized_items = _normalize_items(items)
    if not normalized_items:
        frappe.throw(_("سبد خرید خالی است."), frappe.ValidationError)

    amount_toman = _get_amount_toman(normalized_items)
    if amount_toman <= 0:
        frappe.throw(_("برای پرداخت آنلاین، مبلغ سبد باید بیشتر از صفر باشد."), frappe.ValidationError)

    allowed_customers = _get_allowed_customers_for_session_user()
    scoped_customers = _resolve_customer_scope(customer, allowed_customers)
    if not scoped_customers:
        frappe.throw(_("برای این کاربر مشتری مجاز تعریف نشده است."), frappe.PermissionError)

    selected_customer = scoped_customers[0]
    contact = _get_customer_contact(selected_customer)

    quotation_result = portal_submit_quotation_request(
        customer=selected_customer,
        items=items,
        note=note,
    )
    if (quotation_result or {}).get("status") != "success":
        frappe.throw(_("ثبت درخواست پیش‌فاکتور ناموفق بود."), frappe.ValidationError)

    quotation_name = quotation_result.get("name")
    customer_label = quotation_result.get("customer_name") or contact.get("customer_name") or selected_customer

    return _initiate_payment(
        settings=settings,
        quotation_name=quotation_name,
        customer_name=customer_label,
        amount_toman=amount_toman,
        metadata=_build_metadata(phone=contact.get("mobile_no"), email=contact.get("email_id")),
        mode="portal",
    )


@frappe.whitelist(allow_guest=True)
def verify_payment(authority=None, status=None):
    return verify_payment_status(authority=authority, status=status)
