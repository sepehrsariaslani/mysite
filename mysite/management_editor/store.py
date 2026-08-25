from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import frappe


def management_page_overrides_path() -> Path:
    return Path(frappe.get_site_path("private", "mysite_management_page_overrides.json"))


def management_component_library_path() -> Path:
    return Path(frappe.get_site_path("private", "mysite_management_component_library.json"))


def load_management_page_overrides() -> dict:
    path = management_page_overrides_path()
    if not path.exists():
        return {}
    raw_text = ""
    try:
        raw_text = path.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        try:
            decoder = json.JSONDecoder()
            payload, _ = decoder.raw_decode((raw_text or "").lstrip())
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}


def save_management_page_overrides(payload: dict) -> None:
    path = management_page_overrides_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload or {}, ensure_ascii=False, indent=2)
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def load_management_component_library() -> dict:
    path = management_component_library_path()
    if not path.exists():
        return {}
    raw_text = ""
    try:
        raw_text = path.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        try:
            decoder = json.JSONDecoder()
            payload, _ = decoder.raw_decode((raw_text or "").lstrip())
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}


def save_management_component_library(payload: dict) -> None:
    path = management_component_library_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload or {}, ensure_ascii=False, indent=2)
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
