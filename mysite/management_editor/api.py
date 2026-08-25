from __future__ import annotations

import hashlib
import json
from pathlib import Path

import frappe
from frappe.utils import now_datetime

from .errors import json_error_from_exception, json_validation_error
from .history import (
    backup_visual_editor_version,
    load_management_visual_editor_history,
    serialize_visual_editor_history,
)
from .overrides import (
    build_managed_visual_css,
    clean_prototype_model_payload,
    clean_page_override_payload,
    clean_visual_override_rows,
    extract_first_style_block,
    extract_managed_visual_css,
    infer_route_title,
    upsert_managed_visual_css,
    validate_jinja_template_source,
)
from .shared import normalize_tracked_path, resolve_request_payload, scan_website_pages
from .store import (
    load_management_component_library,
    load_management_page_overrides,
    save_management_component_library,
    save_management_page_overrides,
)
from .target_resolver import (
    is_frontend_component_file,
    resolve_component_usage_routes,
    resolve_management_visual_editor_preview_route,
    resolve_management_visual_editor_target,
    resolve_visual_editor_scope_key,
)

DEFAULT_EDITOR_BRANCH = "main"
MAX_EDITOR_BRANCHES = 32
MAX_EDITOR_MILESTONES = 200
MAX_COMPONENT_LIBRARY_VERSIONS = 120


def _legacy_api():
    # Imported lazily to avoid circular import at module load time.
    from mysite import api as legacy_api

    return legacy_api


def _deep_copy_json(data):
    try:
        return json.loads(json.dumps(data or {}))
    except Exception:
        return {}


def _normalize_branch_name(value) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    cleaned = []
    for char in text:
        if char.isalnum() or char in {"-", "_", ".", "/"}:
            cleaned.append(char)
        else:
            cleaned.append("-")
    text = "".join(cleaned)
    while "--" in text:
        text = text.replace("--", "-")
    text = text.strip("-._/")[:64]
    return text


def _clean_branch_milestones(rows) -> list[dict]:
    if not isinstance(rows, list):
        return []
    result = []
    for row in rows[:MAX_EDITOR_MILESTONES]:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").strip()[:180]
        if not title:
            continue
        milestone_id = str(row.get("id") or "").strip()[:80]
        if not milestone_id:
            milestone_id = f"ms-{hashlib.md5(f'{title}|{len(result)}'.encode('utf-8')).hexdigest()[:10]}"
        result.append(
            {
                "id": milestone_id,
                "title": title,
                "note": str(row.get("note") or "").strip()[:2000],
                "created_at": str(row.get("created_at") or ""),
                "created_by": str(row.get("created_by") or ""),
            }
        )
    return result


def _clean_editor_payload_dict(payload, fallback=None) -> dict:
    payload = payload if isinstance(payload, dict) else {}
    fallback = fallback if isinstance(fallback, dict) else {}
    return clean_page_override_payload(payload, fallback=fallback)


def _normalize_editor_versioning(route_override) -> dict:
    route_override = route_override if isinstance(route_override, dict) else {}
    base_payload = _clean_editor_payload_dict({}, fallback=route_override)
    raw_versioning = route_override.get("versioning") if isinstance(route_override.get("versioning"), dict) else {}
    raw_branches = raw_versioning.get("branches") if isinstance(raw_versioning.get("branches"), dict) else {}

    branches = {}
    for raw_name, raw_branch in list(raw_branches.items())[:MAX_EDITOR_BRANCHES]:
        name = _normalize_branch_name(raw_name)
        if not name:
            continue
        branch = raw_branch if isinstance(raw_branch, dict) else {}
        payload = _clean_editor_payload_dict(branch.get("payload"), fallback=base_payload)
        branches[name] = {
            "name": name,
            "payload": payload,
            "created_at": str(branch.get("created_at") or ""),
            "created_by": str(branch.get("created_by") or ""),
            "updated_at": str(branch.get("updated_at") or ""),
            "updated_by": str(branch.get("updated_by") or ""),
            "milestones": _clean_branch_milestones(branch.get("milestones")),
        }

    if not branches:
        branches[DEFAULT_EDITOR_BRANCH] = {
            "name": DEFAULT_EDITOR_BRANCH,
            "payload": base_payload,
            "created_at": "",
            "created_by": "",
            "updated_at": "",
            "updated_by": "",
            "milestones": [],
        }
    elif DEFAULT_EDITOR_BRANCH not in branches:
        branches[DEFAULT_EDITOR_BRANCH] = {
            "name": DEFAULT_EDITOR_BRANCH,
            "payload": base_payload,
            "created_at": "",
            "created_by": "",
            "updated_at": "",
            "updated_by": "",
            "milestones": [],
        }

    raw_active = raw_versioning.get("active_branch") if isinstance(raw_versioning, dict) else route_override.get("active_branch")
    active_branch = _normalize_branch_name(raw_active) or DEFAULT_EDITOR_BRANCH
    if active_branch not in branches:
        active_branch = DEFAULT_EDITOR_BRANCH if DEFAULT_EDITOR_BRANCH in branches else next(iter(branches.keys()))

    return {
        "active_branch": active_branch,
        "branches": branches,
    }


