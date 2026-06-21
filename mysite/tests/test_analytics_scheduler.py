import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from mysite import analytics_scheduler


class _CacheStub:
    def __init__(self):
        self._store = {}

    def get_value(self, key):
        return self._store.get(key)

    def set_value(self, key, value, expires_in_sec=None):
        self._store[key] = value


class TestAnalyticsScheduler(unittest.TestCase):
    def test_operator_eval(self):
        self.assertTrue(analytics_scheduler._operator_eval(1, "<", 2))
        self.assertTrue(analytics_scheduler._operator_eval(2, "<=", 2))
        self.assertTrue(analytics_scheduler._operator_eval(2, "=", 2))
        self.assertTrue(analytics_scheduler._operator_eval(3, ">", 2))
        self.assertTrue(analytics_scheduler._operator_eval(3, ">=", 3))
        self.assertFalse(analytics_scheduler._operator_eval(2, "<", 1))

    def test_evaluate_alert_rules_dedupes_notifications(self):
        cache = _CacheStub()
        insert_mock = MagicMock()
        sendmail_mock = MagicMock()

        rule = {
            "name": "RULE-001",
            "metric_key": "conversion_rate",
            "operator": "<",
            "threshold_value": 5,
            "window_days": 7,
            "notify_email": 1,
            "notify_notification_log": 1,
            "recipients": "",
        }
        doc = SimpleNamespace(insert=insert_mock)

        with patch.object(analytics_scheduler.frappe.db, "exists", return_value=True), patch.object(
            analytics_scheduler.frappe, "get_all", return_value=[rule]
        ), patch.object(
            analytics_scheduler, "_metric_evaluation", return_value={"current": 1.0, "message": "msg"}
        ), patch.object(
            analytics_scheduler, "_alert_recipients", return_value=["admin@example.com"]
        ), patch.object(
            analytics_scheduler.frappe, "cache", return_value=cache
        ), patch.object(
            analytics_scheduler.frappe, "get_doc", return_value=doc
        ), patch.object(
            analytics_scheduler.frappe, "sendmail", sendmail_mock
        ), patch.object(
            analytics_scheduler.frappe.db, "commit", return_value=None
        ):
            analytics_scheduler.evaluate_alert_rules()
            analytics_scheduler.evaluate_alert_rules()

        # First run should notify; second run should be skipped by daily dedupe key.
        insert_mock.assert_called_once()
        sendmail_mock.assert_called_once()
