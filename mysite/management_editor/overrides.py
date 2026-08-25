from __future__ import annotations

import hashlib
import json
import re
from html import unescape as html_unescape

import frappe
from jinja2 import TemplateSyntaxError
from frappe.utils.jinja import get_jenv

from .shared import normalize_content_text, normalize_tracked_path, to_bool

VISUAL_MANAGED_CSS_START = "/* MYSITE-MANAGEMENT-VISUAL-STYLES:START */"
VISUAL_MANAGED_CSS_END = "/* MYSITE-MANAGEMENT-VISUAL-STYLES:END */"

VISUAL_ALLOWED_STYLE_KEYS = {
    "color",
    "backgroundColor",
    "fontSize",
    "fontWeight",
    "lineHeight",
    "letterSpacing",
    "textAlign",
    "borderRadius",
    "borderColor",
    "borderWidth",
    "padding",
    "margin",
    "width",
    "minWidth",
    "height",
    "maxHeight",
    "maxWidth",
    "minHeight",
    "display",
    "flexDirection",
    "flexWrap",
    "flexGrow",
    "flexShrink",
    "justifyContent",
    "alignItems",
    "gap",
    "gridTemplateColumns",
    "border",
    "boxShadow",
    "opacity",
    "zIndex",
    "overflowX",
    "overflowY",
    "transitionDuration",
    "position",
    "top",
    "right",
    "bottom",
    "left",
    "fontFeatureSettings",
    "fontVariantLigatures",
    "textIndent",
    "listStyleType",
    "listStylePosition",
    "whiteSpace",
    "wordSpacing",
    "textTransform",
    "textDecoration",
}
VISUAL_TRANSIENT_SELECTOR_CLASS_PATTERN = re.compile(r"\.mysite-visual-(?:selected|hover|layer-highlight)\b")
VISUAL_MAX_HTML_CONTENT_LEN = 50000
TOKEN_MAX_COLLECTIONS = 24
TOKEN_MAX_PER_MODE = 320
TOKEN_MAX_MODES = 12
TOKEN_MAX_NAME_LEN = 80
TOKEN_MAX_VALUE_LEN = 600
PROTOTYPE_MAX_FRAMES = 400
PROTOTYPE_MAX_LINKS = 1200
PROTOTYPE_MAX_FRAME_ID_LEN = 80
PROTOTYPE_MAX_TRANSITION_LEN = 24


def normalize_visual_selector(selector: str) -> str:
    value = str(selector or "").strip()
    if not value:
        return ""

    # Remove editor-only helper classes so saved selectors stay stable across page reloads.
    value = VISUAL_TRANSIENT_SELECTOR_CLASS_PATTERN.sub("", value)
    value = re.sub(r"\s*([>+~])\s*", r" \1 ", value)
    value = re.sub(r"\s+", " ", value).strip().strip(",")
    value = value.rstrip(".>+~ ").strip()

    if not value:
        return ""
    if "mysite-visual-" in value:
        return ""
    return value


def _is_meaningful_content_text(text) -> bool:
    value = normalize_content_text(text)
    if len(value) < 3:
        return False
    if "{{" in value or "}}" in value or "{%" in value or "%}" in value:
        return False
    if re.fullmatch(r"[-–—_=+*/|\\:;,.!?()\[\]{}0-9٪%<>#@]+", value):
        return False
    return bool(re.search(r"[A-Za-z\u0600-\u06FF]", value))


def clean_content_override_rows(rows):
    payload = rows
    if isinstance(payload, str):
        try:
            payload = frappe.parse_json(payload)
        except Exception:
            payload = json.loads(payload or "[]")

    if isinstance(payload, dict):
        payload = payload.get("items") or payload.get("content_overrides") or []
    if not isinstance(payload, (list, tuple)):
        return []

    result = []
    seen = set()
    for row in payload:
        if not isinstance(row, dict):
            continue
        source_text = normalize_content_text(row.get("source_text") or row.get("source"))
        if not _is_meaningful_content_text(source_text):
            continue
        replacement_text = normalize_content_text(row.get("replacement_text") or row.get("target"))
        scope = str(row.get("scope") or "").strip() or "page"
        source_file = str(row.get("source_file") or "").strip()

        key = str(row.get("key") or "").strip()
        if not key:
            key_seed = f"{scope}|{source_file}|{source_text}"
            key = hashlib.md5(key_seed.encode("utf-8")).hexdigest()[:16]

        if key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "key": key,
                "scope": scope,
                "scope_label": str(row.get("scope_label") or "").strip(),
                "source_file": source_file,
                "source_text": source_text,
                "replacement_text": replacement_text,
                "enabled": to_bool(row.get("enabled"), bool(replacement_text and replacement_text != source_text)),
            }
        )
        if len(result) >= 1200:
            break
    return result


