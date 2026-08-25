import json
import frappe
from mysite.www.mysite.sofas import get_nested_sofa_products
from mysite.www.mysite.cloth import get_cloth_groups
from mysite import analytics_service
from urllib.parse import unquote, quote
from erpnext.controllers.website_list_for_contact import get_parents_for_user
from frappe.utils import add_days, now, nowdate

no_cache = 1
_HAS_MANAGEMENT_FEATURE_FIELD = None


def _get_default_price_list():
    try:
        default_pl = frappe.db.get_value("Price List", {"default": 1, "enabled": 1}, "name")
        if default_pl:
            return default_pl
    except Exception:
        pass
    return frappe.db.get_single_value("Selling Settings", "selling_price_list")


def _resolve_customer_price_context(requested_customer):
    selected_customer = None
    selected_price_list = _get_default_price_list()
    price_source = "default"

    if not requested_customer or frappe.session.user == "Guest":
        return selected_customer, selected_price_list, price_source

    try:
        allowed_customers = get_parents_for_user("Customer") or []
    except Exception:
        allowed_customers = []

    if requested_customer in allowed_customers:
        selected_customer = requested_customer
        customer_price_list = frappe.db.get_value("Customer", requested_customer, "default_price_list")
        if customer_price_list:
            selected_price_list = customer_price_list
            price_source = "customer"

    return selected_customer, selected_price_list, price_source


FEEDBACK_SUBJECT_PREFIX = "WEB_FEEDBACK::"
FEEDBACK_REVIEW_PREFIX = "WEB_FEEDBACK::REVIEW::"
FEEDBACK_QUESTION_PREFIX = "WEB_FEEDBACK::QUESTION"
FEEDBACK_ANSWER_PREFIX = "WEB_FEEDBACK::ANSWER::"
FUNNEL_SUBJECT_PREFIX = "WEB_FUNNEL::"
FUNNEL_STEP_PRODUCT_VIEW = "product_view"
FUNNEL_STEP_ADD_TO_CART = "add_to_cart"
FUNNEL_STEP_ORDER_SUBMIT = "order_submit"
FUNNEL_ALLOWED_STEPS = {
    FUNNEL_STEP_PRODUCT_VIEW,
    FUNNEL_STEP_ADD_TO_CART,
    FUNNEL_STEP_ORDER_SUBMIT,
}
MANAGEMENT_PRODUCT_FEATURES_FIELD = "custom_management_features_json"


def _safe_json_loads(raw):
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _normalize_management_feature_rows(raw_rows):
    rows = raw_rows
    if isinstance(rows, str):
        stripped = rows.strip()
        if not stripped:
            rows = []
        else:
            try:
                rows = json.loads(stripped)
            except Exception:
                rows = []

    if isinstance(rows, dict):
        rows = rows.get("rows") or rows.get("items") or []
    if not isinstance(rows, (list, tuple)):
        return []

    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label") or row.get("name") or row.get("title") or "").strip()
        value = str(row.get("value") or row.get("content") or row.get("description") or "").strip()
        if not label and not value:
            continue
        normalized.append({"label": label[:140], "value": value[:800]})
        if len(normalized) >= 50:
            break
    return normalized


def _normalize_file_url(value):
    url = str(value or "").strip()
    if not url:
        return ""
    if url.startswith("/private/files/"):
        return "/files/" + url.replace("/private/files/", "", 1)
    return url


def _has_management_features_field():
    global _HAS_MANAGEMENT_FEATURE_FIELD
    if _HAS_MANAGEMENT_FEATURE_FIELD is not None:
        return bool(_HAS_MANAGEMENT_FEATURE_FIELD)
    try:
        item_meta = frappe.get_meta("Item")
        _HAS_MANAGEMENT_FEATURE_FIELD = any(df.fieldname == MANAGEMENT_PRODUCT_FEATURES_FIELD for df in item_meta.fields)
    except Exception:
        _HAS_MANAGEMENT_FEATURE_FIELD = False
    return bool(_HAS_MANAGEMENT_FEATURE_FIELD)


def _get_management_features_map_for_items(item_codes):
    if not _has_management_features_field():
        return {}
    normalized_codes = []
    for code in item_codes or []:
        item_code = str(code or "").strip()
        if item_code and item_code not in normalized_codes:
            normalized_codes.append(item_code)
    if not normalized_codes:
        return {}

    placeholders = ", ".join(["%s"] * len(normalized_codes))
    try:
        rows = frappe.db.sql(
            f"""
            SELECT
                i.name,
                i.item_code,
                i.`{MANAGEMENT_PRODUCT_FEATURES_FIELD}` AS feature_payload
            FROM `tabItem` i
            WHERE i.name IN ({placeholders}) OR i.item_code IN ({placeholders})
            """,
            tuple(normalized_codes) + tuple(normalized_codes),
            as_dict=True,
        )
    except Exception:
        return {}

    features_map = {}
    for row in rows or []:
        parsed_rows = _normalize_management_feature_rows(row.get("feature_payload"))
        if not parsed_rows:
            continue
        item_name = str(row.get("name") or "").strip()
        item_code = str(row.get("item_code") or "").strip()
        if item_name:
            features_map[item_name] = parsed_rows
        if item_code:
            features_map[item_code] = parsed_rows
    return features_map


def _resolve_product_item_code(product_details):
    if not isinstance(product_details, dict):
        return ""
    candidates = [
        product_details.get("item_code"),
        product_details.get("name"),
    ]
    variants = product_details.get("variants") or []
    if isinstance(variants, list):
        for row in variants:
            if isinstance(row, dict):
                candidates.append(row.get("item_code"))

    for candidate in candidates:
        item_code = str(candidate or "").strip()
        if item_code and frappe.db.exists("Item", item_code):
            return item_code
    return ""


def _get_management_feature_rows_for_item(item_code):
    item_code = str(item_code or "").strip()
    if not item_code:
        return []
    return _get_management_features_map_for_items([item_code]).get(item_code, [])


def _enrich_product_variant_metadata(product_details):
    if not isinstance(product_details, dict):
        return

    variants = product_details.get("variants")
    if not isinstance(variants, list) or not variants:
        return

    raw_codes = []
    for row in variants:
        if not isinstance(row, dict):
            continue
        code = str(row.get("item_code") or "").strip()
        if code and code not in raw_codes:
            raw_codes.append(code)
    if not raw_codes:
        return

    placeholders = ", ".join(["%s"] * len(raw_codes))
    item_rows = frappe.db.sql(
        f"""
        SELECT
            i.name,
            i.item_code,
            i.item_name,
            i.description,
            i.image
        FROM `tabItem` i
        WHERE i.name IN ({placeholders}) OR i.item_code IN ({placeholders})
        """,
        tuple(raw_codes) + tuple(raw_codes),
        as_dict=True,
    )
    if not item_rows:
        return

    item_by_name = {}
    item_by_code = {}
    item_names = []
    for row in item_rows:
        row_name = str(row.get("name") or "").strip()
        row_code = str(row.get("item_code") or "").strip()
        row["image"] = _normalize_file_url(row.get("image"))
        if row_name:
            item_by_name[row_name] = row
            item_names.append(row_name)
        if row_code:
            item_by_code[row_code] = row

    model_by_item = {}
    if item_names and frappe.db.exists("DocType", "Item Variant Attribute"):
        model_attr_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={"parent": ["in", item_names], "attribute": "مدل محصول"},
            fields=["parent", "attribute_value"],
            limit_page_length=0,
            ignore_permissions=True,
        )
        for row in model_attr_rows:
            parent = str(row.get("parent") or "").strip()
            value = str(row.get("attribute_value") or "").strip()
            if parent and value:
                model_by_item[parent] = value

    images_by_item = {}
    if item_names:
        file_rows = frappe.db.sql(
            f"""
            SELECT attached_to_name, file_url
            FROM `tabFile`
            WHERE attached_to_doctype = 'Item'
              AND attached_to_name IN ({", ".join(["%s"] * len(item_names))})
              AND is_private = 0
              AND (
                   file_url LIKE '%%.jpg'
                OR file_url LIKE '%%.jpeg'
                OR file_url LIKE '%%.png'
                OR file_url LIKE '%%.webp'
              )
            ORDER BY creation ASC
            """,
            tuple(item_names),
            as_dict=True,
        )
        for row in file_rows or []:
            parent = str(row.get("attached_to_name") or "").strip()
            image_url = _normalize_file_url(row.get("file_url"))
            if not parent or not image_url:
                continue
            images_by_item.setdefault(parent, [])
            if image_url not in images_by_item[parent]:
                images_by_item[parent].append(image_url)

    feature_rows_map = _get_management_features_map_for_items(raw_codes + item_names)

    for variant in variants:
        if not isinstance(variant, dict):
            continue
        code = str(variant.get("item_code") or "").strip()
        if not code:
            continue

        item_row = item_by_name.get(code) or item_by_code.get(code)
        if not item_row:
            continue

        item_name_key = str(item_row.get("name") or "").strip()
        item_code_key = str(item_row.get("item_code") or "").strip()

        if item_code_key and not str(variant.get("item_code") or "").strip():
            variant["item_code"] = item_code_key
        if item_row.get("item_name") and not variant.get("item_name"):
            variant["item_name"] = item_row.get("item_name")
        if item_row.get("description") and not variant.get("description"):
            variant["description"] = item_row.get("description")

        merged_images = []
        candidate_images = []
        if variant.get("image"):
            candidate_images.append(variant.get("image"))
        if item_row.get("image"):
            candidate_images.append(item_row.get("image"))
        candidate_images.extend(images_by_item.get(item_name_key) or [])
        existing_variant_images = variant.get("images")
        if isinstance(existing_variant_images, list):
            candidate_images.extend(existing_variant_images)

        for image_url in candidate_images:
            normalized = _normalize_file_url(image_url)
            if normalized and normalized not in merged_images:
                merged_images.append(normalized)

        if merged_images:
            variant["image"] = merged_images[0]
            variant["images"] = merged_images

        attrs = variant.get("attributes")
        if not isinstance(attrs, dict):
            attrs = {}
        model_name = model_by_item.get(item_name_key)
        if model_name and not attrs.get("مدل محصول"):
            attrs["مدل محصول"] = model_name
        if attrs:
            variant["attributes"] = attrs

        feature_rows = feature_rows_map.get(item_name_key) or feature_rows_map.get(item_code_key) or []
        if feature_rows:
            variant["feature_rows"] = feature_rows


