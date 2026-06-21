from __future__ import annotations

import json
import re
from datetime import datetime
from html import unescape as html_unescape
from pathlib import Path
from urllib.parse import urlsplit

import frappe


def normalize_tracked_path(raw_url) -> str:
    value = str(raw_url or "").strip()
    if not value:
        return ""
    try:
        parsed = urlsplit(value)
        path = parsed.path or value
    except Exception:
        path = value
    if not path.startswith("/"):
        path = f"/{path.lstrip('/')}"
    path = re.sub(r"/{2,}", "/", path)
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return path


def to_bool(value, default=False) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off", ""}:
        return False
    return bool(default)


def normalize_content_text(value) -> str:
    text = html_unescape(str(value or ""))
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def relative_path(path_obj, root_path) -> str:
    try:
        return Path(path_obj).relative_to(Path(root_path)).as_posix()
    except Exception:
        return str(path_obj)


def modified_at(path_obj) -> str:
    try:
        return datetime.fromtimestamp(Path(path_obj).stat().st_mtime).isoformat(timespec="seconds")
    except Exception:
        return ""


def extract_frontend_routes(app_vue_file, app_root):
    app_vue_file = Path(app_vue_file)
    if not app_vue_file.exists():
        return []

    try:
        source = app_vue_file.read_text(encoding="utf-8")
    except Exception:
        return []

    import_map = {}
    for match in re.finditer(r"import\s+([A-Za-z0-9_]+)\s+from\s+'\./pages/([^']+\.vue)'", source):
        import_map[match.group(1)] = f"frontend/src/pages/{match.group(2)}"

    route_rows = []
    for match in re.finditer(r"<([A-Za-z0-9_]+)\s+v(?:-else)?-if=\"page === '([^']+)'\"", source):
        component_name = match.group(1)
        page_key = match.group(2)
        route_rows.append(
            {
                "page_key": page_key,
                "component": component_name,
                "file": import_map.get(component_name, ""),
                "route_guess": "/mysite" if page_key == "home" else f"/{page_key}",
            }
        )

    fallback_match = re.search(r"<([A-Za-z0-9_]+)\s+v-else\s*/>", source)
    if fallback_match:
        component_name = fallback_match.group(1)
        route_rows.append(
            {
                "page_key": "fallback",
                "component": component_name,
                "file": import_map.get(component_name, ""),
                "route_guess": "default-route-fallback",
            }
        )

    return route_rows


def scan_website_pages(app_root):
    app_root = Path(app_root)
    website_dir = app_root / "mysite" / "www" / "mysite"
    if not website_dir.exists():
        return []

    rows = []
    for html_file in sorted(website_dir.glob("*.html")):
        stem = html_file.stem
        route = "/mysite" if stem in {"index", "home"} else f"/{stem}"

        py_exact = website_dir / f"{stem}.py"
        py_slug = website_dir / f"{stem.replace('-', '_')}.py"
        py_file = py_exact if py_exact.exists() else py_slug

        title = ""
        try:
            html_text = html_file.read_text(encoding="utf-8")
            title_match = re.search(r"<title>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
            if title_match:
                title = html_unescape(title_match.group(1).strip())
        except Exception:
            title = ""

        rows.append(
            {
                "name": stem,
                "route": route,
                "title": title,
                "html_file": relative_path(html_file, app_root),
                "py_file": relative_path(py_file, app_root) if py_file.exists() else "",
                "modified_at": modified_at(html_file),
            }
        )

    return rows


def resolve_request_payload(payload=None):
    if isinstance(payload, (bytes, bytearray)):
        try:
            payload = payload.decode("utf-8")
        except Exception:
            payload = payload.decode("utf-8", errors="ignore")

    if isinstance(payload, str):
        payload_text = payload.strip()
        if not payload_text:
            payload = {}
        else:
            try:
                payload = frappe.parse_json(payload_text)
            except Exception:
                try:
                    payload = json.loads(payload_text)
                except Exception:
                    payload = {}

    if isinstance(payload, dict):
        return payload

    resolved = {}
    form_dict = getattr(frappe, "form_dict", None)
    if form_dict:
        try:
            form_payload = form_dict.as_dict() if hasattr(form_dict, "as_dict") else dict(form_dict)
        except Exception:
            form_payload = {}
        if isinstance(form_payload, dict):
            for key, value in form_payload.items():
                if key == "cmd":
                    continue
                resolved[key] = value

    raw_payload_text = ""
    if getattr(frappe, "request", None):
        try:
            raw_payload_text = frappe.request.get_data(as_text=True) or ""
        except Exception:
            try:
                raw_data = frappe.request.data
                if isinstance(raw_data, (bytes, bytearray)):
                    raw_payload_text = raw_data.decode("utf-8", errors="ignore")
                else:
                    raw_payload_text = str(raw_data or "")
            except Exception:
                raw_payload_text = ""

    raw_payload_text = str(raw_payload_text or "").strip()
    if raw_payload_text:
        try:
            raw_payload = frappe.parse_json(raw_payload_text)
        except Exception:
            try:
                raw_payload = json.loads(raw_payload_text)
            except Exception:
                raw_payload = {}
        if isinstance(raw_payload, dict):
            resolved.update(raw_payload)

    nested_payload = resolved.get("payload")
    if isinstance(nested_payload, (bytes, bytearray)):
        try:
            nested_payload = nested_payload.decode("utf-8")
        except Exception:
            nested_payload = nested_payload.decode("utf-8", errors="ignore")
    if isinstance(nested_payload, str):
        nested_text = nested_payload.strip()
        if nested_text:
            try:
                nested_payload = frappe.parse_json(nested_text)
            except Exception:
                try:
                    nested_payload = json.loads(nested_text)
                except Exception:
                    nested_payload = {}
        else:
            nested_payload = {}
    if isinstance(nested_payload, dict):
        resolved.update(nested_payload)

    return resolved if isinstance(resolved, dict) else {}
