from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote, urlsplit

import frappe

from .shared import extract_frontend_routes, normalize_tracked_path, relative_path, scan_website_pages


def resolve_visual_editor_file_candidate(spec, base_path, app_root):
    spec_text = str(spec or "").strip()
    if not spec_text:
        return None

    app_root = Path(app_root)
    app_root_resolved = app_root.resolve()
    base_path = Path(base_path)

    if spec_text.startswith("."):
        candidate = (base_path.parent / spec_text).resolve()
    elif spec_text.startswith("@/"):
        candidate = (app_root / "frontend" / "src" / spec_text[2:]).resolve()
    else:
        return None

    try:
        candidate.relative_to(app_root_resolved)
    except Exception:
        return None

    candidates = []
    if candidate.suffix:
        candidates.append(candidate)
    else:
        candidates.extend([candidate.with_suffix(".vue"), candidate.with_suffix(".html")])

    for item in candidates:
        if item.suffix.lower() not in {".vue", ".html"}:
            continue
        if item.exists():
            return item
    return None


def extract_local_import_specs(source):
    text = str(source or "")
    specs = set()
    pattern = re.compile(r"""import\s+[^;\n]*?\s+from\s+['\"]([^'\"]+)['\"]""")
    for match in pattern.finditer(text):
        spec = str(match.group(1) or "").strip()
        if spec:
            specs.add(spec)
    return sorted(specs)


def collect_visual_editor_editable_files(primary_file_path, app_root, max_files=60):
    app_root = Path(app_root)
    app_root_resolved = app_root.resolve()
    queue = [Path(primary_file_path).resolve()]
    visited = set()
    resolved_files = []

    while queue and len(resolved_files) < max_files:
        file_path = queue.pop(0)
        file_key = str(file_path)
        if file_key in visited:
            continue
        visited.add(file_key)

        try:
            file_path.relative_to(app_root_resolved)
        except Exception:
            continue
        if not file_path.exists():
            continue
        if file_path.suffix.lower() not in {".vue", ".html"}:
            continue

        resolved_files.append(file_path)

        if file_path.suffix.lower() != ".vue":
            continue
        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception:
            source = ""
        for spec in extract_local_import_specs(source):
            next_file = resolve_visual_editor_file_candidate(spec, file_path, app_root)
            if not next_file:
                continue
            if str(next_file) in visited:
                continue
            queue.append(next_file)

    files = []
    for idx, file_path in enumerate(resolved_files):
        rel = relative_path(file_path, app_root)
        file_type = "vue" if file_path.suffix.lower() == ".vue" else "html"
        files.append(
            {
                "file": rel,
                "file_type": file_type,
                "name": file_path.stem,
                "is_primary": idx == 0,
                "label": f"{file_path.stem} ({file_type.upper()})",
            }
        )
    return files


def collect_frontend_component_usage(frontend_routes, app_root, max_routes=260):
    app_root = Path(app_root)
    usage_map = {}

    for route_row in list(frontend_routes or [])[:max_routes]:
        raw_route_guess = str(route_row.get("route_guess") or "").strip()
        if raw_route_guess == "default-route-fallback":
            continue
        route_key = normalize_tracked_path(raw_route_guess)
        if not route_key or not route_key.startswith("/mysite") or route_key.startswith("/mysite/management"):
            continue
        page_rel = str(route_row.get("file") or "").strip()
        if not page_rel:
            continue

        page_path = (app_root / page_rel).resolve()
        try:
            page_path.relative_to(app_root.resolve())
        except Exception:
            continue
        if not page_path.exists() or page_path.suffix.lower() != ".vue":
            continue

        try:
            source = page_path.read_text(encoding="utf-8")
        except Exception:
            source = ""

        for spec in extract_local_import_specs(source):
            component_path = resolve_visual_editor_file_candidate(spec, page_path, app_root)
            if not component_path:
                continue
            component_rel = relative_path(component_path, app_root)
            if "/frontend/src/components/" not in f"/{component_rel}":
                continue
            usage_map.setdefault(component_rel, set()).add(route_key)

    return {key: sorted(values) for key, values in usage_map.items()}