def _get_request_path():
    try:
        return frappe.local.request.path or ""
    except Exception:
        return ""


def _get_session_token(session_id=None):
    if session_id:
        return str(session_id).strip()
    try:
        sid = frappe.session.sid or ""
        if sid:
            return str(sid).strip()
    except Exception:
        pass
    try:
        sid_cookie = frappe.local.request.cookies.get("sid")
        if sid_cookie:
            return str(sid_cookie).strip()
    except Exception:
        pass
    return ""


def _resolve_model_name_for_item(item_code=None, fallback_name=None):
    item_code = (item_code or "").strip()
    if item_code:
        model_name = frappe.db.get_value(
            "Item Variant Attribute",
            {"parent": item_code, "attribute": "مدل محصول"},
            "attribute_value",
        )
        if model_name:
            return model_name
        variant_of = frappe.db.get_value("Item", item_code, "variant_of")
        if variant_of:
            parent_model = frappe.db.get_value(
                "Item Variant Attribute",
                {"parent": variant_of, "attribute": "مدل محصول"},
                "attribute_value",
            )
            if parent_model:
                return parent_model
    fallback_name = (fallback_name or "").strip()
    return fallback_name


def _create_funnel_event(
    step,
    model_name=None,
    item_code=None,
    qty=1,
    amount=0,
    session_id=None,
    customer=None,
    quotation_name=None,
    request_path=None,
    extra=None,
):
    if step not in FUNNEL_ALLOWED_STEPS:
        return None

    normalized_model = (model_name or "").strip()
    normalized_item = (item_code or "").strip()
    normalized_session = _get_session_token(session_id=session_id)
    normalized_customer = (customer or "").strip()
    normalized_path = (request_path or _get_request_path() or "").strip()

    try:
        qty_number = float(qty or 0)
    except Exception:
        qty_number = 0
    if qty_number <= 0:
        qty_number = 1

    try:
        amount_number = float(amount or 0)
    except Exception:
        amount_number = 0
    if amount_number < 0:
        amount_number = 0

    payload = {
        "step": step,
        "session_id": normalized_session,
        "model_name": normalized_model,
        "item_code": normalized_item,
        "qty": qty_number,
        "amount": amount_number,
        "customer": normalized_customer,
        "path": normalized_path,
        "timestamp": now(),
        "user": frappe.session.user or "Guest",
    }
    if quotation_name:
        payload["quotation_request"] = quotation_name
    if isinstance(extra, dict) and extra:
        payload["extra"] = extra

    reference_doctype = None
    reference_name = None
    if normalized_item and frappe.db.exists("Item", normalized_item):
        reference_doctype = "Item"
        reference_name = normalized_item
    elif quotation_name and frappe.db.exists("Quotation Request", quotation_name):
        reference_doctype = "Quotation Request"
        reference_name = quotation_name

    event_doc = frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "subject": f"{FUNNEL_SUBJECT_PREFIX}{step}",
            "content": json.dumps(payload, ensure_ascii=False),
            "comment_by": frappe.session.user_fullname or frappe.session.user or "Guest",
            "comment_email": frappe.session.user if frappe.session.user != "Guest" else "",
            "published": 1,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
        }
    )
    event_doc.insert(ignore_permissions=True)
    return event_doc.name


