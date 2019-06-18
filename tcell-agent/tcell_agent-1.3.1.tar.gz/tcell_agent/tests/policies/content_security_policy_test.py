import unittest

from tcell_agent.policies.headers_policy import HeadersPolicy
from tcell_agent.rust.native_agent import create_native_agent
from tcell_agent.tests.support.builders import ConfigurationBuilder, ContextBuilder
from tcell_agent.tests.support.free_native_agent import free_native_agent


class ContentSecurityPolicyTest(unittest.TestCase):
    def setUp(self):
        configuration = ConfigurationBuilder().update_attribute(
            "max_csp_header_bytes", 105
        ).build()
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
            "csp-headers": {
                "version": 1,
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "test321"}]}})

        policy = HeadersPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertTrue(policy.headers_enabled)
        self.assertEqual(policy.get_headers(self.tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "test321"}])

    def test_header_with_report_uri(self):
        policies_rsp = self.native_agent.update_policies({
            "csp-headers": {
                "version": 1,
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "normalvalue",
                             "report_uri": "https://www.example.com/xys"}]}})

        policy = HeadersPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertTrue(policy.headers_enabled)
        self.assertEqual(policy.get_headers(self.tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "normalvalue; report-uri https://www.example.com/xys?sid=ab7074d0bf86c2884766d88b6ad9de4a&rid=route-id"}])

    def test_header_equal_to_max_csp_header_bytes(self):
        policies_rsp = self.native_agent.update_policies({
            "csp-headers": {
                "version": 1,
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "normalvalue",
                             "report_uri": "https://www.example.com/1234567"}]}})

        policy = HeadersPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertTrue(policy.headers_enabled)
        self.assertEqual(policy.get_headers(self.tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "normalvalue; report-uri https://www.example.com/1234567?sid=ab7074d0bf86c2884766d88b6ad9de4a&rid=route-id"}])

    def test_header_exceeding_max_csp_header_bytes(self):
        policies_rsp = self.native_agent.update_policies({
            "csp-headers": {
                "version": 1,
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "normalvalue",
                             "report_uri": "https://www.example.com/12345678"}]}})
        policy = HeadersPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertTrue(policy.headers_enabled)
        # no headers returned because they are bigger than max_csp_header_bytes
        self.assertEqual(policy.get_headers(self.tcell_context), [])