def _editor_active_payload(versioning_state) -> dict:
    active_branch = str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH)
    branches = versioning_state.get("branches") if isinstance(versioning_state.get("branches"), dict) else {}
    branch = branches.get(active_branch) if isinstance(branches.get(active_branch), dict) else {}
    payload = branch.get("payload") if isinstance(branch.get("payload"), dict) else {}
    return _clean_editor_payload_dict(payload, fallback={})


def _build_override_from_versioning(versioning_state) -> dict:
    payload = _editor_active_payload(versioning_state)
    output = dict(payload)
    output["active_branch"] = str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH)
    output["versioning"] = _deep_copy_json(versioning_state)
    return output


def _versioning_branches_summary(versioning_state) -> list[dict]:
    active_branch = str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH)
    branches = versioning_state.get("branches") if isinstance(versioning_state.get("branches"), dict) else {}
    result = []
    for name, branch in branches.items():
        if not isinstance(branch, dict):
            continue
        payload = branch.get("payload") if isinstance(branch.get("payload"), dict) else {}
        milestones = branch.get("milestones") if isinstance(branch.get("milestones"), list) else []
        visual_rows = payload.get("visual_overrides") if isinstance(payload.get("visual_overrides"), list) else []
        active_items = len([row for row in visual_rows if row.get("styles") or row.get("apply_text") or row.get("apply_html")])
        result.append(
            {
                "name": str(name),
                "is_active": str(name) == active_branch,
                "milestone_count": len(milestones),
                "active_items": active_items,
                "updated_at": str(branch.get("updated_at") or payload.get("visual_updated_at") or ""),
                "updated_by": str(branch.get("updated_by") or payload.get("visual_updated_by") or ""),
            }
        )
    result.sort(key=lambda row: (0 if row.get("name") == DEFAULT_EDITOR_BRANCH else 1, str(row.get("name") or "")))
    return result


def _clean_component_library_components(payload) -> dict:
    payload = payload if isinstance(payload, dict) else {}
    result = {}
    for raw_id, raw_row in list(payload.items())[:2000]:
        component_id = str(raw_id or "").strip()
        if not component_id:
            continue
        row = raw_row if isinstance(raw_row, dict) else {}
        name = str(row.get("name") or component_id).strip()[:140] or component_id
        variants_raw = row.get("variants") if isinstance(row.get("variants"), dict) else {}
        variants = {}
        for raw_variant, raw_variant_row in list(variants_raw.items())[:120]:
            variant_name = str(raw_variant or "").strip()[:120] or "default"
            variant_row = raw_variant_row if isinstance(raw_variant_row, dict) else {}
            html = str(variant_row.get("html") or "").strip()
            if not html:
                continue
            variants[variant_name] = {"html": html[:120000]}
        master_html = str(row.get("master_html") or variants.get("default", {}).get("html") or "").strip()[:120000]
        if not variants and master_html:
            variants["default"] = {"html": master_html}
        if not variants and not master_html:
            continue
        result[component_id] = {
            "id": component_id,
            "name": name,
            "master_html": master_html,
            "variants": variants,
            "description": str(row.get("description") or "").strip()[:600],
            "version": max(1, int(row.get("version") or 1)),
            "updated_at": str(row.get("updated_at") or ""),
            "published_at": str(row.get("published_at") or ""),
        }
    return result


def _normalize_component_library_store(payload) -> dict:
    payload = payload if isinstance(payload, dict) else {}
    raw_libraries = payload.get("libraries") if isinstance(payload.get("libraries"), dict) else {}
    libraries = {}
    for raw_name, raw_library in list(raw_libraries.items())[:120]:
        library_name = _normalize_branch_name(raw_name) or "global"
        library = raw_library if isinstance(raw_library, dict) else {}
        versions_raw = library.get("versions") if isinstance(library.get("versions"), list) else []
        versions = []
        seen_ids = set()
        for row in versions_raw[:MAX_COMPONENT_LIBRARY_VERSIONS]:
            if not isinstance(row, dict):
                continue
            version_id = str(row.get("id") or "").strip()[:120]
            if not version_id or version_id in seen_ids:
                continue
            seen_ids.add(version_id)
            versions.append(
                {
                    "id": version_id,
                    "created_at": str(row.get("created_at") or ""),
                    "created_by": str(row.get("created_by") or ""),
                    "note": str(row.get("note") or "").strip()[:2000],
                    "components": _clean_component_library_components(row.get("components")),
                }
            )
        latest_version_id = str(library.get("latest_version_id") or "").strip()
        if latest_version_id and not any(row.get("id") == latest_version_id for row in versions):
            latest_version_id = ""
        if not latest_version_id and versions:
            latest_version_id = str(versions[-1].get("id") or "")
        libraries[library_name] = {
            "name": library_name,
            "description": str(library.get("description") or "").strip()[:600],
            "latest_version_id": latest_version_id,
            "versions": versions,
        }
    if "global" not in libraries:
        libraries["global"] = {"name": "global", "description": "Default shared library", "latest_version_id": "", "versions": []}
    return {"libraries": libraries}