def _log_funnel_event_safely(**kwargs):
    try:
        event_id = _create_funnel_event(**kwargs)
        try:
            analytics_service.ingest_legacy_funnel_event(
                step=kwargs.get("step"),
                model_name=kwargs.get("model_name"),
                item_code=kwargs.get("item_code"),
                qty=kwargs.get("qty"),
                amount=kwargs.get("amount"),
                session_id=kwargs.get("session_id"),
                customer=kwargs.get("customer"),
                path=kwargs.get("request_path"),
                extra=kwargs.get("extra"),
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Legacy Funnel Bridge Error")
        if event_id:
            frappe.db.commit()
        return event_id
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Web Funnel Tracking Error")
        return None


def get_context(context):
    try:
        csrf_token = str(frappe.sessions.get_csrf_token() or "").strip()
    except Exception:
        csrf_token = ""
    
    context.safe_render = 0
    context.csrf_token = csrf_token
    
    raw_name = frappe.form_dict.get('name') or ""
    
    # Fallback: Extract from path if name is missing
    # Handles both /mysite/product/اورامان and /mysite/sofas/اورامان
    if not raw_name:
        path = frappe.local.request.path
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            raw_name = parts[-1] # Usually the last part is the name
            
    model_name = unquote(raw_name).replace('-', ' ').strip()
    
    if not model_name or model_name in ["product", "sofas", "barstools"]:
        frappe.throw("مدل محصول یافت نشد", frappe.DoesNotExistError)

    path = frappe.local.request.path
    is_sofa_route = "/sofas/" in path
    is_product_route = "/product/" in path

    requested_customer = (frappe.form_dict.get("customer") or "").strip()
    requested_bundle = (frappe.form_dict.get("bundle") or "").strip()
    requested_kind = (frappe.form_dict.get("kind") or "").strip().lower()
    selected_customer, price_list_param, price_source = _resolve_customer_price_context(requested_customer)

    product_details = None
    page_type = 'product'
    
    def _resolve_individual(kind):
        if kind == "chair":
            from mysite.www.mysite.controllers.chair_details import get_chair_details
            return get_chair_details(model_name, price_list_param), "chairdetails"
        if kind == "barstool":
            from mysite.www.mysite.controllers.barstool_details import get_barstool_details
            return get_barstool_details(model_name, price_list_param), "barstooldetails"
        if kind == "bench":
            from mysite.www.mysite.controllers.bench_details import get_bench_details
            return get_bench_details(model_name, price_list_param), "benchdetails"
        if kind == "table":
            from mysite.www.mysite.controllers.table_details import get_table_details
            return get_table_details(model_name, price_list_param), "tabledetails"
        if kind == "sofa":
            from mysite.www.mysite.controllers.sofa_details import get_sofa_unit_details
            return get_sofa_unit_details(model_name, price_list_param), "sofadetails"
        return None, "product"

    # helper for Case 1/2 switching
    def check_individual(preferred_kind=""):
        model_lc = model_name.lower()

        def has_any(words):
            return any(w in model_lc for w in words)

        dynamic_order = []
        if preferred_kind in {"chair", "barstool", "bench", "table", "sofa"}:
            dynamic_order.append(preferred_kind)
        if has_any(("مبل", "کاناپه", "اکسنت", "سکشنال")):
            dynamic_order.append("sofa")
        if has_any(("نیمکت", "پاف")):
            dynamic_order.append("bench")
        if has_any(("میز", "جلومبلی", "عسلی", "باکس")):
            dynamic_order.append("table")
        if has_any(("صندلی ناهارخوری", "ناهارخوری")):
            dynamic_order.append("chair")
        if has_any(("صندلی اپن", "اپن", "بار")):
            dynamic_order.append("barstool")

        for fallback_kind in ["chair", "barstool", "bench", "table", "sofa"]:
            if fallback_kind not in dynamic_order:
                dynamic_order.append(fallback_kind)

        for kind in dynamic_order:
            res, page = _resolve_individual(kind)
            if res:
                return res, page

        return None, "product"

    def check_collection():
        from mysite.www.mysite.controllers.sofa_details import get_sofa_collection_details
        res = get_sofa_collection_details(model_name, price_list_param)
        if res: return res, 'sofacollectiondetails'
        return None, 'product'

    # EXECUTE ROUTING BASED ON PATH PRIORITY
    if is_sofa_route:
        # Prioritize Collection
        product_details, page_type = check_collection()
        if not product_details:
            product_details, page_type = check_individual(requested_kind or "sofa")
    else:
        # Default or /product/ : Prioritize Individual
        product_details, page_type = check_individual(requested_kind)
        if not product_details:
            product_details, page_type = check_collection()

    if not product_details:
        from mysite.www.mysite.controllers.sofa_details import get_sofa_unit_details
        product_details = get_sofa_unit_details(model_name, price_list_param)
        if product_details: page_type = 'sofadetails'

    if not product_details:
        frappe.throw(f"محصول {model_name} یافت نشد", frappe.DoesNotExistError)

    # Attach current attributes and set display name
    if page_type in ['sofadetails', 'chairdetails', 'barstooldetails', 'tabledetails', 'benchdetails', 'product']:
        _enrich_product_variant_metadata(product_details)
        attrs = frappe.db.get_all("Item Variant Attribute", 
            filters={"parent": product_details.get("name") or product_details.get("item_code")}, 
            fields=["attribute", "attribute_value"]
        )
        product_details["attributes"] = {a.attribute: a.attribute_value for a in attrs}
        # Use 'مدل محصول' as the display name if available
        product_details["display_name"] = product_details["attributes"].get("مدل محصول") or product_details.get("name")
        resolved_item_code = _resolve_product_item_code(product_details)
        product_details["feature_rows"] = _get_management_feature_rows_for_item(resolved_item_code)

    # Normalize name for generic use
    if "name" not in product_details and "item_name" in product_details:
        product_details["name"] = product_details["item_name"]

    # Similar Products
    similar_products = get_similar_products(product_details, price_list_param)

    # ── Fetch Siblings/Variants for Dynamic Configuration ──────────
    # The dedicated controllers now return `selectable_attributes` and `variants` directly.
    # We no longer need to manually query the DB for siblings.
    selectable_attributes = product_details.get("selectable_attributes", [])
    siblings = product_details.get("variants", [])

    context.boot = {
        "ProductDetails": product_details,
        "ClothGroups": get_cloth_groups(price_list_param),
        "SimilarProducts": similar_products,
        "SelectedCustomer": selected_customer or "",
        "SelectedPriceList": price_list_param or "",
        "PriceSource": price_source,
        "BundlePrefill": requested_bundle if page_type == "sofacollectiondetails" else "",
        "PageType": page_type,
    }

    
    context.product_name = context.boot["ProductDetails"].get("name") or context.boot["ProductDetails"].get("item_name") or "محصول"
    context.page_type = page_type

    if page_type in {"sofadetails", "chairdetails", "barstooldetails", "tabledetails", "benchdetails", "product"}:
        tracked_model = (
            product_details.get("parent_model_name")
            or product_details.get("display_name")
            or product_details.get("name")
            or model_name
        )
        tracked_item = product_details.get("item_code") or product_details.get("name")
        _log_funnel_event_safely(
            step=FUNNEL_STEP_PRODUCT_VIEW,
            model_name=tracked_model,
            item_code=tracked_item,
            qty=1,
            amount=product_details.get("price") or 0,
            customer=selected_customer,
            request_path=path,
        )

    return context

def get_similar_products(product, price_list):
    """Fetch similar products based on category or type"""
    similar = []
    p_type = product.get("type")
    p_name = product.get("name") or product.get("item_name")

    if p_type in ["sofa", "sofa-collection", "sofa-unit"]:
        # Get other sofas
        from mysite.www.mysite.sofas import get_nested_sofa_products
        all_sofas = get_nested_sofa_products(price_list)
        similar = [s for s in all_sofas if s["sofa_model_name"] != p_name][:4]
        # Simplify for listing
        similar = [{
            "name": s["sofa_model_name"],
            "image": s["sofa_main_photo"],
            "price": 0, 
            "route": s["sofa_route"]
        } for s in similar]
    elif p_type in {"table", "coffee-table", "dining-table"}:
        from mysite.www.mysite.tables import get_chairs_by_type as get_tables
        from mysite.www.mysite.coffee_tables import get_related_items as get_coffee_tables

        all_tables = (get_tables("میز ناهارخوری", price_list) or []) + (
            get_coffee_tables(("میز جلومبلی", "میز عسلی", "باکس"), price_list) or []
        )
        similar = [c for c in all_tables if c.get("name") != p_name][:4]
        from urllib.parse import quote

        similar = [
            {
                "name": c["name"],
                "image": c["image"],
                "price": c["colors"][0]["variant"]["raw_price"] / 10 if c["colors"] else 0,
                "route": f"/mysite/product?name={quote(c['name'])}&kind=table",
            }
            for c in similar
        ]
    elif p_type == "bench":
        from mysite.www.mysite.benches import get_related_items
        all_benches = get_related_items(('نیمکت', 'پاف'), price_list)
        similar = [c for c in all_benches if c["name"] != p_name][:4]
        from urllib.parse import quote
        similar = [{
            "name": c["name"],
            "image": c["image"],
            "price": c["colors"][0]["variant"]["raw_price"] / 10 if c["colors"] else 0,
            "route": f"/mysite/product/{quote(c['name'])}"
        } for c in similar]
    elif p_type == "chair":
        from mysite.www.mysite.dining_chairs import get_chairs_by_type as get_chairs
        all_chairs = get_chairs("صندلی ناهارخوری", price_list)
        similar = [c for c in all_chairs if c["name"] != p_name][:4]
        from urllib.parse import quote
        similar = [{
            "name": c["name"],
            "image": c["image"],
            "price": c["colors"][0]["variant"]["raw_price"] / 10 if c["colors"] else 0,
            "route": f"/mysite/product/{quote(c['name'])}"
        } for c in similar]
    else:
        # Default: Barstools
        from mysite.www.mysite.barstools import get_chairs_by_type
        all_bars = get_chairs_by_type("صندلی اپن", price_list)
        similar = [c for c in all_bars if c.get("name") != p_name][:4]
        from urllib.parse import quote
        similar = [{
            "name": c["name"],
            "image": c["image"],
            "price": c["colors"][0]["variant"]["raw_price"] / 10 if c["colors"] else 0,
            "route": f"/mysite/product/{quote(c['name'])}"
        } for c in similar]
    
    return similar

@frappe.whitelist(allow_guest=True)
def submit_quotation_request(customer_info, items):
    """
    Submits a quotation request from the website.
    """
    import json
    if isinstance(customer_info, str):
        customer_info = json.loads(customer_info)
    if isinstance(items, str):
        items = json.loads(items)
        
    from mysite.mysite.doctype.quotation_request.quotation_request import resolve_or_create_customer

    customer = resolve_or_create_customer(
        customer_name=customer_info.get("name"),
        email=customer_info.get("email"),
        phone=customer_info.get("phone"),
    )

    # Create Quotation Request
    doc = frappe.get_doc({
        "doctype": "Quotation Request",
        "customer_name": customer_info.get("name"),
        "phone": customer_info.get("phone"),
        "email": customer_info.get("email"),
        "customer": customer,
        "status": "Submitted",
        "items": []
    })
    
    for item in items:
        doc.append("items", {
            "item_name": item.get("name"),
            "item_code": item.get("item_code"),
            "configuration": json.dumps(item.get("config")),
            "qty": item.get("qty", 1),
            "price": item.get("price", 0)
        })
    
    doc.insert(ignore_permissions=True)

    total_qty = 0
    total_amount = 0
    model_names = []
    for item in items:
        item_code = (item.get("item_code") or "").strip()
        item_name = item.get("name") or item.get("item_name") or item_code
        model_name = _resolve_model_name_for_item(item_code=item_code, fallback_name=item_name)
        if model_name and model_name not in model_names:
            model_names.append(model_name)
        total_qty += _to_int(item.get("qty"), default=1) or 1
        try:
            total_amount += float(item.get("price") or 0)
        except Exception:
            pass

    _log_funnel_event_safely(
        step=FUNNEL_STEP_ORDER_SUBMIT,
        model_name=model_names[0] if model_names else "",
        qty=total_qty,
        amount=total_amount,
        customer=customer_info.get("name") or customer,
        quotation_name=doc.name,
        extra={
            "models": model_names,
            "items_count": len(items),
            "source": "website_guest",
        },
    )

    frappe.db.commit()
    
    return {"status": "success", "name": doc.name, "customer": customer}

@frappe.whitelist(allow_guest=True)
def search_everything(query, customer=None):
    """Global search across products, collections, blog posts, projects and gallery."""
    raw_query = (query or "").strip()
    if len(raw_query) < 2:
        return {"items": [], "models": [], "posts": [], "projects": [], "gallery": [], "pages": []}

    requested_customer = (customer or frappe.form_dict.get("customer") or "").strip()
    selected_customer, selected_price_list, _ = _resolve_customer_price_context(requested_customer)
    like_query = f"%{raw_query}%"
    normalized_query = " ".join(raw_query.replace("\u200c", " ").lower().split())

    def _append_customer(route):
        if not route:
            return route
        if not selected_customer:
            return route
        if "customer=" in route:
            return route
        joiner = "&" if "?" in route else "?"
        return f"{route}{joiner}customer={quote(selected_customer)}"

    def _guess_item_kind(item_row):
        raw = " ".join([
            str(item_row.get("model_name") or ""),
            str(item_row.get("variant_of") or ""),
            str(item_row.get("item_name") or ""),
            str(item_row.get("item_code") or ""),
            str(item_row.get("item_group") or ""),
            str(item_row.get("description") or ""),
        ])
        raw = raw.lower()
        if any(token in raw for token in ("صندلی اپن", "اپن", "بار", "barstool", "bar stool", "counter stool")):
            return "barstool"
        if any(token in raw for token in ("نیمکت", "پاف", "bench", "ottoman")):
            return "bench"
        if any(token in raw for token in ("جلومبلی", "عسلی", "میز", "table", "coffee table", "side table", "dining table")):
            return "table"
        if any(token in raw for token in ("صندلی ناهارخوری", "dining chair", "chair")) and "barstool" not in raw and "counter stool" not in raw:
            return "chair"
        if any(token in raw for token in ("مبل", "کاناپه", "sofa", "sectional", "loveseat")):
            return "sofa"
        return "sofa"

    def _normalize_model_key(value):
        return " ".join(str(value or "").replace("\u200c", " ").split()).strip().lower()

    def _resolve_model_name_for_search_row(item_row, model_by_item, template_name_by_item=None):
        item_name = str(item_row.get("name") or "").strip()
        model_name = str(model_by_item.get(item_name) or "").strip()
        if model_name:
            return model_name
        variant_of = str(item_row.get("variant_of") or "").strip()
        variant_model_name = str(model_by_item.get(variant_of) or "").strip()
        if variant_model_name:
            return variant_model_name
        if variant_of and isinstance(template_name_by_item, dict):
            template_item_name = str(template_name_by_item.get(variant_of) or "").strip()
            if template_item_name:
                return template_item_name
        fallback_name = str(item_row.get("item_name") or item_row.get("item_code") or item_name).strip()
        return fallback_name

    def _build_product_route_by_model(model_name, kind):
        clean_model = str(model_name or "").strip()
        if not clean_model:
            return ""
        base_route = f"/mysite/product?name={quote(clean_model)}"
        if kind:
            base_route = f"{base_route}&kind={quote(kind)}"
        return _append_customer(base_route)

    def _collect_model_metadata(item_rows):
        item_names = []
        template_names = []
        for row in item_rows or []:
            row_name = str((row.get("name") if isinstance(row, dict) else getattr(row, "name", "")) or "").strip()
            if row_name:
                item_names.append(row_name)
            variant_of = str((row.get("variant_of") if isinstance(row, dict) else getattr(row, "variant_of", "")) or "").strip()
            if variant_of:
                template_names.append(variant_of)

        lookup_names = sorted({name for name in item_names + template_names if name})
        model_by_item = {}
        if lookup_names and frappe.db.exists("DocType", "Item Variant Attribute"):
            model_attr_rows = frappe.get_all(
                "Item Variant Attribute",
                filters={"parent": ["in", lookup_names], "attribute": "مدل محصول"},
                fields=["parent", "attribute_value"],
                limit_page_length=0,
                ignore_permissions=True,
            )
            for row in model_attr_rows:
                parent = str(row.get("parent") or "").strip()
                value = str(row.get("attribute_value") or "").strip()
                if parent and value:
                    model_by_item[parent] = value

        template_name_by_item = {}
        template_unique = sorted({name for name in template_names if name})
        if template_unique:
            try:
                template_rows = frappe.get_all(
                    "Item",
                    filters={"name": ["in", template_unique]},
                    fields=["name", "item_name"],
                    limit_page_length=0,
                    ignore_permissions=True,
                )
            except Exception:
                template_rows = []
            for row in template_rows:
                template_key = str(row.get("name") or "").strip()
                template_title = str(row.get("item_name") or "").strip()
                if template_key and template_title:
                    template_name_by_item[template_key] = template_title

        return model_by_item, template_name_by_item

    def _to_toman(rial_value):
        try:
            amount = float(rial_value or 0)
        except Exception:
            return 0
        if amount <= 0:
            return 0
        return int(amount / 10)

    def _safe_text(value):
        return frappe.utils.strip_html(str(value or "")).strip()

    def _dedupe_rows(rows, key_field):
        seen = set()
        result = []
        for row in rows or []:
            key = str(row.get(key_field) or "").strip()
            if not key:
                continue
            if key in seen:
                continue
            seen.add(key)
            result.append(row)
        return result

    def _contains_any(source_text, tokens):
        source = str(source_text or "").strip().lower()
        if not source:
            return False
        return any(str(token or "").strip().lower() in source for token in tokens)

    sofa_intent_tokens = (
        "مبل",
        "مبلمان",
        "کاناپه",
        "sofa",
        "couch",
        "sectional",
    )
    bench_intent_tokens = (
        "نیمکت",
        "پاف",
        "bench",
        "ottoman",
    )
    table_intent_tokens = (
        "میز",
        "ناهارخوری",
        "جلومبلی",
        "عسلی",
        "coffee table",
        "dining table",
        "side table",
        "table",
    )
    is_sofa_intent = _contains_any(normalized_query, sofa_intent_tokens) and not _contains_any(
        normalized_query,
        ("میز", "جلومبلی", "عسلی", "table"),
    )
    is_bench_intent = _contains_any(normalized_query, bench_intent_tokens)
    is_table_intent = _contains_any(normalized_query, table_intent_tokens)
    is_sofa_generic_query = normalized_query in {"مبل", "مبلمان", "کاناپه", "sofa", "couch"}
    is_bench_generic_query = normalized_query in {"نیمکت", "پاف", "bench", "ottoman"}
    is_table_generic_query = normalized_query in {
        "میز",
        "table",
        "tables",
        "میزها",
    }

    def _extract_module_cover_image(mod):
        module_images = mod.get("sofa_module_images") or []
        if isinstance(module_images, list):
            for image_row in module_images:
                if not isinstance(image_row, dict):
                    continue
                image_url = _normalize_file_url(image_row.get("file_url"))
                if image_url:
                    return image_url
        module_items = mod.get("sofa_module_items") or []
        if isinstance(module_items, list) and module_items:
            first_item = module_items[0] or {}
            nested_images = first_item.get("images") or []
            if isinstance(nested_images, list):
                for image_row in nested_images:
                    if not isinstance(image_row, dict):
                        continue
                    image_url = _normalize_file_url(image_row.get("file_url"))
                    if image_url:
                        return image_url
            direct_image = _normalize_file_url(first_item.get("image"))
            if direct_image:
                return direct_image
        return ""

    def _extract_module_price(mod):
        prices = []
        for item in mod.get("sofa_module_items") or []:
            try:
                price_toman = int(float(item.get("Price") or 0))
            except Exception:
                price_toman = 0
            if price_toman > 0:
                prices.append(price_toman)
        return max(prices) if prices else 0

    def _build_sofa_module_bundle_items():
        rows = []
        try:
            nested_products = get_nested_sofa_products(selected_price_list) or []
        except Exception:
            nested_products = []

        for model in nested_products:
            if not isinstance(model, dict):
                continue
            model_name = str(model.get("sofa_model_name") or "").strip()
            model_desc = _safe_text(model.get("sofa_model_description"))
            model_match = _contains_any(
                f"{model_name} {model_desc}",
                (normalized_query,),
            )

            for mod in model.get("sofa_modules") or []:
                if not isinstance(mod, dict):
                    continue
                module_name = str(mod.get("sofa_module_name") or "").strip()
                module_type = str(mod.get("sofa_module_type") or "").strip()
                module_items = mod.get("sofa_module_items") or []
                first_item = module_items[0] if isinstance(module_items, list) and module_items else {}
                first_item_name = str((first_item or {}).get("item_name") or "").strip()
                if not first_item_name:
                    first_item_name = f"{model_name} {module_name}".strip()
                route = _append_customer(f"/mysite/product?name={quote(first_item_name)}&kind=sofa")
                module_haystack = " ".join(
                    [
                        model_name,
                        module_name,
                        module_type,
                        str((first_item or {}).get("display_name") or ""),
                        str((first_item or {}).get("variant_of") or ""),
                    ]
                )
                module_match = _contains_any(module_haystack, (normalized_query,))
                if not (is_sofa_generic_query or model_match or module_match):
                    continue
                module_key = f"sofa-module::{_normalize_model_key(model_name)}::{_normalize_model_key(module_name)}"
                rows.append(
                    {
                        "name": module_name or model_name or "ماژول مبلمان",
                        "item_name": module_name or model_name or "ماژول مبلمان",
                        "item_group": "ماژول مبلمان",
                        "kind": "sofa",
                        "image": _extract_module_cover_image(mod),
                        "base_price": _extract_module_price(mod),
                        "summary": model_desc or module_type or "",
                        "variant_count": len(module_items) if isinstance(module_items, list) else 1,
                        "route": route,
                        "_grouped_key": module_key,
                    }
                )

            for bundle in model.get("sofa_bundles") or []:
                if not isinstance(bundle, dict):
                    continue
                bundle_name = str(bundle.get("bundle_name") or "").strip()
                display_name = str(bundle.get("sofa_bundle_display_name") or bundle.get("name") or "").strip()
                if not bundle_name or not display_name:
                    continue
                bundle_haystack = " ".join(
                    [
                        model_name,
                        display_name,
                        str(bundle.get("sofa_bundle_name") or ""),
                        str(bundle.get("description") or ""),
                    ]
                )
                bundle_match = _contains_any(bundle_haystack, (normalized_query,))
                if not (is_sofa_generic_query or model_match or bundle_match):
                    continue
                route = _append_customer(f"/mysite/sofas/{quote(model_name)}?bundle={quote(bundle_name)}")
                bundle_key = f"sofa-bundle::{_normalize_model_key(model_name)}::{_normalize_model_key(bundle_name)}"
                rows.append(
                    {
                        "name": display_name,
                        "item_name": display_name,
                        "item_group": "بسته مبلمان",
                        "kind": "sofa",
                        "image": _normalize_file_url(bundle.get("bundle_cover_photo")),
                        "base_price": int(bundle.get("bundle_price") or 0),
                        "summary": model_desc or "",
                        "variant_count": 1,
                        "route": route,
                        "_grouped_key": bundle_key,
                    }
                )

        rows = _dedupe_rows(rows, "route")
        return rows[:16]

    def _build_bench_model_items():
        rows = []
        try:
            from mysite.www.mysite.benches import get_related_items as _get_bench_related_items
            bench_models = _get_bench_related_items(("نیمکت", "پاف"), selected_price_list) or []
        except Exception:
            bench_models = []

        for model in bench_models:
            if not isinstance(model, dict):
                continue
            model_name = str(model.get("name") or model.get("display_name") or "").strip()
            if not model_name:
                continue
            model_match = _contains_any(model_name, (normalized_query,))
            if not (is_bench_generic_query or model_match):
                continue

            min_price_rial = 0
            for color in model.get("colors") or []:
                if not isinstance(color, dict):
                    continue
                variant = color.get("variant") or {}
                raw_price = int(variant.get("raw_price") or 0)
                if raw_price <= 0:
                    continue
                if min_price_rial == 0 or raw_price < min_price_rial:
                    min_price_rial = raw_price

            route = _append_customer(f"/mysite/product?name={quote(model_name)}&kind=bench")
            summary_bits = []
            if model.get("length"):
                summary_bits.append(str(model.get("length")))
            if model.get("width"):
                summary_bits.append(str(model.get("width")))
            if model.get("shape"):
                summary_bits.append(str(model.get("shape")))
            rows.append(
                {
                    "name": model_name,
                    "item_name": model_name,
                    "item_group": "نیمکت و پاف",
                    "kind": "bench",
                    "image": _normalize_file_url(model.get("image")),
                    "base_price": _to_toman(min_price_rial),
                    "summary": " - ".join(summary_bits),
                    "variant_count": len(model.get("colors") or []),
                    "route": route,
                    "_grouped_key": f"bench-model::{_normalize_model_key(model_name)}",
                }
            )

        rows = _dedupe_rows(rows, "route")
        return rows[:10]

    def _extract_model_min_price_toman(model):
        min_price_rial = 0
        for color in model.get("colors") or []:
            if not isinstance(color, dict):
                continue
            variant = color.get("variant") or {}
            try:
                raw_price = int(float(variant.get("raw_price") or 0))
            except Exception:
                raw_price = 0
            if raw_price <= 0:
                continue
            if min_price_rial == 0 or raw_price < min_price_rial:
                min_price_rial = raw_price
        return _to_toman(min_price_rial)

    def _build_table_model_items():
        rows = []
        table_models = []

        try:
            from mysite.www.mysite.tables import get_chairs_by_type as _get_dining_tables

            table_models.extend(_get_dining_tables("میز ناهارخوری", selected_price_list) or [])
        except Exception:
            pass

        try:
            from mysite.www.mysite.coffee_tables import get_related_items as _get_coffee_tables

            table_models.extend(_get_coffee_tables(("میز جلومبلی", "میز عسلی", "باکس"), selected_price_list) or [])
        except Exception:
            pass

        for model in table_models:
            if not isinstance(model, dict):
                continue
            model_name = str(model.get("name") or model.get("display_name") or "").strip()
            if not model_name:
                continue

            haystack_bits = [
                model_name,
                str(model.get("display_name") or ""),
                str(model.get("shape") or ""),
                str(model.get("length") or ""),
                str(model.get("width") or ""),
            ]
            model_match = _contains_any(" ".join(haystack_bits), (normalized_query,))
            if not (is_table_generic_query or model_match):
                continue

            model_name_lc = model_name.lower()
            if "ناهارخوری" in model_name_lc:
                table_group = "میز ناهارخوری"
            elif "جلومبلی" in model_name_lc or "عسلی" in model_name_lc:
                table_group = "میز جلومبلی و عسلی"
            else:
                table_group = "میز"

            summary_bits = []
            if model.get("shape"):
                summary_bits.append(str(model.get("shape")))
            if model.get("length"):
                summary_bits.append(str(model.get("length")))
            if model.get("width"):
                summary_bits.append(str(model.get("width")))

            rows.append(
                {
                    "name": model_name,
                    "item_name": model_name,
                    "item_group": table_group,
                    "kind": "table",
                    "image": _normalize_file_url(model.get("image")),
                    "base_price": _extract_model_min_price_toman(model),
                    "summary": " - ".join(summary_bits),
                    "variant_count": len(model.get("colors") or []),
                    "route": _append_customer(f"/mysite/product?name={quote(model_name)}&kind=table"),
                    "_grouped_key": f"table-model::{_normalize_model_key(model_name)}",
                }
            )

        rows = _dedupe_rows(rows, "route")
        return rows[:14]

    # 1) Product Items
    raw_item_rows = frappe.db.sql(
        """
        SELECT
            i.name,
            i.item_code,
            i.item_name,
            i.image,
            i.item_group,
            i.variant_of,
            i.description,
            COALESCE(ip.price_list_rate, 0) as price_list_rate
        FROM `tabItem` i
        LEFT JOIN (
            SELECT item_code, MAX(price_list_rate) as price_list_rate
            FROM `tabItem Price`
            WHERE price_list = %(price_list)s
            GROUP BY item_code
        ) ip
          ON i.name = ip.item_code
        WHERE i.show_on_site = 1
          AND i.disabled = 0
          AND i.is_stock_item = 1
          AND (
                i.item_name LIKE %(query)s
             OR i.item_code LIKE %(query)s
             OR i.description LIKE %(query)s
          )
        ORDER BY i.modified DESC
        LIMIT 120
        """,
        {"query": like_query, "price_list": selected_price_list or ""},
        as_dict=True,
    )

    item_model_by_name, template_item_name_by_item = _collect_model_metadata(raw_item_rows)

    grouped_items = {}
    for row in raw_item_rows:
        model_name = _resolve_model_name_for_search_row(row, item_model_by_name, template_item_name_by_item)
        model_key = _normalize_model_key(model_name)
        if not model_key:
            continue

        row["model_name"] = model_name
        row["kind"] = _guess_item_kind(row)
        grouped_key = f"{str(row.get('kind') or 'sofa').strip().lower()}::{model_key}"
        row["base_price"] = _to_toman(row.get("price_list_rate"))
        row["summary"] = _safe_text(row.get("description"))

        bucket = grouped_items.get(grouped_key)
        if not bucket:
            bucket = {
                "name": model_name,
                "item_name": model_name,
                "item_group": row.get("item_group") or "محصول",
                "kind": row.get("kind") or "",
                "image": _normalize_file_url(row.get("image")),
                "base_price": row.get("base_price") or 0,
                "summary": row.get("summary") or "",
                "variant_count": 0,
                "_kind_count": {},
                "_grouped_key": grouped_key,
            }
            grouped_items[grouped_key] = bucket

        bucket["variant_count"] += 1
        row_kind = str(row.get("kind") or "").strip().lower() or "sofa"
        kind_counter = bucket.get("_kind_count") or {}
        kind_counter[row_kind] = int(kind_counter.get(row_kind) or 0) + 1
        bucket["_kind_count"] = kind_counter
        if not bucket.get("image") and row.get("image"):
            bucket["image"] = _normalize_file_url(row.get("image"))
        if not bucket.get("summary") and row.get("summary"):
            bucket["summary"] = row.get("summary")
        if not bucket.get("item_group") and row.get("item_group"):
            bucket["item_group"] = row.get("item_group")
        if not bucket.get("kind") and row.get("kind"):
            bucket["kind"] = row.get("kind")

        current_price = bucket.get("base_price") or 0
        next_price = row.get("base_price") or 0
        if next_price and (not current_price or next_price < current_price):
            bucket["base_price"] = next_price

    model_items = list(grouped_items.values())
    for row in model_items:
        kind_count = row.get("_kind_count") if isinstance(row.get("_kind_count"), dict) else {}
        if kind_count:
            row["kind"] = max(
                kind_count.keys(),
                key=lambda key: (
                    int(kind_count.get(key) or 0),
                    1 if key in {"barstool", "chair", "bench", "table"} else 0,
                ),
            )
        row["route"] = _build_product_route_by_model(row.get("item_name"), row.get("kind"))
        row.pop("_kind_count", None)
    model_items = model_items[:12]

    has_table_model_hits = any(str(row.get("kind") or "").strip().lower() == "table" for row in model_items)

    intent_sofa_items = []
    intent_bench_items = []
    intent_table_items = []

    if is_sofa_intent:
        intent_sofa_items = _build_sofa_module_bundle_items()
    if is_bench_intent:
        intent_bench_items = _build_bench_model_items()
    if is_table_intent or has_table_model_hits:
        intent_table_items = _build_table_model_items()

    intent_items = intent_sofa_items + intent_bench_items + intent_table_items

    if is_sofa_generic_query:
        items = intent_sofa_items if intent_sofa_items else model_items[:8]
    elif is_table_generic_query:
        table_only = [row for row in model_items if str(row.get("kind") or "").strip().lower() == "table"]
        items = intent_table_items if intent_table_items else table_only[:10]
    elif is_bench_generic_query:
        bench_only = [row for row in model_items if str(row.get("kind") or "").strip().lower() == "bench"]
        items = intent_bench_items if intent_bench_items else bench_only[:8]
    else:
        model_items_without_table = (
            [row for row in model_items if str(row.get("kind") or "").strip().lower() != "table"]
            if intent_table_items
            else model_items
        )
        items = intent_items + model_items_without_table

    items = _dedupe_rows(items, "route")
    items = items[:20]

    # 2) Sofa Collections (Sofa Model)
    models = []
    if frappe.db.exists("DocType", "Sofa Model"):
        try:
            models = frappe.get_all(
                "Sofa Model",
                filters={"sofa_model_name": ["like", like_query]},
                fields=["name", "sofa_model_name", "sofa_main_photo", "sofa_route", "description"],
                order_by="modified desc",
                limit_page_length=8,
            )
            for row in models:
                route = f"/mysite/{str(row.get('sofa_route') or '').lstrip('/')}"
                row["route"] = _append_customer(route)
                row["summary"] = _safe_text(row.get("description"))
        except Exception:
            models = []
    models = _dedupe_rows(models, "name")

    # 3) Blog Posts
    posts = []
    try:
        meta = frappe.get_meta("Blog Post")
        available_fields = {f.fieldname for f in meta.fields}
        fields = ["name", "title", "route", "meta_image"]
        if "blog_intro" in available_fields:
            fields.append("blog_intro")
        if "content" in available_fields:
            fields.append("content")
        if "blog_category" in available_fields:
            fields.append("blog_category")
        if "published_on" in available_fields:
            fields.append("published_on")

        filters = {"published": 1}
        or_filters = {"title": ["like", like_query]}
        if "blog_intro" in available_fields:
            or_filters["blog_intro"] = ["like", like_query]
        if "content" in available_fields:
            or_filters["content"] = ["like", like_query]

        posts = frappe.get_all(
            "Blog Post",
            filters=filters,
            or_filters=or_filters,
            fields=fields,
            order_by="published_on desc, modified desc",
            limit_page_length=8,
        )
        for row in posts:
            post_name = str(row.get("name") or "").strip()
            route = f"/mysite/blog?post={quote(post_name)}" if post_name else "/mysite/blog"
            row["route"] = route
            row["summary"] = _safe_text(row.get("blog_intro") or row.get("content"))
    except Exception:
        posts = []
    posts = _dedupe_rows(posts, "name")

    # 4) Customer Projects
    projects = []
    try:
        projects = frappe.get_all(
            "Customer Project",
            filters={"is_published": 1},
            or_filters={
                "title": ["like", like_query],
                "short_description": ["like", like_query],
                "location": ["like", like_query],
                "customer_name": ["like", like_query],
            },
            fields=[
                "name",
                "title",
                "project_type",
                "project_type_custom",
                "cover_image",
                "short_description",
                "location",
            ],
            order_by="sort_order asc, modified desc",
            limit_page_length=8,
        )
        for row in projects:
            project_type = (row.get("project_type_custom") or "").strip() if row.get("project_type") == "سایر" else row.get("project_type")
            row["project_type_label"] = project_type or "پروژه"
            row["image"] = row.get("cover_image") or ""
            row["route"] = _append_customer(f"/mysite/project?name={quote(str(row.get('name') or ''))}")
            row["summary"] = _safe_text(row.get("short_description"))
    except Exception:
        projects = []
    projects = _dedupe_rows(projects, "name")

    # 5) Gallery-like results (search in image-rich items)
    gallery = []
    gallery_items = frappe.get_all(
        "Item",
        filters={"show_on_site": 1, "disabled": 0, "is_stock_item": 1},
        or_filters={
            "item_name": ["like", like_query],
            "description": ["like", like_query],
            "item_group": ["like", like_query],
        },
        fields=["name", "item_name", "item_code", "item_group", "description", "image", "variant_of"],
        order_by="modified desc",
        limit_page_length=8,
    )

    item_names = [row.name for row in gallery_items]
    image_by_item = {}
    price_by_item = {}
    if item_names:
        placeholders = ", ".join(["%s"] * len(item_names))
        files = frappe.db.sql(
            f"""
            SELECT attached_to_name, file_url
            FROM `tabFile`
            WHERE attached_to_doctype = 'Item'
              AND attached_to_name IN ({placeholders})
              AND is_private = 0
              AND (
                   file_url LIKE '%%.jpg'
                OR file_url LIKE '%%.jpeg'
                OR file_url LIKE '%%.png'
                OR file_url LIKE '%%.webp'
              )
            ORDER BY creation ASC
            """,
            tuple(item_names),
            as_dict=True,
        )
        for file_row in files:
            image_by_item.setdefault(file_row.attached_to_name, file_row.file_url)
        item_prices = frappe.get_all(
            "Item Price",
            filters={
                "price_list": selected_price_list,
                "item_code": ["in", item_names],
            },
            fields=["item_code", "price_list_rate"],
            limit_page_length=0,
        )
        for price_row in item_prices:
            code = price_row.get("item_code")
            if code and code not in price_by_item:
                price_by_item[code] = price_row.get("price_list_rate") or 0

    gallery_model_by_name, gallery_template_name_by_item = _collect_model_metadata(gallery_items)
    product_model_keys = set(grouped_items.keys())
    for row in gallery_items:
        kind = _guess_item_kind(row)
        model_name = _resolve_model_name_for_search_row(row, gallery_model_by_name, gallery_template_name_by_item)
        model_key = _normalize_model_key(model_name)
        grouped_key = f"{str(kind or 'sofa').strip().lower()}::{model_key}"
        route = _build_product_route_by_model(model_name, kind)
        gallery.append(
            {
                "name": row.get("name"),
                "title": row.get("item_name") or row.get("item_code") or row.get("name"),
                "image": image_by_item.get(row.get("name")) or row.get("image") or "",
                "category": row.get("item_group") or "",
                "base_price": _to_toman(price_by_item.get(row.get("name"))),
                "route": route,
                "summary": _safe_text(row.get("description")),
                "model_key": grouped_key,
            }
        )
    gallery = _dedupe_rows(gallery, "model_key")
    gallery = [row for row in gallery if str(row.get("model_key") or "") not in product_model_keys]
    for row in gallery:
        row.pop("model_key", None)

    # 6) Website Pages
    pages = []
    query_text = raw_query.lower()
    static_pages = [
        {"name": "home", "title": "صفحه اصلی", "route": "/mysite", "keywords": "خانه اصلی دنروم"},
        {"name": "products", "title": "محصولات", "route": "/mysite/products", "keywords": "فروشگاه کالا"},
        {"name": "sofas", "title": "مبلمان", "route": "/mysite/sofas", "keywords": "کالکشن مبلمان مبل کاناپه ماژول بسته"},
        {"name": "benches", "title": "نیمکت و پاف", "route": "/mysite/benches", "keywords": "نیمکت پاف bench ottoman"},
        {"name": "fabrics", "title": "پارچه‌ها", "route": "/mysite/fabrics", "keywords": "کالیته پارچه رنگ پارچه"},
        {"name": "shop-by-look", "title": "Shop by Look", "route": "/mysite/shop-by-look", "keywords": "فوتو گالری صحنه"},
        {"name": "faq", "title": "سوالات متداول", "route": "/mysite/faq", "keywords": "پرسش پاسخ faq"},
        {"name": "projects", "title": "پروژه‌ها", "route": "/mysite/projects", "keywords": "نمونه کار پروژه مشتری"},
        {"name": "gallery", "title": "فوتوگالری", "route": "/mysite/gallery", "keywords": "گالری عکس"},
        {"name": "blog", "title": "بلاگ", "route": "/mysite/blog", "keywords": "مقاله مجله"},
        {"name": "saved-products", "title": "محصولات ذخیره‌شده", "route": "/mysite/saved-products", "keywords": "علاقه‌مندی"},
    ]
    for page in static_pages:
        haystack = f"{page.get('title', '')} {page.get('keywords', '')}".lower()
        if query_text in haystack:
            pages.append(
                {
                    "name": page.get("name"),
                    "title": page.get("title"),
                    "route": _append_customer(page.get("route")),
                    "summary": page.get("keywords", ""),
                }
            )

    if frappe.db.exists("DocType", "Web Page"):
        try:
            web_pages = frappe.get_all(
                "Web Page",
                filters={"published": 1, "title": ["like", like_query]},
                fields=["name", "title", "route", "meta_description"],
                order_by="modified desc",
                limit_page_length=10,
            )
            for row in web_pages:
                route = "/" + str(row.get("route") or "").lstrip("/")
                pages.append(
                    {
                        "name": row.get("name"),
                        "title": row.get("title") or row.get("name"),
                        "route": _append_customer(route),
                        "summary": _safe_text(row.get("meta_description")),
                    }
                )
        except Exception:
            pass
    pages = _dedupe_rows(pages, "route")

    return {
        "items": items,
        "models": models,
        "posts": posts,
        "projects": projects,
        "gallery": gallery,
        "pages": pages,
        "selected_customer": selected_customer or "",
        "selected_price_list": selected_price_list or "",
    }


def _clean_feedback_text(value):
    cleaned = frappe.utils.strip_html(str(value or "")).strip()
    return " ".join(cleaned.split())


def _to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _resolve_model_item_codes(model_name=None, item_code=None):
    model_name = (model_name or "").strip()
    item_code = (item_code or "").strip()

    found_codes = []

    def _add(code):
        code = (code or "").strip()
        if code and code not in found_codes:
            found_codes.append(code)

    if model_name:
        model_rows = frappe.get_all(
            "Item Variant Attribute",
            filters={"attribute": "مدل محصول", "attribute_value": model_name},
            fields=["parent"],
            limit_page_length=0,
            ignore_permissions=True,
        )
        for row in model_rows:
            _add(row.get("parent"))

    base_code = ""
    if item_code and frappe.db.exists("Item", item_code):
        base_code = item_code
    elif found_codes:
        base_code = found_codes[0]

    if base_code:
        _add(base_code)
        template_code = frappe.db.get_value("Item", base_code, "variant_of")
        if template_code:
            _add(template_code)
            sibling_rows = frappe.get_all(
                "Item",
                filters={"variant_of": template_code},
                fields=["name"],
                limit_page_length=0,
                ignore_permissions=True,
            )
            for row in sibling_rows:
                _add(row.get("name"))
    elif model_name and frappe.db.exists("Item", model_name):
        _add(model_name)

    return found_codes


def _extract_feedback(rows, feedback_type):
    reviews = []
    questions = []
    answers_by_question = {}

    for row in rows or []:
        subject = str(row.get("subject") or "").strip()
        content = _clean_feedback_text(row.get("content"))
        if not content:
            continue

        base_payload = {
            "id": row.get("name"),
            "author": (row.get("comment_by") or row.get("comment_email") or "کاربر").strip(),
            "date": row.get("creation"),
            "content": content,
        }

        if subject.startswith(FEEDBACK_REVIEW_PREFIX):
            rating = _to_int(subject.replace(FEEDBACK_REVIEW_PREFIX, "", 1), default=0)
            rating = max(1, min(5, rating))
            base_payload["rating"] = rating
            reviews.append(base_payload)
            continue

        if subject.startswith(FEEDBACK_QUESTION_PREFIX):
            questions.append(base_payload)
            continue

        if subject.startswith(FEEDBACK_ANSWER_PREFIX):
            question_id = subject.replace(FEEDBACK_ANSWER_PREFIX, "", 1).strip()
            if question_id and question_id not in answers_by_question:
                answers_by_question[question_id] = content

    for question in questions:
        question["answer"] = answers_by_question.get(question.get("id"))

    if feedback_type == "question":
        return questions
    return reviews


def _get_feedback_rows(item_codes, feedback_type, max_limit):
    base_filters = {
        "reference_doctype": "Item",
        "reference_name": ["in", item_codes],
        "comment_type": "Comment",
    }
    fields = ["name", "subject", "content", "comment_by", "comment_email", "creation"]

    if feedback_type == "review":
        review_filters = {**base_filters, "subject": ["like", f"{FEEDBACK_REVIEW_PREFIX}%"]}
        rows = frappe.get_all(
            "Comment",
            filters=review_filters,
            fields=fields,
            order_by="creation desc",
            limit_page_length=max_limit,
            ignore_permissions=True,
        )
        return rows, frappe.db.count("Comment", filters=review_filters)

    question_filters = {**base_filters, "subject": ["like", f"{FEEDBACK_QUESTION_PREFIX}%"]}
    question_rows = frappe.get_all(
        "Comment",
        filters=question_filters,
        fields=fields,
        order_by="creation desc",
        limit_page_length=max_limit,
        ignore_permissions=True,
    )
    total_questions = frappe.db.count("Comment", filters=question_filters)

    if not question_rows:
        return [], total_questions

    answer_subjects = [
        f"{FEEDBACK_ANSWER_PREFIX}{row.get('name')}"
        for row in question_rows
        if row.get("name")
    ]
    if not answer_subjects:
        return question_rows, total_questions

    answer_rows = frappe.get_all(
        "Comment",
        filters={**base_filters, "subject": ["in", answer_subjects]},
        fields=fields,
        order_by="creation desc",
        limit_page_length=len(answer_subjects),
        ignore_permissions=True,
    )
    return question_rows + answer_rows, total_questions


@frappe.whitelist(allow_guest=True)
def get_product_feedback(feedback_type="review", model_name=None, item_code=None, limit=50):
    feedback_type = (feedback_type or "review").strip().lower()
    if feedback_type not in {"review", "question"}:
        frappe.throw("نوع بازخورد نامعتبر است.")

    try:
        max_limit = min(max(_to_int(limit, default=50), 1), 150)
    except Exception:
        max_limit = 50

    item_codes = _resolve_model_item_codes(model_name=model_name, item_code=item_code)
    if not item_codes:
        return {"items": [], "stats": {"count": 0, "avg_rating": 0}}

    rows, total_count = _get_feedback_rows(
        item_codes=item_codes,
        feedback_type=feedback_type,
        max_limit=max_limit,
    )

    parsed = _extract_feedback(rows, feedback_type=feedback_type)
    if feedback_type == "review":
        ratings = [max(1, min(5, _to_int(row.get("rating"), default=0))) for row in parsed if row.get("rating")]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
    else:
        avg_rating = 0

    return {
        "items": parsed,
        "stats": {
            "count": total_count,
            "avg_rating": avg_rating,
        },
    }


@frappe.whitelist(allow_guest=True)
def submit_product_feedback(
    feedback_type="review",
    model_name=None,
    item_code=None,
    content=None,
    rating=None,
    author_name=None,
    author_email=None,
):
    payload = frappe.parse_json(frappe.request.data) if getattr(frappe, "request", None) and frappe.request.data else {}
    if payload:
        feedback_type = payload.get("feedback_type", feedback_type)
        model_name = payload.get("model_name", model_name)
        item_code = payload.get("item_code", item_code)
        content = payload.get("content", content)
        rating = payload.get("rating", rating)
        author_name = payload.get("author_name", author_name)
        author_email = payload.get("author_email", author_email)

    feedback_type = (feedback_type or "review").strip().lower()
    if feedback_type not in {"review", "question"}:
        frappe.throw("نوع بازخورد نامعتبر است.")

    cleaned_content = _clean_feedback_text(content)
    if len(cleaned_content) < 3:
        frappe.throw("متن وارد شده بسیار کوتاه است.")
    if len(cleaned_content) > 1200:
        frappe.throw("متن وارد شده بیش از حد طولانی است.")

    cleaned_name = _clean_feedback_text(author_name)[:120] if author_name else ""
    cleaned_email = _clean_feedback_text(author_email)[:140] if author_email else ""
    if cleaned_email:
        cleaned_email = frappe.utils.validate_email_address(cleaned_email, throw=True)

    numeric_rating = 0
    if feedback_type == "review":
        numeric_rating = max(1, min(5, _to_int(rating, default=0)))
        if not numeric_rating:
            frappe.throw("امتیاز دیدگاه باید بین ۱ تا ۵ باشد.")

    item_codes = _resolve_model_item_codes(model_name=model_name, item_code=item_code)
    if not item_codes:
        frappe.throw("محصول مرتبط با بازخورد پیدا نشد.")

    reference_name = ""
    if item_code and item_code in item_codes:
        reference_name = item_code
    else:
        reference_name = item_codes[0]

    subject = (
        f"{FEEDBACK_REVIEW_PREFIX}{numeric_rating}"
        if feedback_type == "review"
        else FEEDBACK_QUESTION_PREFIX
    )

    comment_doc = frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": "Item",
            "reference_name": reference_name,
            "subject": subject,
            "content": cleaned_content,
            "comment_by": cleaned_name or frappe.session.user_fullname or "کاربر مهمان",
            "comment_email": cleaned_email or "",
            "published": 1,
        }
    )
    comment_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "ok": True,
        "id": comment_doc.name,
        "feedback_type": feedback_type,
    }


