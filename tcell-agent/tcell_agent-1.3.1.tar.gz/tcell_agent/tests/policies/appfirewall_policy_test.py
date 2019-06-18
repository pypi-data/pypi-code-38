import unittest

from mock import Mock, patch

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appfirewall_policy import AppfirewallPolicy
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.rust.native_agent import create_native_agent
from tcell_agent.tests.support.free_native_agent import free_native_agent


class AppSensorPolicyTest(unittest.TestCase):
    def test_classname(self):
        self.assertEqual(AppfirewallPolicy.api_identifier, "appsensor")

    def test_empty_enablements_and_policies_json(self):
        policy = AppfirewallPolicy(None, {}, {})

        self.assertFalse(policy.instrument_database_queries)
        self.assertFalse(policy.appfirewall_enabled)

    def test_check_appfirewall_injections_with_disabled_policy(self):
        native_agent = Mock()
        policy = AppfirewallPolicy(native_agent, {}, {})

        with patch.object(native_agent, "apply_appfirewall", return_value=None) as patched_apply_appfirewall:
            policy.check_appfirewall_injections(AppSensorMeta())

            self.assertFalse(patched_apply_appfirewall.called)

    def test_check_appfirewall_injections_with_enabled_policy(self):
        configuration = ConfigurationBuilder().build()
        native_agent = create_native_agent(configuration)
        policy = AppfirewallPolicy(native_agent, {"appfirewall": True}, {})

        result = policy.check_appfirewall_injections(AppSensorMeta())
        free_native_agent(native_agent.agent_ptr)
        self.assertEqual(result, {})

    def test_instrument_database_queries(self):
        policy = AppfirewallPolicy(
            None,
            {},
            {
                "appsensor": {
                    "data": {
                        "sensors": {
                            "database": {
                                "large_result": {
                                    "limit": 10
                                }
                            }
                        }
                    }
                }
            })

        self.assertTrue(policy.instrument_database_queries)
        self.assertFalse(policy.appfirewall_enabled)
