from __future__ import annotations

import hashlib
import json
from pathlib import Path

import frappe
from frappe.utils import now_datetime

from .shared import normalize_tracked_path


def management_visual_editor_history_path() -> Path:
    return Path(frappe.get_site_path("private", "mysite_management_visual_editor_history.json"))


def load_management_visual_editor_history() -> dict:
    path = management_visual_editor_history_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def save_management_visual_editor_history(payload: dict) -> None:
    path = management_visual_editor_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {}, ensure_ascii=False, indent=2), encoding="utf-8")


def backup_visual_editor_version(route, file_rel_path, current_source, note="") -> dict:
    history = load_management_visual_editor_history()
    route_key = normalize_tracked_path(route)
    if not route_key:
        return {}

    route_payload = history.get(route_key) if isinstance(history.get(route_key), dict) else {}
    versions = route_payload.get("versions") if isinstance(route_payload.get("versions"), list) else []
    version_id = frappe.generate_hash(length=12)
    versions.append(
        {
            "id": version_id,
            "saved_at": now_datetime().isoformat(),
            "saved_by": frappe.session.user,
            "note": str(note or "").strip(),
            "file": str(file_rel_path or "").strip(),
            "sha1": hashlib.sha1(str(current_source or "").encode("utf-8")).hexdigest(),
            "content": str(current_source or ""),
        }
    )
    versions = versions[-60:]
    history[route_key] = {
        "route": route_key,
        "file": str(file_rel_path or "").strip(),
        "versions": versions,
    }
    save_management_visual_editor_history(history)
    return versions[-1]


def serialize_visual_editor_history(route, target_file=None):
    route_key = normalize_tracked_path(route)
    history = load_management_visual_editor_history()
    route_payload = history.get(route_key) if isinstance(history.get(route_key), dict) else {}
    versions = route_payload.get("versions") if isinstance(route_payload.get("versions"), list) else []
    target_file_value = str(target_file or "").strip()
    items = []
    for row in reversed(versions):
        if not isinstance(row, dict):
            continue
        row_file = str(row.get("file") or "").strip()
        if target_file_value and row_file != target_file_value:
            continue
        items.append(
            {
                "id": str(row.get("id") or "").strip(),
                "saved_at": str(row.get("saved_at") or ""),
                "saved_by": str(row.get("saved_by") or ""),
                "note": str(row.get("note") or ""),
                "file": row_file,
                "sha1": str(row.get("sha1") or ""),
            }
        )
    return items
