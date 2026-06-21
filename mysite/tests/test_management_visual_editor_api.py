import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import frappe

from mysite.management_editor import api as editor_api
from mysite.management_editor.overrides import (
    clean_page_override_payload,
    clean_visual_override_rows,
    extract_managed_visual_css,
    upsert_managed_visual_css,
)
from mysite.management_editor.target_resolver import resolve_management_visual_editor_target


class TestManagementVisualEditorApi(unittest.TestCase):
    def test_clean_visual_override_rows_filters_invalid(self):
        rows = clean_visual_override_rows(
            [
                {"selector": ".hero", "styles": {"color": "#111", "invalid": "x"}, "apply_text": False},
                {"selector": ".hero", "styles": {"color": "#222"}},
                {"selector": "", "styles": {"color": "#333"}},
                {"selector": ".title", "apply_text": True, "text_content": "سلام"},
            ]
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["selector"], ".hero")
        self.assertEqual(rows[0]["styles"], {"color": "#111"})
        self.assertEqual(rows[1]["selector"], ".title")

    def test_clean_visual_override_rows_supports_rich_html(self):
        rows = clean_visual_override_rows(
            [
                {
                    "selector": ".title",
                    "apply_html": True,
                    "html_content": '<span style="font-weight:700" onclick="alert(1)">Hello</span><script>alert(1)</script>',
                }
            ]
        )
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["apply_html"])
        self.assertIn("font-weight:700", rows[0]["html_content"])
        self.assertNotIn("<script", rows[0]["html_content"].lower())
        self.assertNotIn("onclick=", rows[0]["html_content"].lower())

    def test_clean_page_override_payload_keeps_token_collections(self):
        payload = clean_page_override_payload(
            {
                "visual_overrides": [],
                "token_collections": {
                    "core": {
                        "id": "core",
                        "name": "Core",
                        "modes": {
                            "light": {"--color-primary": "#ffffff"},
                            "brand": {"--color-primary": "var(--brand-primary)"},
                        },
                    }
                },
                "token_active_collection": "core",
                "token_active_mode": "brand",
            }
        )
        self.assertIn("core", payload["token_collections"])
        self.assertEqual(payload["token_active_collection"], "core")
        self.assertEqual(payload["token_active_mode"], "brand")

    def test_upsert_managed_visual_css_is_deterministic(self):
        source = "<template><div/></template>\n<style scoped>\n.a{color:red;}\n</style>"
        updated = upsert_managed_visual_css(source, ".x {\n  color: blue;\n}")
        managed = extract_managed_visual_css(updated)
        self.assertIn("color: blue", managed)

        updated_again = upsert_managed_visual_css(updated, ".x {\n  color: green;\n}")
        self.assertIn("color: green", extract_managed_visual_css(updated_again))
        self.assertNotIn("color: blue", extract_managed_visual_css(updated_again))

    def test_resolve_target_by_target_file_without_route(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            app_root = Path(tmp_dir) / "app"
            component_dir = app_root / "frontend" / "src" / "components"
            component_dir.mkdir(parents=True, exist_ok=True)
            component_file = component_dir / "AppHeader.vue"
            component_file.write_text("<template><header>H</header></template>", encoding="utf-8")

            with patch("mysite.management_editor.target_resolver.frappe.get_app_path", return_value=str(app_root / "mysite")):
                target = resolve_management_visual_editor_target("", target_file="frontend/src/components/AppHeader.vue")

            self.assertEqual(target.get("file_rel"), "frontend/src/components/AppHeader.vue")
            self.assertEqual(target.get("file_type"), "vue")
            self.assertTrue(str(target.get("route") or "").startswith("/mysite"))

    def test_save_wrapper_returns_json_validation_error(self):
        with patch.object(editor_api, "_save_management_visual_editor_changes_impl", side_effect=frappe.ValidationError("invalid")):
            payload = editor_api.save_management_visual_editor_changes(route="/mysite")
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("exc_type"), "ValidationError")

    def test_save_wrapper_returns_json_runtime_error(self):
        with patch.object(editor_api, "_save_management_visual_editor_changes_impl", side_effect=RuntimeError("boom")):
            payload = editor_api.save_management_visual_editor_changes(route="/mysite")
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("exc_type"), "RuntimeError")
        self.assertIn("message", payload)


if __name__ == "__main__":
    unittest.main()