def is_frontend_component_file(file_rel) -> bool:
    value = str(file_rel or "").strip().replace("\\", "/").lstrip("/")
    if not value:
        return False
    return "/frontend/src/components/" in f"/{value}"


def resolve_component_usage_routes(component_file_rel, app_root):
    component_file = str(component_file_rel or "").strip().replace("\\", "/").lstrip("/")
    if not component_file or not is_frontend_component_file(component_file):
        return []

    app_root = Path(app_root)
    app_vue_file = app_root / "frontend" / "src" / "App.vue"
    frontend_routes = extract_frontend_routes(app_vue_file, app_root)
    usage_map = collect_frontend_component_usage(frontend_routes, app_root)
    return list(usage_map.get(component_file, []))


def resolve_visual_editor_scope_key(route, file_rel=None) -> str:
    file_value = str(file_rel or "").strip().replace("\\", "/").lstrip("/")
    if is_frontend_component_file(file_value):
        return normalize_tracked_path(f"component::{file_value}")
    return normalize_tracked_path(route)


def resolve_direct_visual_editor_file(target_file, app_root):
    app_root = Path(app_root)
    app_root_resolved = app_root.resolve()
    file_rel = str(target_file or "").strip().replace("\\", "/").lstrip("/")
    if not file_rel:
        return None

    file_path = (app_root / file_rel).resolve()
    try:
        file_path.relative_to(app_root_resolved)
    except Exception:
        return None
    if not file_path.exists() or file_path.suffix.lower() not in {".vue", ".html"}:
        return None

    allowed_roots = [
        (app_root / "frontend" / "src" / "components").resolve(),
        (app_root / "frontend" / "src" / "pages").resolve(),
        (app_root / "mysite" / "www" / "mysite").resolve(),
    ]
    allowed = False
    for root in allowed_roots:
        try:
            file_path.relative_to(root)
            allowed = True
            break
        except Exception:
            continue
    if not allowed:
        return None

    file_type = "vue" if file_path.suffix.lower() == ".vue" else "html"
    return {
        "file_rel": file_rel,
        "file_path": file_path,
        "file_type": file_type,
        "component": file_path.stem,
    }