@frappe.whitelist(allow_guest=True)
def track_funnel_event(
    step=None,
    model_name=None,
    item_code=None,
    qty=None,
    amount=None,
    session_id=None,
    customer=None,
):
    payload = frappe.parse_json(frappe.request.data) if getattr(frappe, "request", None) and frappe.request.data else {}
    if payload:
        step = payload.get("step", step)
        model_name = payload.get("model_name", model_name)
        item_code = payload.get("item_code", item_code)
        qty = payload.get("qty", qty)
        amount = payload.get("amount", amount)
        session_id = payload.get("session_id", session_id)
        customer = payload.get("customer", customer)

    normalized_step = (step or "").strip()
    if normalized_step not in FUNNEL_ALLOWED_STEPS:
        frappe.throw("مرحله قیف نامعتبر است.")

    event_id = _log_funnel_event_safely(
        step=normalized_step,
        model_name=model_name,
        item_code=item_code,
        qty=qty or 1,
        amount=amount or 0,
        session_id=session_id,
        customer=customer,
    )
    return {"ok": bool(event_id), "id": event_id}


def _parse_funnel_row(row):
    payload = _safe_json_loads(row.get("content"))
    subject = str(row.get("subject") or "")
    step = subject.replace(FUNNEL_SUBJECT_PREFIX, "", 1).strip()
    payload["step"] = payload.get("step") or step
    payload["created_at"] = row.get("creation")
    return payload