def clean_visual_override_rows(rows):
    payload = rows
    if isinstance(payload, str):
        try:
            payload = frappe.parse_json(payload)
        except Exception:
            payload = json.loads(payload or "[]")

    if isinstance(payload, dict):
        payload = payload.get("items") or payload.get("visual_overrides") or []
    if not isinstance(payload, (list, tuple)):
        return []

    result = []
    seen = set()

    def _clean_visual_html_content(content) -> str:
        text = str(content or "")
        if not text:
            return ""
        text = text[:VISUAL_MAX_HTML_CONTENT_LEN]
        # Strip dangerous blocks.
        text = re.sub(r"<\s*(script|iframe|object|embed|meta|link|base)\b[^>]*>[\s\S]*?<\s*/\s*\1\s*>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<\s*(script|iframe|object|embed|meta|link|base)\b[^>]*\/?>", "", text, flags=re.IGNORECASE)
        # Remove inline event handlers and javascript: URLs.
        text = re.sub(r"""\s+on[a-z0-9_-]+\s*=\s*(".*?"|'.*?'|[^\s>]+)""", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"""(href|src)\s*=\s*(['"])\s*javascript:[\s\S]*?\2""", r"\1=\2\2", text, flags=re.IGNORECASE)
        # Editor-only attributes should not persist.
        text = re.sub(r"""\s+(contenteditable|data-mysite-inline-text)\s*=\s*(".*?"|'.*?'|[^\s>]+)""", "", text, flags=re.IGNORECASE | re.DOTALL)
        return text.strip()

    for row in payload:
        if not isinstance(row, dict):
            continue

        selector = normalize_visual_selector(row.get("selector") or "")
        if not selector or len(selector) > 420:
            continue
        if selector in seen:
            continue

        styles = {}
        raw_styles = row.get("styles")
        if isinstance(raw_styles, dict):
            for raw_key, raw_value in raw_styles.items():
                key = str(raw_key or "").strip()
                value = str(raw_value or "").strip()
                if not key or key not in VISUAL_ALLOWED_STYLE_KEYS:
                    continue
                if not value or len(value) > 120:
                    continue
                styles[key] = value

        text_content = str(row.get("text_content") or "")
        apply_text = to_bool(row.get("apply_text"), False)
        html_content = _clean_visual_html_content(
            row.get("html_content") or row.get("rich_text_html") or row.get("html")
        )
        apply_html = to_bool(row.get("apply_html"), False) and bool(html_content)
        selector_lower = selector.lower()
        is_root_selector = selector_lower in {"body", "html", "#app", ":root"} or bool(
            re.match(r"^(body|html|#app)\b", selector_lower)
        )
        if is_root_selector and (apply_text or apply_html):
            continue
        enabled = to_bool(row.get("enabled"), True)
        if not enabled:
            continue
        if not styles and not apply_text and not apply_html:
            continue

        seen.add(selector)
        result.append(
            {
                "selector": selector,
                "tag": str(row.get("tag") or "").strip(),
                "label": str(row.get("label") or "").strip(),
                "styles": styles,
                "apply_text": apply_text,
                "text_content": text_content if apply_text else "",
                "apply_html": apply_html,
                "html_content": html_content if apply_html else "",
            }
        )
        if len(result) >= 1200:
            break
    return result