def _component_library_summaries(library_store) -> list[dict]:
    store = _normalize_component_library_store(library_store)
    result = []
    for name, library in (store.get("libraries") or {}).items():
        versions = library.get("versions") if isinstance(library.get("versions"), list) else []
        latest_id = str(library.get("latest_version_id") or "")
        latest = next((row for row in versions if str(row.get("id") or "") == latest_id), None)
        latest_components = _clean_component_library_components((latest or {}).get("components"))
        result.append(
            {
                "name": name,
                "description": str(library.get("description") or ""),
                "latest_version_id": latest_id,
                "version_count": len(versions),
                "updated_at": str((latest or {}).get("created_at") or ""),
                "components_count": len(latest_components),
            }
        )
    result.sort(key=lambda row: str(row.get("name") or ""))
    return result


def get_management_visual_editor_payload(route=None, target_file=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    raw_route = str(route or frappe.form_dict.get("route") or "").strip()
    route_key = normalize_tracked_path(raw_route)
    target_file = str(target_file or frappe.form_dict.get("target_file") or "").strip()
    target = resolve_management_visual_editor_target(route_key, target_file=target_file or None)
    effective_route = normalize_tracked_path(target.get("route")) or route_key
    scope_key = resolve_visual_editor_scope_key(effective_route, target.get("file_rel"))

    source = target["file_path"].read_text(encoding="utf-8")
    overrides = load_management_page_overrides()
    route_override = overrides.get(scope_key) if isinstance(overrides.get(scope_key), dict) else {}
    versioning_state = _normalize_editor_versioning(route_override)
    active_branch = str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH)
    active_payload = _editor_active_payload(versioning_state)

    visual_rows = clean_visual_override_rows(active_payload.get("visual_overrides") if isinstance(active_payload, dict) else [])
    visual_raw_css = str(active_payload.get("visual_raw_css") or "") if isinstance(active_payload, dict) else ""
    token_collections = active_payload.get("token_collections") if isinstance(active_payload.get("token_collections"), dict) else {}
    token_active_collection = str(active_payload.get("token_active_collection") or "") if isinstance(active_payload, dict) else ""
    token_active_mode = str(active_payload.get("token_active_mode") or "light") if isinstance(active_payload, dict) else "light"
    prototype_model = clean_prototype_model_payload(active_payload, fallback=active_payload)
    managed_css = extract_managed_visual_css(source)
    is_component_file = is_frontend_component_file(target.get("file_rel"))
    component_usage_routes = resolve_component_usage_routes(target.get("file_rel"), target.get("app_root")) if is_component_file else []
    component_library_store = _normalize_component_library_store(load_management_component_library())
    component_library_summaries = _component_library_summaries(component_library_store)

    return {
        "route": effective_route,
        "preview_route": resolve_management_visual_editor_preview_route(effective_route, raw_route=raw_route),
        "file": target.get("file_rel"),
        "primary_file": target.get("primary_file_rel"),
        "file_type": target.get("file_type"),
        "component": target.get("component"),
        "editable_files": target.get("editable_files") or [],
        "source": source,
        "style_source": extract_first_style_block(source),
        "managed_css": managed_css,
        "visual_raw_css": visual_raw_css,
        "visual_overrides": visual_rows,
        "token_collections": token_collections,
        "token_active_collection": token_active_collection,
        "token_active_mode": token_active_mode,
        "prototype_model": prototype_model,
        "active_branch": active_branch,
        "versioning_branches": _versioning_branches_summary(versioning_state),
        "history": serialize_visual_editor_history(scope_key, target_file=target.get("file_rel")),
        "updated_at": str(active_payload.get("visual_updated_at") or ""),
        "updated_by": str(active_payload.get("visual_updated_by") or ""),
        "component_library_summaries": component_library_summaries,
        "is_component_file": bool(is_component_file),
        "component_usage_routes": component_usage_routes,
        "component_primary_route": component_usage_routes[0] if component_usage_routes else "",
        "default_preview_mode": "component" if is_component_file else "page",
        "scope_key": scope_key,
    }


def save_management_visual_editor_changes(route=None, items=None, raw_css=None, full_source=None, note=None, target_file=None, payload=None):
    try:
        return _save_management_visual_editor_changes_impl(
            route=route,
            items=items,
            raw_css=raw_css,
            full_source=full_source,
            note=note,
            target_file=target_file,
            payload=payload,
        )
    except frappe.ValidationError as err:
        return json_validation_error(err)
    except Exception as err:
        context = {
            "route": str(route or ""),
            "target_file": str(target_file or ""),
            "has_items": bool(items),
            "has_raw_css": bool(raw_css),
            "has_full_source": bool(full_source),
            "note": str(note or ""),
        }
        return json_error_from_exception(
            err,
            default_message="ذخیره انجام نشد. لطفاً یک‌بار صفحه را رفرش کنید و دوباره تلاش کنید.",
            log_title="save_management_visual_editor_changes:unexpected",
            context=context,
        )