@frappe.whitelist()
def get_funnel_analytics(days=30):
    if frappe.session.user == "Guest":
        frappe.throw("دسترسی مجاز نیست.", frappe.PermissionError)
    roles = set(frappe.get_roles(frappe.session.user))
    if not ({"System Manager", "Website Manager"} & roles):
        frappe.throw("فقط مدیر سیستم به آنالیتیکس قیف دسترسی دارد.", frappe.PermissionError)

    if frappe.db.exists("DocType", "Analytics Event"):
        try:
            return analytics_service.build_legacy_funnel_payload(days=days)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Legacy Funnel API Bridge Error")

    day_count = min(max(_to_int(days, default=30), 1), 365)
    from_date = add_days(nowdate(), -1 * (day_count - 1))
    to_date = nowdate()

    funnel_subjects = [f"{FUNNEL_SUBJECT_PREFIX}{step}" for step in FUNNEL_ALLOWED_STEPS]
    rows = frappe.get_all(
        "Comment",
        filters={
            "comment_type": "Comment",
            "subject": ["in", funnel_subjects],
            "creation": [">=", f"{from_date} 00:00:00"],
        },
        fields=["name", "subject", "content", "creation"],
        order_by="creation asc",
        limit_page_length=0,
        ignore_permissions=True,
    )

    step_counts = {step: 0 for step in FUNNEL_ALLOWED_STEPS}
    unique_sessions = {step: set() for step in FUNNEL_ALLOWED_STEPS}
    top_models = {step: {} for step in FUNNEL_ALLOWED_STEPS}
    daily = {}

    for row in rows:
        parsed = _parse_funnel_row(row)
        step = (parsed.get("step") or "").strip()
        if step not in FUNNEL_ALLOWED_STEPS:
            continue

        step_counts[step] += 1

        sid = (parsed.get("session_id") or "").strip()
        if sid:
            unique_sessions[step].add(sid)

        model_name = (parsed.get("model_name") or "").strip()
        if model_name:
            top_models[step][model_name] = top_models[step].get(model_name, 0) + 1

        created_at = str(parsed.get("created_at") or row.get("creation") or "")
        day_key = created_at.split(" ")[0] if created_at else ""
        if day_key:
            if day_key not in daily:
                daily[day_key] = {k: 0 for k in FUNNEL_ALLOWED_STEPS}
            daily[day_key][step] += 1

    view_sessions = unique_sessions[FUNNEL_STEP_PRODUCT_VIEW]
    cart_sessions = unique_sessions[FUNNEL_STEP_ADD_TO_CART]
    order_sessions = unique_sessions[FUNNEL_STEP_ORDER_SUBMIT]

    view_to_cart_sessions = view_sessions.intersection(cart_sessions)
    cart_to_order_sessions = cart_sessions.intersection(order_sessions)
    view_to_order_sessions = view_sessions.intersection(order_sessions)

    def _rate(numerator, denominator):
        if not denominator:
            return 0
        return round((numerator / denominator) * 100, 2)

    def _top(entries):
        ordered = sorted(entries.items(), key=lambda row: (-row[1], row[0]))
        return [{"model_name": key, "count": value} for key, value in ordered[:10]]

    return {
        "range": {"from_date": from_date, "to_date": to_date, "days": day_count},
        "events": step_counts,
        "sessions": {
            "product_view": len(view_sessions),
            "add_to_cart": len(cart_sessions),
            "order_submit": len(order_sessions),
            "view_to_cart": len(view_to_cart_sessions),
            "cart_to_order": len(cart_to_order_sessions),
            "view_to_order": len(view_to_order_sessions),
        },
        "conversion_rate": {
            "view_to_cart_percent": _rate(len(view_to_cart_sessions), len(view_sessions)),
            "cart_to_order_percent": _rate(len(cart_to_order_sessions), len(cart_sessions)),
            "view_to_order_percent": _rate(len(view_to_order_sessions), len(view_sessions)),
        },
        "top_models": {
            FUNNEL_STEP_PRODUCT_VIEW: _top(top_models[FUNNEL_STEP_PRODUCT_VIEW]),
            FUNNEL_STEP_ADD_TO_CART: _top(top_models[FUNNEL_STEP_ADD_TO_CART]),
            FUNNEL_STEP_ORDER_SUBMIT: _top(top_models[FUNNEL_STEP_ORDER_SUBMIT]),
        },
        "daily": daily,
    }
