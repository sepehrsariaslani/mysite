import unittest
from types import SimpleNamespace
from unittest.mock import patch

from mysite import api


class TestManagementApiWorkflow(unittest.TestCase):
    def test_publish_dispatches_product_primary_image_operation(self):
        doc = SimpleNamespace(target_type="product_media_primary", target_key="ITEM-100", request_payload_json="{}")
        with patch.object(api, "parse_request_payload", return_value={"item_code": "ITEM-100", "file_url": "/files/a.jpg"}), patch.object(
            api,
            "set_management_product_primary_image",
            return_value={"ok": True},
        ) as primary_mock:
            result = api._apply_change_request_publish(doc)

        self.assertEqual(result, {"ok": True})
        primary_mock.assert_called_once()
        called_kwargs = primary_mock.call_args.kwargs
        self.assertEqual(called_kwargs.get("item_code"), "ITEM-100")
        self.assertEqual(called_kwargs.get("file_url"), "/files/a.jpg")

    def test_publish_raises_on_unsupported_target(self):
        doc = SimpleNamespace(target_type="unknown_target", target_key="KEY", request_payload_json="{}")
        with patch.object(api, "parse_request_payload", return_value={}):
            with self.assertRaises(Exception):
                api._apply_change_request_publish(doc)