def _save_management_visual_editor_changes_impl(route=None, items=None, raw_css=None, full_source=None, note=None, target_file=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    request_payload = resolve_request_payload(payload=payload)
    workflow_bypass = legacy_api._workflow_bypass_enabled(request_payload)

    route_key = normalize_tracked_path(route or request_payload.get("route") or "")
    target_file_val = str(target_file or request_payload.get("target_file") or "").strip()

    if items is None:
        items = request_payload.get("items") or request_payload.get("visual_overrides")
    if raw_css is None:
        raw_css = request_payload.get("raw_css")
    if full_source is None:
        full_source = request_payload.get("full_source") or request_payload.get("source")
    if note is None:
        note = request_payload.get("note")

    if not route_key and not target_file_val:
        frappe.throw("مسیر صفحه یا فایل انتخابی ارسال نشده است.")

    target = resolve_management_visual_editor_target(route_key, target_file=target_file_val or None)
    effective_route = normalize_tracked_path(target.get("route")) or route_key or "/mysite"
    scope_key = resolve_visual_editor_scope_key(effective_route, target.get("file_rel"))

    if not workflow_bypass and legacy_api.should_enforce("content"):
        workflow_resp = legacy_api._workflow_create_response(
            module_key="content",
            target_type="visual_source",
            target_key=effective_route,
            payload={
                "route": effective_route,
                "target_file": target_file_val,
                "items": items,
                "raw_css": raw_css,
                "full_source": full_source,
                "note": note,
            },
            current_snapshot={"file": target.get("file_rel")},
            source_endpoint="save_management_visual_editor_changes",
        )
        workflow_resp["workflow_enforced"] = True
        workflow_resp["message"] = "تغییرات برای تأیید ارسال شد و هنوز منتشر نشده‌اند."
        return workflow_resp

    if not target["file_path"].exists():
        frappe.throw("فایل مقصد پیدا نشد.")

    source_before = target["file_path"].read_text(encoding="utf-8")
    backup_info = backup_visual_editor_version(scope_key, target.get("file_rel"), source_before, note=note or "before-save")

    app_root = Path(frappe.get_app_path("mysite")).parent
    website_pages = scan_website_pages(app_root)
    website_map = {row.get("route"): row for row in website_pages if row.get("route")}

    overrides = load_management_page_overrides()
    current_override = overrides.get(scope_key) if isinstance(overrides.get(scope_key), dict) else {}
    versioning_state = _normalize_editor_versioning(current_override)
    requested_branch = _normalize_branch_name(request_payload.get("active_branch") or request_payload.get("branch_name"))
    if requested_branch and requested_branch in (versioning_state.get("branches") or {}):
        versioning_state["active_branch"] = requested_branch
    active_branch = str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH)
    active_branch_payload = _editor_active_payload(versioning_state)

    payload_for_clean = {}
    if items is not None:
        payload_for_clean["visual_overrides"] = items
    else:
        payload_for_clean["visual_overrides"] = active_branch_payload.get("visual_overrides") or []

    if raw_css is not None:
        payload_for_clean["visual_raw_css"] = raw_css
    elif "visual_raw_css" in active_branch_payload:
        payload_for_clean["visual_raw_css"] = active_branch_payload.get("visual_raw_css", "")

    if "token_collections" in request_payload:
        payload_for_clean["token_collections"] = request_payload.get("token_collections")
    elif "token_collections" in active_branch_payload:
        payload_for_clean["token_collections"] = active_branch_payload.get("token_collections")

    if "token_active_collection" in request_payload:
        payload_for_clean["token_active_collection"] = request_payload.get("token_active_collection")
    elif "token_active_collection" in active_branch_payload:
        payload_for_clean["token_active_collection"] = active_branch_payload.get("token_active_collection")

    if "token_active_mode" in request_payload:
        payload_for_clean["token_active_mode"] = request_payload.get("token_active_mode")
    elif "token_active_mode" in active_branch_payload:
        payload_for_clean["token_active_mode"] = active_branch_payload.get("token_active_mode")

    if "prototype_model" in request_payload:
        payload_for_clean["prototype_model"] = request_payload.get("prototype_model")
    elif "prototype_model" in active_branch_payload:
        payload_for_clean["prototype_model"] = active_branch_payload.get("prototype_model")

    clean_payload = clean_page_override_payload(payload_for_clean, fallback=active_branch_payload)

    if not clean_payload.get("title"):
        website_title = str((website_map.get(effective_route) or {}).get("title") or "").strip()
        clean_payload["title"] = website_title or infer_route_title(effective_route)

    clean_payload["status_label"] = "منتشر شده" if clean_payload.get("status_key") == "published" else "غیرفعال"
    clean_payload["updated_at"] = now_datetime().isoformat()
    clean_payload["updated_by"] = frappe.session.user
    clean_payload["visual_updated_at"] = now_datetime().isoformat()
    clean_payload["visual_updated_by"] = frappe.session.user

    branches = versioning_state.get("branches") if isinstance(versioning_state.get("branches"), dict) else {}
    if active_branch not in branches:
        branches[active_branch] = {
            "name": active_branch,
            "payload": _clean_editor_payload_dict({}, fallback=clean_payload),
            "created_at": now_datetime().isoformat(),
            "created_by": frappe.session.user,
            "updated_at": "",
            "updated_by": "",
            "milestones": [],
        }
    branch = branches.get(active_branch) if isinstance(branches.get(active_branch), dict) else {}
    branch["name"] = active_branch
    branch["payload"] = clean_payload
    if not branch.get("created_at"):
        branch["created_at"] = now_datetime().isoformat()
    if not branch.get("created_by"):
        branch["created_by"] = frappe.session.user
    branch["updated_at"] = now_datetime().isoformat()
    branch["updated_by"] = frappe.session.user
    branch["milestones"] = _clean_branch_milestones(branch.get("milestones"))
    branches[active_branch] = branch
    versioning_state["branches"] = branches
    versioning_state["active_branch"] = active_branch

    source_after = source_before
    full_source_str = str(full_source or "").strip()
    if len(full_source_str) > 2_000_000:
        frappe.throw("حجم محتوای ارسالی بیش از حد مجاز است.")

    if full_source_str:
        source_after = full_source_str
    else:
        managed_css = build_managed_visual_css(
            clean_payload.get("visual_overrides") or [],
            clean_payload.get("visual_raw_css"),
        )
        existing_managed_css = extract_managed_visual_css(source_before)
        if managed_css or existing_managed_css:
            source_after = upsert_managed_visual_css(source_before, managed_css)

    if target.get("file_type") == "html":
        validate_jinja_template_source(source_after, file_rel=target.get("file_rel"))

    file_changed = source_after != source_before
    if file_changed:
        target["file_path"].write_text(source_after, encoding="utf-8")

    overrides[scope_key] = _build_override_from_versioning(versioning_state)
    save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()

    visual_rows = clean_payload.get("visual_overrides") or []
    active_rows = [
        row for row in visual_rows
        if row.get("styles") or row.get("apply_text") or row.get("apply_html")
    ]

    response = {
        "ok": True,
        "workflow_enforced": False,
        "route": effective_route,
        "scope_key": scope_key,
        "active_branch": active_branch,
        "versioning_branches": _versioning_branches_summary(versioning_state),
        "file": target.get("file_rel"),
        "file_type": target.get("file_type"),
        "saved_items": len(visual_rows),
        "active_items": len(active_rows),
        "history_version_id": str(backup_info.get("id") or ""),
        "source_changed": file_changed,
        "source_sha1": hashlib.sha1(str(source_after or "").encode("utf-8")).hexdigest(),
    }

    try:
        legacy_api._workflow_shadow_record(
            module_key="content",
            target_type="visual_source",
            target_key=effective_route,
            payload={
                "route": effective_route,
                "target_file": target_file_val,
                "items": items,
                "raw_css": raw_css,
                "full_source": full_source,
                "note": note,
            },
            current_snapshot={"file": target.get("file_rel")},
            source_endpoint="save_management_visual_editor_changes",
            publish_result=response,
        )
    except Exception:
        frappe.log_error(title="save_management_visual_editor_changes:workflow-shadow-failed", message=frappe.get_traceback())

    return response


