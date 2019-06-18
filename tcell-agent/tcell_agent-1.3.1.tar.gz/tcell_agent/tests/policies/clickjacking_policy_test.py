import unittest

from tcell_agent.policies.headers_policy import HeadersPolicy
from tcell_agent.rust.native_agent import create_native_agent
from tcell_agent.tests.support.builders import ConfigurationBuilder, ContextBuilder
from tcell_agent.tests.support.free_native_agent import free_native_agent


class ClickjackingPolicyTest(unittest.TestCase):
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

    def test_new_header(self):
        policies_rsp = self.native_agent.update_policies({
            "clickjacking": {
                "policy_id": "890f1310-5c6c-11e8-8080-808080808080",
                "headers": [
                    {
                        "name": "Content-Security-Policy",
                        "value": "frame-ancestors 'none'",
                        "report_uri": "https://input.tcell-preview.io/csp/430d"
                    }
                ],
                "version": 1
            }
        })
        policy = HeadersPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertTrue(policy.headers_enabled)
        self.assertEqual(policy.get_headers(self.tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "frame-ancestors 'none'; report-uri https://input.tcell-preview.io/csp/430d?sid=ab7074d0bf86c2884766d88b6ad9de4a&rid=route-id"}])
