import unittest

from tcell_agent.policies.headers_policy import HeadersPolicy
from tcell_agent.rust.native_agent import create_native_agent
from tcell_agent.tests.support.builders import ConfigurationBuilder, ContextBuilder
from tcell_agent.tests.support.free_native_agent import free_native_agent


class SecureHeaderPolicyTest(unittest.TestCase):
    def setUp(self):
        configuration = ConfigurationBuilder().build()
        self.native_agent = create_native_agent(configuration)
        self.tcell_context = ContextBuilder().update_attribute(
            "session-id", "session-id"
        ).update_attribute(
            "route-id", "12345"
        ).build()

    def tearDown(self):
        free_native_agent(self.native_agent.agent_ptr)

    def test_classname(self):
        self.assertEqual(HeadersPolicy.api_identifier, "headers")

    def test_one_header(self):
        policies_rsp = self.native_agent.update_policies({
            "secure-headers": {
                "version": 1,
                "policy_id": "xyzd",
                "headers": [{"name": "X-Content-Type-Options",
                             "value": "nosniff"}]}})

        policy = HeadersPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertTrue(policy.headers_enabled)
        self.assertEqual(policy.get_headers(self.tcell_context),
                         [{"name": "X-Content-Type-Options", "value": "nosniff"}])