def _resolve_editor_scope(route=None, target_file=None, payload=None):
    request_payload = resolve_request_payload(payload=payload)
    route_key = normalize_tracked_path(route or request_payload.get("route"))
    target_file_val = str(target_file or request_payload.get("target_file") or "").strip()
    target = resolve_management_visual_editor_target(route_key, target_file=target_file_val or None)
    effective_route = normalize_tracked_path(target.get("route")) or route_key or "/mysite"
    scope_key = resolve_visual_editor_scope_key(effective_route, target.get("file_rel"))
    return {
        "request_payload": request_payload,
        "route": effective_route,
        "scope_key": scope_key,
        "target": target,
        "target_file": target_file_val,
    }


def get_management_visual_editor_versioning(route=None, target_file=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    resolved = _resolve_editor_scope(route=route, target_file=target_file, payload=payload)
    overrides = load_management_page_overrides()
    route_override = overrides.get(resolved["scope_key"]) if isinstance(overrides.get(resolved["scope_key"]), dict) else {}
    versioning_state = _normalize_editor_versioning(route_override)
    return {
        "ok": True,
        "route": resolved["route"],
        "scope_key": resolved["scope_key"],
        "active_branch": str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH),
        "branches": _versioning_branches_summary(versioning_state),
    }


def create_management_visual_editor_branch(route=None, branch_name=None, from_branch=None, target_file=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    resolved = _resolve_editor_scope(route=route, target_file=target_file, payload=payload)
    request_payload = resolved["request_payload"]
    branch_name = _normalize_branch_name(branch_name or request_payload.get("branch_name"))
    from_branch = _normalize_branch_name(from_branch or request_payload.get("from_branch")) or DEFAULT_EDITOR_BRANCH
    if not branch_name:
        frappe.throw("نام branch معتبر نیست.")
    if branch_name == DEFAULT_EDITOR_BRANCH:
        frappe.throw("branch پیش‌فرض قابل ایجاد مجدد نیست.")

    overrides = load_management_page_overrides()
    current_override = overrides.get(resolved["scope_key"]) if isinstance(overrides.get(resolved["scope_key"]), dict) else {}
    versioning_state = _normalize_editor_versioning(current_override)
    branches = versioning_state.get("branches") if isinstance(versioning_state.get("branches"), dict) else {}
    if branch_name in branches:
        frappe.throw("branch با این نام وجود دارد.")
    if len(branches) >= MAX_EDITOR_BRANCHES:
        frappe.throw("تعداد branch ها به سقف مجاز رسیده است.")
    if from_branch not in branches:
        from_branch = str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH)
    source_payload = branches.get(from_branch, {}).get("payload") if isinstance(branches.get(from_branch), dict) else {}
    now_text = now_datetime().isoformat()
    branches[branch_name] = {
        "name": branch_name,
        "payload": _clean_editor_payload_dict({}, fallback=source_payload if isinstance(source_payload, dict) else {}),
        "created_at": now_text,
        "created_by": frappe.session.user,
        "updated_at": now_text,
        "updated_by": frappe.session.user,
        "milestones": [],
    }
    versioning_state["branches"] = branches
    versioning_state["active_branch"] = branch_name

    overrides[resolved["scope_key"]] = _build_override_from_versioning(versioning_state)
    save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()
    return {
        "ok": True,
        "route": resolved["route"],
        "scope_key": resolved["scope_key"],
        "active_branch": branch_name,
        "branches": _versioning_branches_summary(versioning_state),
    }


