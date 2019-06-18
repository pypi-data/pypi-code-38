import unittest

from mock import Mock, call, patch

from tcell_agent.policies.policy_polling import PolicyPolling, call_update
from tcell_agent.tests.support.builders import ConfigurationBuilder


class EnsurePollingThreadRunningTest(unittest.TestCase):
    def setUp(self):
        self.policies_manager_mock = Mock()
        self.native_agent_mock = Mock()

    def test_empty_tcell_api_url(self):
        config = ConfigurationBuilder().update_attribute(
            "app_id", "TestApp-id"
        ).update_attribute(
            "api_key", "TestApi-key"
        ).update_attribute(
            "tcell_api_url", None
        ).update_attribute(
            "fetch_policies_from_tcell", True
        ).build()
        policy_polling = PolicyPolling(self.policies_manager_mock, config)
        with patch.object(policy_polling, "start_polling_thread") as patched_start_polling_thread:
            policy_polling.ensure_polling_thread_running(self.native_agent_mock)
            self.assertFalse(patched_start_polling_thread.called)

    def test_empty_app_id(self):
        config = ConfigurationBuilder().update_attribute(
            "app_id", None
        ).update_attribute(
            "api_key", "TestApi-key"
        ).update_attribute(
            "tcell_api_url", "tcell-api-url"
        ).update_attribute(
            "fetch_policies_from_tcell", True
        ).build()
        policy_polling = PolicyPolling(self.policies_manager_mock, config)
        with patch.object(policy_polling, "start_polling_thread") as patched_start_polling_thread:
            policy_polling.ensure_polling_thread_running(self.native_agent_mock)
            self.assertFalse(patched_start_polling_thread.called)

    def test_empty_api_key(self):
        config = ConfigurationBuilder().update_attribute(
            "app_id", "TestApp-id"
        ).update_attribute(
            "api_key", None
        ).update_attribute(
            "tcell_api_url", "tcell-api-url"
        ).update_attribute(
            "fetch_policies_from_tcell", True
        ).build()
        policy_polling = PolicyPolling(self.policies_manager_mock, config)
        with patch.object(policy_polling, "start_polling_thread") as patched_start_polling_thread:
            policy_polling.ensure_polling_thread_running(self.native_agent_mock)
            self.assertFalse(patched_start_polling_thread.called)

    def test_fetch_policies_is_disabled(self):
        config = ConfigurationBuilder().update_attribute(
            "app_id", "TestApp-id"
        ).update_attribute(
            "api_key", "TestApi-key"
        ).update_attribute(
            "tcell_api_url", "tcell-api-url"
        ).update_attribute(
            "fetch_policies_from_tcell", False
        ).build()
        policy_polling = PolicyPolling(self.policies_manager_mock, config)
        with patch.object(policy_polling, "start_polling_thread") as patched_start_polling_thread:
            policy_polling.ensure_polling_thread_running(self.native_agent_mock)
            self.assertFalse(patched_start_polling_thread.called)

    def test_policy_polling_already_running(self):
        config = ConfigurationBuilder().update_attribute(
            "app_id", "TestApp-id"
        ).update_attribute(
            "api_key", "TestApi-key"
        ).update_attribute(
            "tcell_api_url", "tcell-api-url"
        ).update_attribute(
            "fetch_policies_from_tcell", True
        ).build()
        policy_polling = PolicyPolling(self.policies_manager_mock, config)
        with patch.object(policy_polling, "is_polling_thread_running", return_value=True) as patched_is_polling_thread_running:
            with patch.object(policy_polling, "start_polling_thread") as patched_start_polling_thread:
                policy_polling.ensure_polling_thread_running(self.native_agent_mock)
                self.assertTrue(patched_is_polling_thread_running.called)
                self.assertFalse(patched_start_polling_thread.called)

    def test_ensure_polling_thread_running(self):
        config = ConfigurationBuilder().update_attribute(
            "app_id", "TestApp-id"
        ).update_attribute(
            "api_key", "TestApi-key"
        ).update_attribute(
            "tcell_api_url", "tcell-api-url"
        ).update_attribute(
            "fetch_policies_from_tcell", True
        ).build()
        policy_polling = PolicyPolling(self.policies_manager_mock, config)
        with patch.object(policy_polling, "is_polling_thread_running", return_value=False) as patched_is_polling_thread_running:
            with patch.object(policy_polling, "start_polling_thread") as patched_start_polling_thread:
                policy_polling.ensure_polling_thread_running(self.native_agent_mock)
                self.assertTrue(patched_is_polling_thread_running.called)
                self.assertTrue(patched_start_polling_thread.called)


class CallUpdateTest(unittest.TestCase):
    def test_call_update(self):
        process_policies_mock = Mock()
        policies_manager_mock = Mock(process_policies=process_policies_mock)
        response = {
            "new_policies_and_enablements": {
                "enablements": "enablements-results",
                "policies": "policies-results"
            }
        }
        request_policies_mock = Mock(return_value=response)
        native_agent_mock = Mock(request_policies=request_policies_mock)
        call_update(native_agent_mock, policies_manager_mock)

        self.assertEqual(process_policies_mock.call_args_list,
                         [call("enablements-results", "policies-results")])