def resolve_management_visual_editor_target(route, target_file=None):
    app_root = Path(frappe.get_app_path("mysite")).parent
    app_root_resolved = app_root.resolve()
    route_key = normalize_tracked_path(route)
    target_file_value = str(target_file or "").strip()

    if route_key.startswith("/mysite/management") and target_file_value:
        route_key = ""

    if (not route_key or not route_key.startswith("/mysite")) and target_file_value:
        direct_target = resolve_direct_visual_editor_file(target_file_value, app_root)
        if not direct_target:
            frappe.throw("مسیر صفحه یا فایل انتخابی معتبر نیست.")

        resolved_route = route_key if route_key.startswith("/mysite") and not route_key.startswith("/mysite/management") else ""
        if not resolved_route and is_frontend_component_file(direct_target.get("file_rel")):
            usage_routes = resolve_component_usage_routes(direct_target.get("file_rel"), app_root)
            for usage_route in usage_routes:
                normalized_usage_route = normalize_tracked_path(usage_route)
                if not normalized_usage_route or not normalized_usage_route.startswith("/mysite"):
                    continue
                if normalized_usage_route.startswith("/mysite/management"):
                    continue
                resolved_route = normalized_usage_route
                break
        if not resolved_route:
            resolved_route = "/mysite"

        return {
            "route": resolved_route,
            "app_root": app_root,
            "file_rel": direct_target.get("file_rel"),
            "primary_file_rel": direct_target.get("file_rel"),
            "file_path": direct_target.get("file_path"),
            "component": direct_target.get("component"),
            "file_type": direct_target.get("file_type"),
            "editable_files": [
                {
                    "file": direct_target.get("file_rel"),
                    "file_type": direct_target.get("file_type"),
                    "name": direct_target.get("component"),
                    "is_primary": True,
                    "label": f"{direct_target.get('component')} ({str(direct_target.get('file_type') or '').upper()})",
                }
            ],
        }

    if not route_key or not route_key.startswith("/mysite"):
        frappe.throw("مسیر صفحه معتبر نیست.")

    app_vue_file = app_root / "frontend" / "src" / "App.vue"
    frontend_routes = extract_frontend_routes(app_vue_file, app_root)
    frontend_match = next(
        (
            row
            for row in (frontend_routes or [])
            if normalize_tracked_path(row.get("route_guess")) == route_key and str(row.get("file") or "").strip()
        ),
        None,
    )

    file_rel = str((frontend_match or {}).get("file") or "").strip()
    component = str((frontend_match or {}).get("component") or "").strip()
    if not file_rel:
        website_pages = scan_website_pages(app_root)
        website_map = {row.get("route"): row for row in website_pages if row.get("route")}
        file_rel = str((website_map.get(route_key) or {}).get("html_file") or "").strip()

    if not file_rel:
        frappe.throw("برای این مسیر فایل قابل‌ویرایش پیدا نشد.")

    primary_file_path = (app_root / file_rel).resolve()
    try:
        primary_file_path.relative_to(app_root_resolved)
    except Exception:
        frappe.throw("مسیر فایل صفحه معتبر نیست.")

    if primary_file_path.suffix.lower() not in {".vue", ".html"}:
        frappe.throw("فقط فایل‌های Vue/HTML قابل ویرایش هستند.")
    if not primary_file_path.exists():
        frappe.throw("فایل صفحه پیدا نشد.")

    editable_files = collect_visual_editor_editable_files(primary_file_path, app_root)
    editable_rel_map = {str(row.get("file") or "").strip(): row for row in editable_files}
    selected_rel = str(target_file or "").strip() or file_rel
    if selected_rel not in editable_rel_map:
        direct_target = resolve_direct_visual_editor_file(selected_rel, app_root)
        if not direct_target:
            frappe.throw("فایل انتخابی برای این مسیر قابل ویرایش نیست.")
        selected_rel = str(direct_target.get("file_rel") or "").strip()
        selected_meta = {
            "file": selected_rel,
            "file_type": direct_target.get("file_type"),
            "name": direct_target.get("component"),
            "is_primary": False,
            "label": f"{direct_target.get('component')} ({str(direct_target.get('file_type') or '').upper()})",
        }
        editable_files.append(selected_meta)
        editable_rel_map[selected_rel] = selected_meta

    file_path = (app_root / selected_rel).resolve()
    try:
        file_path.relative_to(app_root_resolved)
    except Exception:
        frappe.throw("مسیر فایل صفحه معتبر نیست.")
    if not file_path.exists():
        frappe.throw("فایل انتخابی پیدا نشد.")

    selected_meta = editable_rel_map.get(selected_rel) or {}
    selected_component = component if selected_rel == file_rel else str(selected_meta.get("name") or Path(selected_rel).stem)

    return {
        "route": route_key,
        "app_root": app_root,
        "file_rel": selected_rel,
        "primary_file_rel": file_rel,
        "file_path": file_path,
        "component": selected_component,
        "file_type": "vue" if file_path.suffix.lower() == ".vue" else "html",
        "editable_files": editable_files,
    }


def resolve_management_visual_editor_preview_route(route_key, raw_route=None) -> str:
    normalized_route = normalize_tracked_path(route_key)
    if not normalized_route:
        return "/mysite"
    if (
        normalized_route == "/default-route-fallback"
        or not normalized_route.startswith("/mysite")
        or normalized_route.startswith("/mysite/management")
    ):
        return "/mysite"

    raw_value = str(raw_route or "").strip()
    if raw_value:
        try:
            parsed = urlsplit(raw_value)
            raw_path = normalize_tracked_path(parsed.path or raw_value)
            if raw_path == normalized_route and parsed.query:
                return f"{normalized_route}?{parsed.query}"
        except Exception:
            pass

    if normalized_route == "/mysite/product":
        sample_model = ""
        try:
            sample_model = frappe.db.get_value(
                "Item Variant Attribute",
                {"attribute": "مدل محصول", "attribute_value": ["!=", ""]},
                "attribute_value",
            )
        except Exception:
            sample_model = ""
        sample_model = str(sample_model or "").strip()
        if sample_model:
            return f"/mysite/product/{quote(sample_model)}"
        return "/mysite/sofas"

    return normalized_route