def set_management_visual_editor_active_branch(route=None, branch_name=None, target_file=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    resolved = _resolve_editor_scope(route=route, target_file=target_file, payload=payload)
    request_payload = resolved["request_payload"]
    branch_name = _normalize_branch_name(branch_name or request_payload.get("branch_name"))
    if not branch_name:
        frappe.throw("branch انتخاب نشده است.")

    overrides = load_management_page_overrides()
    current_override = overrides.get(resolved["scope_key"]) if isinstance(overrides.get(resolved["scope_key"]), dict) else {}
    versioning_state = _normalize_editor_versioning(current_override)
    branches = versioning_state.get("branches") if isinstance(versioning_state.get("branches"), dict) else {}
    if branch_name not in branches:
        frappe.throw("branch پیدا نشد.")
    versioning_state["active_branch"] = branch_name
    overrides[resolved["scope_key"]] = _build_override_from_versioning(versioning_state)
    save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()
    return {
        "ok": True,
        "route": resolved["route"],
        "scope_key": resolved["scope_key"],
        "active_branch": branch_name,
        "branches": _versioning_branches_summary(versioning_state),
    }


def create_management_visual_editor_milestone(route=None, title=None, note=None, branch_name=None, target_file=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    resolved = _resolve_editor_scope(route=route, target_file=target_file, payload=payload)
    request_payload = resolved["request_payload"]
    title = str(title or request_payload.get("title") or "").strip()
    note = str(note or request_payload.get("note") or "").strip()
    if not title:
        frappe.throw("عنوان milestone الزامی است.")
    branch_name = _normalize_branch_name(branch_name or request_payload.get("branch_name"))

    overrides = load_management_page_overrides()
    current_override = overrides.get(resolved["scope_key"]) if isinstance(overrides.get(resolved["scope_key"]), dict) else {}
    versioning_state = _normalize_editor_versioning(current_override)
    active_branch = str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH)
    if not branch_name:
        branch_name = active_branch
    branches = versioning_state.get("branches") if isinstance(versioning_state.get("branches"), dict) else {}
    if branch_name not in branches:
        frappe.throw("branch milestone پیدا نشد.")
    branch = branches.get(branch_name) if isinstance(branches.get(branch_name), dict) else {}
    milestones = branch.get("milestones") if isinstance(branch.get("milestones"), list) else []
    milestone_id = f"ms-{hashlib.md5(f'{branch_name}|{title}|{now_datetime().isoformat()}'.encode('utf-8')).hexdigest()[:10]}"
    milestones.append(
        {
            "id": milestone_id,
            "title": title[:180],
            "note": note[:2000],
            "created_at": now_datetime().isoformat(),
            "created_by": frappe.session.user,
        }
    )
    branch["milestones"] = _clean_branch_milestones(milestones)
    branch["updated_at"] = now_datetime().isoformat()
    branch["updated_by"] = frappe.session.user
    branches[branch_name] = branch
    versioning_state["branches"] = branches

    overrides[resolved["scope_key"]] = _build_override_from_versioning(versioning_state)
    save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()
    return {
        "ok": True,
        "route": resolved["route"],
        "scope_key": resolved["scope_key"],
        "active_branch": str(versioning_state.get("active_branch") or DEFAULT_EDITOR_BRANCH),
        "created_milestone_id": milestone_id,
        "branches": _versioning_branches_summary(versioning_state),
    }


def merge_management_visual_editor_branch(route=None, source_branch=None, target_branch=None, target_file=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    resolved = _resolve_editor_scope(route=route, target_file=target_file, payload=payload)
    request_payload = resolved["request_payload"]
    source_branch = _normalize_branch_name(source_branch or request_payload.get("source_branch"))
    target_branch = _normalize_branch_name(target_branch or request_payload.get("target_branch")) or DEFAULT_EDITOR_BRANCH
    if not source_branch:
        frappe.throw("source branch مشخص نشده است.")
    if source_branch == target_branch:
        frappe.throw("source و target branch باید متفاوت باشند.")

    overrides = load_management_page_overrides()
    current_override = overrides.get(resolved["scope_key"]) if isinstance(overrides.get(resolved["scope_key"]), dict) else {}
    versioning_state = _normalize_editor_versioning(current_override)
    branches = versioning_state.get("branches") if isinstance(versioning_state.get("branches"), dict) else {}
    if source_branch not in branches or target_branch not in branches:
        frappe.throw("branch merge پیدا نشد.")

    source_payload = branches.get(source_branch, {}).get("payload") if isinstance(branches.get(source_branch), dict) else {}
    merged_payload = _clean_editor_payload_dict({}, fallback=source_payload if isinstance(source_payload, dict) else {})

    target_state = branches.get(target_branch) if isinstance(branches.get(target_branch), dict) else {}
    target_state["payload"] = merged_payload
    target_state["updated_at"] = now_datetime().isoformat()
    target_state["updated_by"] = frappe.session.user
    milestones = target_state.get("milestones") if isinstance(target_state.get("milestones"), list) else []
    milestones.append(
        {
            "id": f"merge-{hashlib.md5(f'{source_branch}->{target_branch}|{now_datetime().isoformat()}'.encode('utf-8')).hexdigest()[:10]}",
            "title": f"Merge {source_branch} -> {target_branch}",
            "note": str(request_payload.get("note") or "").strip()[:2000],
            "created_at": now_datetime().isoformat(),
            "created_by": frappe.session.user,
        }
    )
    target_state["milestones"] = _clean_branch_milestones(milestones)
    branches[target_branch] = target_state
    versioning_state["branches"] = branches
    versioning_state["active_branch"] = target_branch

    overrides[resolved["scope_key"]] = _build_override_from_versioning(versioning_state)
    save_management_page_overrides(overrides)
    frappe.clear_cache()
    frappe.db.commit()
    return {
        "ok": True,
        "route": resolved["route"],
        "scope_key": resolved["scope_key"],
        "active_branch": target_branch,
        "branches": _versioning_branches_summary(versioning_state),
    }


def get_management_component_library(library_name=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    request_payload = resolve_request_payload(payload=None)
    library_name = _normalize_branch_name(library_name or request_payload.get("library_name") or "global") or "global"
    store = _normalize_component_library_store(load_management_component_library())
    libraries = store.get("libraries") if isinstance(store.get("libraries"), dict) else {}
    library = libraries.get(library_name) if isinstance(libraries.get(library_name), dict) else libraries.get("global", {})
    versions = library.get("versions") if isinstance(library.get("versions"), list) else []
    latest_version_id = str(library.get("latest_version_id") or "")
    latest = next((row for row in versions if str(row.get("id") or "") == latest_version_id), None)
    if latest is None and versions:
        latest = versions[-1]
    latest_components = _clean_component_library_components((latest or {}).get("components"))
    return {
        "ok": True,
        "library_name": str(library.get("name") or library_name),
        "latest_version_id": str((latest or {}).get("id") or ""),
        "versions": [
            {
                "id": str(row.get("id") or ""),
                "created_at": str(row.get("created_at") or ""),
                "created_by": str(row.get("created_by") or ""),
                "note": str(row.get("note") or ""),
                "components_count": len(_clean_component_library_components(row.get("components"))),
            }
            for row in versions
        ],
        "components": latest_components,
        "summaries": _component_library_summaries(store),
    }


def publish_management_component_library(library_name=None, components=None, note=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    request_payload = resolve_request_payload(payload=payload)
    library_name = _normalize_branch_name(library_name or request_payload.get("library_name") or "global") or "global"
    components = components if components is not None else request_payload.get("components")
    note = str(note or request_payload.get("note") or "").strip()[:2000]
    clean_components = _clean_component_library_components(components if isinstance(components, dict) else {})
    if not clean_components:
        frappe.throw("کامپوننتی برای publish ارسال نشده است.")

    store = _normalize_component_library_store(load_management_component_library())
    libraries = store.get("libraries") if isinstance(store.get("libraries"), dict) else {}
    library = libraries.get(library_name) if isinstance(libraries.get(library_name), dict) else {"name": library_name, "description": "", "latest_version_id": "", "versions": []}
    versions = library.get("versions") if isinstance(library.get("versions"), list) else []
    version_id = f"{library_name}-{hashlib.md5(f'{now_datetime().isoformat()}|{frappe.session.user}|{len(clean_components)}'.encode('utf-8')).hexdigest()[:12]}"
    versions.append(
        {
            "id": version_id,
            "created_at": now_datetime().isoformat(),
            "created_by": frappe.session.user,
            "note": note,
            "components": clean_components,
        }
    )
    if len(versions) > MAX_COMPONENT_LIBRARY_VERSIONS:
        versions = versions[-MAX_COMPONENT_LIBRARY_VERSIONS:]
    library["versions"] = versions
    library["latest_version_id"] = version_id
    libraries[library_name] = library
    store["libraries"] = libraries
    save_management_component_library(store)
    frappe.clear_cache()
    frappe.db.commit()
    return {
        "ok": True,
        "library_name": library_name,
        "published_version_id": version_id,
        "components_count": len(clean_components),
        "summaries": _component_library_summaries(store),
    }


def consume_management_component_library(library_name=None, version_id=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    request_payload = resolve_request_payload(payload=payload)
    library_name = _normalize_branch_name(library_name or request_payload.get("library_name") or "global") or "global"
    version_id = str(version_id or request_payload.get("version_id") or "").strip()
    store = _normalize_component_library_store(load_management_component_library())
    libraries = store.get("libraries") if isinstance(store.get("libraries"), dict) else {}
    library = libraries.get(library_name) if isinstance(libraries.get(library_name), dict) else libraries.get("global", {})
    versions = library.get("versions") if isinstance(library.get("versions"), list) else []
    selected = None
    if version_id:
        selected = next((row for row in versions if str(row.get("id") or "") == version_id), None)
    if selected is None:
        latest_id = str(library.get("latest_version_id") or "")
        selected = next((row for row in versions if str(row.get("id") or "") == latest_id), None)
    if selected is None and versions:
        selected = versions[-1]
    if selected is None:
        return {"ok": True, "library_name": library_name, "version_id": "", "components": {}, "components_count": 0}
    components = _clean_component_library_components(selected.get("components"))
    return {
        "ok": True,
        "library_name": str(library.get("name") or library_name),
        "version_id": str(selected.get("id") or ""),
        "components": components,
        "components_count": len(components),
    }


def get_management_visual_editor_history(route=None, target_file=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    target_file = str(target_file or frappe.form_dict.get("target_file") or "").strip()
    route_key = normalize_tracked_path(route or frappe.form_dict.get("route"))
    target = resolve_management_visual_editor_target(route_key, target_file=target_file or None)
    effective_route = normalize_tracked_path(target.get("route")) or route_key
    scope_key = resolve_visual_editor_scope_key(effective_route, target.get("file_rel"))
    return {
        "route": effective_route,
        "scope_key": scope_key,
        "items": serialize_visual_editor_history(scope_key, target_file=target.get("file_rel")),
    }


def restore_management_visual_editor_history(route=None, version_id=None, target_file=None, payload=None):
    legacy_api = _legacy_api()
    legacy_api._require_management_access("content.edit")

    request_payload = resolve_request_payload(payload=payload)
    route_key = normalize_tracked_path(route or request_payload.get("route"))
    version_id = str(version_id or request_payload.get("version_id") or "").strip()
    target_file = str(target_file or request_payload.get("target_file") or "").strip()
    if not version_id:
        frappe.throw("نسخه انتخاب نشده است.")

    initial_target = resolve_management_visual_editor_target(route_key, target_file=target_file or None)
    effective_route = normalize_tracked_path(initial_target.get("route")) or route_key
    scope_key = resolve_visual_editor_scope_key(effective_route, initial_target.get("file_rel"))

    history = load_management_visual_editor_history()
    route_payload = history.get(scope_key) if isinstance(history.get(scope_key), dict) else {}
    versions = route_payload.get("versions") if isinstance(route_payload.get("versions"), list) else []
    selected = next((row for row in versions if str((row or {}).get("id") or "").strip() == version_id), None)
    if not selected:
        frappe.throw("نسخه موردنظر پیدا نشد.")

    selected_file = str((selected or {}).get("file") or "").strip()
    if target_file and selected_file and target_file != selected_file:
        frappe.throw("نسخه انتخابی مربوط به فایل دیگری است.")

    target = resolve_management_visual_editor_target(effective_route, target_file=selected_file or target_file or None)
    effective_route = normalize_tracked_path(target.get("route")) or effective_route
    scope_key = resolve_visual_editor_scope_key(effective_route, target.get("file_rel"))

    current_source = target["file_path"].read_text(encoding="utf-8")
    backup_visual_editor_version(scope_key, target.get("file_rel"), current_source, note=f"before-restore:{version_id}")

    restore_content = str(selected.get("content") or "")
    target["file_path"].write_text(restore_content, encoding="utf-8")
    frappe.clear_cache()
    frappe.db.commit()

    return {
        "ok": True,
        "route": effective_route,
        "scope_key": scope_key,
        "file": target.get("file_rel"),
        "restored_version_id": version_id,
        "history": serialize_visual_editor_history(scope_key, target_file=target.get("file_rel")),
    }