def _normalize_token_name(raw_name: str) -> str:
    value = str(raw_name or "").strip()
    if not value:
        return ""
    if not value.startswith("--"):
        value = f"--{value.lstrip('-')}"
    value = re.sub(r"[^a-zA-Z0-9_-]", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-")
    if not value:
        return ""
    value = f"--{value}" if not value.startswith("--") else value
    if len(value) > TOKEN_MAX_NAME_LEN:
        value = value[:TOKEN_MAX_NAME_LEN]
    if not re.fullmatch(r"--[A-Za-z0-9_-]+", value):
        return ""
    return value


def clean_token_collections_payload(payload, fallback=None) -> tuple[dict, str, str]:
    fallback = fallback if isinstance(fallback, dict) else {}
    fallback_collections = fallback.get("token_collections") if isinstance(fallback.get("token_collections"), dict) else {}
    fallback_active_collection = str(fallback.get("token_active_collection") or "").strip()
    fallback_active_mode = str(fallback.get("token_active_mode") or "").strip() or "light"

    source = payload
    if isinstance(source, str):
        try:
            source = frappe.parse_json(source)
        except Exception:
            try:
                source = json.loads(source or "{}")
            except Exception:
                source = {}
    if not isinstance(source, dict):
        source = {}

    raw_collections = source.get("token_collections")
    if not isinstance(raw_collections, dict):
        raw_collections = fallback_collections
    clean_collections = {}

    for raw_collection_id, raw_collection in list((raw_collections or {}).items())[:TOKEN_MAX_COLLECTIONS]:
        collection_id = str(raw_collection_id or "").strip()
        if not collection_id:
            continue
        if not isinstance(raw_collection, dict):
            continue
        collection_name = str(raw_collection.get("name") or collection_id).strip()[:120] or collection_id
        raw_modes = raw_collection.get("modes") if isinstance(raw_collection.get("modes"), dict) else {}
        modes = {}
        for raw_mode_name, raw_mode_tokens in list(raw_modes.items())[:TOKEN_MAX_MODES]:
            mode_name = str(raw_mode_name or "").strip().lower()
            if not mode_name:
                continue
            if not isinstance(raw_mode_tokens, dict):
                continue
            tokens = {}
            for raw_token_name, raw_token_value in list(raw_mode_tokens.items())[:TOKEN_MAX_PER_MODE]:
                token_name = _normalize_token_name(raw_token_name)
                if not token_name:
                    continue
                token_value = str(raw_token_value or "").strip()
                if not token_value:
                    continue
                tokens[token_name] = token_value[:TOKEN_MAX_VALUE_LEN]
            if tokens:
                modes[mode_name] = tokens
        if not modes:
            modes = {"light": {}}
        clean_collections[collection_id] = {
            "id": collection_id,
            "name": collection_name,
            "modes": modes,
        }

    if not clean_collections:
        clean_collections = {
            "core": {
                "id": "core",
                "name": "Core",
                "modes": {"light": {}, "dark": {}, "brand": {}},
            }
        }

    active_collection = str(source.get("token_active_collection") or fallback_active_collection or "").strip()
    if not active_collection or active_collection not in clean_collections:
        active_collection = next(iter(clean_collections.keys()))

    active_mode = str(source.get("token_active_mode") or fallback_active_mode or "light").strip().lower() or "light"
    collection_modes = clean_collections.get(active_collection, {}).get("modes", {})
    if active_mode not in collection_modes:
        active_mode = "light" if "light" in collection_modes else (next(iter(collection_modes.keys()), "light"))

    return clean_collections, active_collection, active_mode


def _normalize_prototype_frame_id(value) -> str:
    frame_id = str(value or "").strip().lower()
    if not frame_id:
        return ""
    frame_id = re.sub(r"[^a-z0-9._-]", "-", frame_id)
    frame_id = re.sub(r"-{2,}", "-", frame_id).strip("-._")
    if not frame_id:
        return ""
    if len(frame_id) > PROTOTYPE_MAX_FRAME_ID_LEN:
        frame_id = frame_id[:PROTOTYPE_MAX_FRAME_ID_LEN]
    return frame_id


def clean_prototype_model_payload(payload, fallback=None) -> dict:
    fallback = fallback if isinstance(fallback, dict) else {}
    fallback_model = fallback.get("prototype_model") if isinstance(fallback.get("prototype_model"), dict) else {}

    source = payload
    if isinstance(source, str):
        try:
            source = frappe.parse_json(source)
        except Exception:
            try:
                source = json.loads(source or "{}")
            except Exception:
                source = {}
    if not isinstance(source, dict):
        source = {}

    candidate = source.get("prototype_model")
    if isinstance(candidate, dict):
        model_source = candidate
    elif source:
        model_source = source
    else:
        model_source = fallback_model

    if not isinstance(model_source, dict):
        model_source = {}

    raw_frames = model_source.get("frames")
    if not isinstance(raw_frames, dict):
        raw_frames = {}
    frames = {}
    for raw_frame_id, raw_frame in list(raw_frames.items())[:PROTOTYPE_MAX_FRAMES]:
        frame_id = _normalize_prototype_frame_id(raw_frame_id)
        if not frame_id:
            continue
        frame = raw_frame if isinstance(raw_frame, dict) else {}
        selector = normalize_visual_selector(frame.get("selector") or "")
        if not selector:
            continue
        frames[frame_id] = {
            "id": frame_id,
            "selector": selector,
            "label": str(frame.get("label") or "").strip()[:140],
        }

    raw_links = model_source.get("links")
    if not isinstance(raw_links, (list, tuple)):
        raw_links = []
    links = []
    seen_link_ids = set()
    for row in raw_links:
        if not isinstance(row, dict):
            continue
        source_frame = _normalize_prototype_frame_id(row.get("source_frame_id") or row.get("source") or "")
        target_frame = _normalize_prototype_frame_id(row.get("target_frame_id") or row.get("target") or "")
        if not source_frame or not target_frame:
            continue
        if source_frame == target_frame:
            continue
        if source_frame not in frames or target_frame not in frames:
            continue
        transition = str(row.get("transition") or "instant").strip().lower()
        if transition not in {"instant", "dissolve", "smart-animate", "smart_animate"}:
            transition = "instant"
        if transition == "smart_animate":
            transition = "smart-animate"
        transition = transition[:PROTOTYPE_MAX_TRANSITION_LEN]
        link_id = str(row.get("id") or f"{source_frame}->{target_frame}").strip()[:180]
        if not link_id or link_id in seen_link_ids:
            continue
        seen_link_ids.add(link_id)
        duration_ms = int(row.get("duration_ms") or 280)
        if duration_ms < 60:
            duration_ms = 60
        if duration_ms > 8000:
            duration_ms = 8000
        links.append(
            {
                "id": link_id,
                "source_frame_id": source_frame,
                "target_frame_id": target_frame,
                "trigger": "click",
                "transition": transition,
                "duration_ms": duration_ms,
                "smart_animate": to_bool(row.get("smart_animate"), transition == "smart-animate"),
            }
        )
        if len(links) >= PROTOTYPE_MAX_LINKS:
            break

    start_frame_id = _normalize_prototype_frame_id(model_source.get("start_frame_id") or "")
    if start_frame_id and start_frame_id not in frames:
        start_frame_id = ""
    if not start_frame_id and frames:
        start_frame_id = next(iter(frames.keys()))

    return {
        "preview_enabled": to_bool(model_source.get("preview_enabled"), False),
        "start_frame_id": start_frame_id,
        "frames": frames,
        "links": links,
    }


def camel_to_kebab(name) -> str:
    text = str(name or "").strip()
    if not text:
        return ""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
    text = text.replace("_", "-")
    return text.lower()


def visual_rows_to_css(rows) -> str:
    lines = []
    for row in rows or []:
        selector = str(row.get("selector") or "").strip()
        if not selector:
            continue
        styles = row.get("styles") if isinstance(row.get("styles"), dict) else {}
        declarations = []
        for raw_key, raw_value in styles.items():
            key = camel_to_kebab(raw_key)
            value = str(raw_value or "").strip()
            if not key or not value:
                continue
            declarations.append(f"  {key}: {value};")
        if not declarations:
            continue
        lines.append(f"{selector} {{")
        lines.extend(declarations)
        lines.append("}")
        lines.append("")
    return "\n".join(lines).strip()


def build_managed_visual_css(rows, raw_css) -> str:
    css_from_rows = visual_rows_to_css(rows or [])
    css_parts = []
    if css_from_rows:
        css_parts.append(css_from_rows)
    raw_css_text = str(raw_css or "").strip()
    if raw_css_text:
        css_parts.append(raw_css_text)
    return "\n\n".join(css_parts).strip()


def extract_first_style_block(source) -> str:
    source_text = str(source or "")
    match = re.search(r"<style\b[^>]*>([\s\S]*?)</style>", source_text, flags=re.IGNORECASE)
    if not match:
        return ""
    return str(match.group(1) or "").strip()


def extract_managed_visual_css(source) -> str:
    source_text = str(source or "")
    pattern = re.compile(
        re.escape(VISUAL_MANAGED_CSS_START) + r"([\s\S]*?)" + re.escape(VISUAL_MANAGED_CSS_END),
        flags=re.IGNORECASE,
    )
    match = pattern.search(source_text)
    if not match:
        return ""
    return str(match.group(1) or "").strip()


def upsert_managed_visual_css(source, css_content) -> str:
    source_text = str(source or "")
    css_text = str(css_content or "").strip()
    managed_block = f"{VISUAL_MANAGED_CSS_START}\n{css_text}\n{VISUAL_MANAGED_CSS_END}"

    pattern = re.compile(
        re.escape(VISUAL_MANAGED_CSS_START) + r"[\s\S]*?" + re.escape(VISUAL_MANAGED_CSS_END),
        flags=re.IGNORECASE,
    )
    if pattern.search(source_text):
        return pattern.sub(managed_block, source_text, count=1)

    style_match = re.search(r"<style\b[^>]*>", source_text, flags=re.IGNORECASE)
    if style_match:
        close_match = re.search(r"</style>", source_text[style_match.end() :], flags=re.IGNORECASE)
        if close_match:
            close_index = style_match.end() + close_match.start()
            before = source_text[:close_index]
            after = source_text[close_index:]
            insert = f"\n\n{managed_block}\n"
            return f"{before}{insert}{after}"

    return f"{source_text}\n\n<style scoped>\n{managed_block}\n</style>\n"


def infer_route_title(route, fallback="صفحه") -> str:
    path = normalize_tracked_path(route)
    if path == "/mysite":
        return "صفحه اصلی"
    slug = path.replace("/mysite/", "").strip("/") if path else ""
    slug = slug or fallback
    slug = slug.replace("-", " ").replace("_", " ").strip()
    return slug or fallback


def validate_jinja_template_source(source, file_rel="") -> None:
    source_text = str(source or "")
    if not source_text.strip():
        frappe.throw("محتوای فایل قابل ویرایش خالی است.")
    try:
        get_jenv().parse(source_text)
    except TemplateSyntaxError as exc:
        line_no = int(exc.lineno or 0) if getattr(exc, "lineno", None) else 0
        file_hint = f" ({file_rel})" if file_rel else ""
        message = str(exc.message or str(exc)).strip() or "خطای سینتکس Jinja"
        if line_no > 0:
            frappe.throw(f"خطای سینتکس Jinja در فایل{file_hint}، خط {line_no}: {message}")
        frappe.throw(f"خطای سینتکس Jinja در فایل{file_hint}: {message}")


def clean_page_override_payload(payload, fallback=None) -> dict:
    payload = payload or {}
    fallback = fallback or {}
    raw_content_rows = payload.get("content_overrides") if "content_overrides" in payload else fallback.get("content_overrides", [])
    raw_visual_rows = payload.get("visual_overrides") if "visual_overrides" in payload else fallback.get("visual_overrides", [])
    raw_visual_css = payload.get("visual_raw_css") if "visual_raw_css" in payload else fallback.get("visual_raw_css", "")
    token_source = {}
    if "token_collections" in payload:
        token_source["token_collections"] = payload.get("token_collections")
    if "token_active_collection" in payload:
        token_source["token_active_collection"] = payload.get("token_active_collection")
    if "token_active_mode" in payload:
        token_source["token_active_mode"] = payload.get("token_active_mode")
    token_collections, token_active_collection, token_active_mode = clean_token_collections_payload(
        token_source,
        fallback=fallback,
    )
    prototype_model = clean_prototype_model_payload(payload, fallback=fallback)
    visual_css_text = str(raw_visual_css or "")
    if len(visual_css_text) > 120000:
        visual_css_text = visual_css_text[:120000]

    return {
        "title": str(payload.get("title") or fallback.get("title") or "").strip(),
        "meta_description": str(payload.get("meta_description") or fallback.get("meta_description") or "").strip(),
        "canonical_url": str(payload.get("canonical_url") or fallback.get("canonical_url") or "").strip(),
        "meta_image": str(payload.get("meta_image") or fallback.get("meta_image") or "").strip(),
        "noindex": to_bool(payload.get("noindex"), fallback.get("noindex", False)),
        "protected_page": to_bool(payload.get("protected_page"), fallback.get("protected_page", False)),
        "status_key": str(payload.get("status_key") or fallback.get("status_key") or "published").strip() or "published",
        "content_overrides": clean_content_override_rows(raw_content_rows),
        "visual_overrides": clean_visual_override_rows(raw_visual_rows),
        "visual_raw_css": visual_css_text,
        "token_collections": token_collections,
        "token_active_collection": token_active_collection,
        "token_active_mode": token_active_mode,
        "prototype_model": prototype_model,
        "content_updated_at": str(payload.get("content_updated_at") or fallback.get("content_updated_at") or "").strip(),
        "content_updated_by": str(payload.get("content_updated_by") or fallback.get("content_updated_by") or "").strip(),
        "visual_updated_at": str(payload.get("visual_updated_at") or fallback.get("visual_updated_at") or "").strip(),
        "visual_updated_by": str(payload.get("visual_updated_by") or fallback.get("visual_updated_by") or "").strip(),
    }
