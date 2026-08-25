import unittest
from unittest.mock import MagicMock, patch

from mysite import management_audit


class TestManagementAudit(unittest.TestCase):
    def test_log_event_skips_when_doctype_missing(self):
        with patch.object(management_audit, "_doctype_exists", return_value=False), patch.object(
            management_audit.frappe, "get_doc"
        ) as get_doc_mock:
            management_audit.log_event(
                module_key="content",
                action_key="content.write",
                target_type="page_config",
                target_key="/mysite",
            )
        get_doc_mock.assert_not_called()

    def test_log_event_inserts_when_doctype_exists(self):
        insert_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.insert = insert_mock

        fake_request = MagicMock()
        fake_request.headers = {}
        fake_request.remote_addr = "127.0.0.1"

        with patch.object(management_audit, "_doctype_exists", return_value=True), patch.object(
            management_audit, "get_roles", return_value={"Mysite Content Editor"}
        ), patch.object(management_audit.frappe, "request", fake_request, create=True), patch.object(
            management_audit.frappe, "local", MagicMock(request_ip="127.0.0.1"), create=True
        ), patch.object(
            management_audit.frappe, "get_doc", return_value=doc_mock
        ):
            management_audit.log_event(
                module_key="content",
                action_key="content.write",
                target_type="page_config",
                target_key="/mysite",
                details={"ok": True},
            )

        insert_mock.assert_called_once_with(ignore_permissions=True)
