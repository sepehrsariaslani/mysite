import unittest
from unittest.mock import patch

from mysite import management_permissions as permissions


class TestManagementPermissions(unittest.TestCase):
    def test_system_manager_has_all_capabilities(self):
        with patch.object(permissions, "get_roles", return_value={"System Manager"}):
            capabilities = permissions.get_capabilities("administrator@example.com")
        self.assertEqual(capabilities, set(permissions.CAPABILITY_ROLE_MAP))

    def test_website_manager_keeps_legacy_access(self):
        with patch.object(permissions, "get_roles", return_value={"Website Manager"}):
            capabilities = permissions.get_capabilities("manager@example.com")
        self.assertEqual(capabilities, set(permissions.CAPABILITY_ROLE_MAP))

    def test_content_reviewer_capability_matrix(self):
        with patch.object(permissions, "get_roles", return_value={"Mysite Content Reviewer"}):
            capabilities = permissions.get_capabilities("reviewer@example.com")
        self.assertIn("management.access", capabilities)
        self.assertIn("content.edit", capabilities)
        self.assertIn("content.review", capabilities)
        self.assertNotIn("content.publish", capabilities)
        self.assertNotIn("product.edit", capabilities)

    def test_product_publisher_capability_matrix(self):
        with patch.object(permissions, "get_roles", return_value={"Mysite Product Publisher"}):
            capabilities = permissions.get_capabilities("publisher@example.com")
        self.assertIn("management.access", capabilities)
        self.assertIn("product.edit", capabilities)
        self.assertIn("product.review", capabilities)
        self.assertIn("product.publish", capabilities)
        self.assertNotIn("content.edit", capabilities)

    def test_has_capability_returns_false_for_guest(self):
        self.assertFalse(permissions.has_capability("content.edit", user="Guest"))
