import unittest
from types import SimpleNamespace
from unittest.mock import patch

from mysite import management_workflow as workflow


class TestManagementWorkflow(unittest.TestCase):
    def test_state_machine_valid_transitions(self):
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Draft"), "submit_review"), "In Review")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="In Review"), "approve"), "Approved")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="In Review"), "reject"), "Rejected")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Approved"), "publish"), "Published")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="In Review"), "return_to_draft"), "Draft")

    def test_publish_is_only_allowed_after_approval(self):
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Draft"), "publish"), "")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="In Review"), "publish"), "")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Rejected"), "publish"), "")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Approved"), "publish"), "Published")

    def test_cancel_allowed_states(self):
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Draft"), "cancel"), "Cancelled")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="In Review"), "cancel"), "Cancelled")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Approved"), "cancel"), "Cancelled")
        self.assertEqual(workflow._allowed_transition(SimpleNamespace(state="Published"), "cancel"), "")

    def test_should_enforce_obeys_shadow_and_bypass_rules(self):
        mode = {"enforce_workflow": True, "allow_system_manager_bypass": True}
        with patch.object(workflow, "workflow_mode", return_value=mode), patch.object(
            workflow, "is_super_admin", return_value=True
        ):
            self.assertFalse(workflow.should_enforce("content", user="administrator", bypass_requested=True))

        with patch.object(workflow, "workflow_mode", return_value=mode), patch.object(
            workflow, "is_super_admin", return_value=False
        ):
            self.assertTrue(workflow.should_enforce("content", user="editor", bypass_requested=False))
            self.assertFalse(workflow.should_enforce("analytics", user="editor", bypass_requested=False))

    def test_shadow_mode_creates_published_record(self):
        mode = {"shadow_mode": True}
        with patch.object(workflow, "workflow_mode", return_value=mode), patch.object(
            workflow, "create_change_request", return_value={"name": "CR-0001", "state": "Published", "available": True}
        ) as create_mock:
            output = workflow.shadow_create_if_enabled(
                module_key="product",
                target_type="product_update",
                target_key="ITEM-001",
                request_payload={"item_code": "ITEM-001"},
                current_snapshot={"item_code": "ITEM-001"},
                source_endpoint="save_management_product",
            )

        self.assertEqual(output.get("name"), "CR-0001")
        self.assertEqual(output.get("state"), "Published")
        self.assertTrue(create_mock.called)
        kwargs = create_mock.call_args.kwargs
        self.assertEqual(kwargs["initial_state"], "Published")
        self.assertTrue(kwargs["is_shadow_record"])

    def test_shadow_mode_off_returns_no_record(self):
        with patch.object(workflow, "workflow_mode", return_value={"shadow_mode": False}):
            output = workflow.shadow_create_if_enabled(
                module_key="content",
                target_type="page_config",
                target_key="/mysite",
                request_payload={},
            )
        self.assertFalse(output.get("available"))
        self.assertEqual(output.get("state"), "Published")
