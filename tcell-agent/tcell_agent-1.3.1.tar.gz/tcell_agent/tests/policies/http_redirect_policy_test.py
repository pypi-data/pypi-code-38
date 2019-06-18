# -*- coding: utf-8 -*-

import unittest

from tcell_agent.policies.http_redirect_policy import HttpRedirectPolicy
from tcell_agent.rust.native_agent import create_native_agent
from tcell_agent.tests.support.builders import ConfigurationBuilder, ContextBuilder
from tcell_agent.tests.support.free_native_agent import free_native_agent


class HttpRedirectPolicyTest(unittest.TestCase):
    def setUp(self):
        configuration = ConfigurationBuilder().build()
        self.native_agent = create_native_agent(configuration)

    def tearDown(self):
        free_native_agent(self.native_agent.agent_ptr)

    def test_classname(self):
        self.assertEqual(HttpRedirectPolicy.api_identifier, "http-redirect")

    def test_large_header(self):
        policies_rsp = self.native_agent.update_policies({
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["whitelisted"],
                    "block": True
                }
            }
        })

        policy = HttpRedirectPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertEqual(policy.enabled, True)

    def test_same_domain_redirect(self):
        policies_rsp = self.native_agent.update_policies({
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["whitelisted"],
                    "block": True
                }
            }
        })

        policy = HttpRedirectPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertEqual(policy.enabled, True)
        context = ContextBuilder().update_attribute(
            "path", "/etc/123"
        ).update_attribute(
            "remote_address", "0.1.1.0"
        ).update_attribute(
            "fullpath", "/etc/123"
        ).build()
        check = policy.process_location(
            redirect_url="http://localhost:8011/abc/def",
            from_domain="localhost:8011",
            status_code=200,
            tcell_context=context)

        self.assertEqual(check, "http://localhost:8011/abc/def")

    def test_asterisk_in_domain_redirect(self):
        policies_rsp = self.native_agent.update_policies({
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["*.allowed*.com"],
                    "block": True
                }
            }
        })

        policy = HttpRedirectPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertEqual(policy.enabled, True)
        context = ContextBuilder().update_attribute(
            "path", "/etc/123"
        ).update_attribute(
            "remote_address", "0.1.1.0"
        ).update_attribute(
            "fullpath", "/etc/123"
        ).build()

        check = policy.process_location(
            redirect_url="http://allowed.com",
            from_domain="localhost:8011",
            status_code=200,
            tcell_context=context)
        self.assertEqual(check, "http://allowed.com")

        check = policy.process_location(
            redirect_url="http://www.alloweddomain.com",
            from_domain="localhost:8011",
            status_code=200,
            tcell_context=context)
        self.assertEqual(check, "http://www.alloweddomain.com")

    def test_domains_with_ports_should_be_removed(self):
        policies_rsp = self.native_agent.update_policies({
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": [],
                    "block": True
                }
            }
        })

        policy = HttpRedirectPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertEqual(policy.enabled, True)
        context = ContextBuilder().update_attribute(
            "path", "/some/path"
        ).update_attribute(
            "remote_address", "0.1.1.0"
        ).update_attribute(
            "fullpath", "/some/path"
        ).build()

        check = policy.process_location(
            redirect_url="http://user:pass@192.168.99.100:3000",
            from_domain="localhost:8011",
            status_code=200,
            tcell_context=context)
        self.assertEqual(check, "/")

    def test_data_scheme_allowed(self):
        policies_rsp = self.native_agent.update_policies({
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["whitelisted"],
                    "block": True,
                    "data_scheme_allowed": True
                }
            }
        })

        policy = HttpRedirectPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertEqual(policy.enabled, True)
        context = ContextBuilder().update_attribute(
            "path", "/some/path"
        ).update_attribute(
            "remote_address", "0.1.1.0"
        ).update_attribute(
            "fullpath", "/some/path"
        ).build()

        check = policy.process_location(
            redirect_url="data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K",
            from_domain="localhost:8011",
            status_code=200,
            tcell_context=context)
        self.assertEqual(check, "data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K")

    def test_data_scheme_not_allowed(self):
        policies_rsp = self.native_agent.update_policies({
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["whitelisted"],
                    "block": True,
                    "data_scheme_allowed": False
                }
            }
        })

        policy = HttpRedirectPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertEqual(policy.enabled, True)
        context = ContextBuilder().update_attribute(
            "path", "/some/path"
        ).update_attribute(
            "remote_address", "0.1.1.0"
        ).update_attribute(
            "fullpath", "/some/path"
        ).build()

        check = policy.process_location(
            redirect_url="data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K",
            from_domain="localhost:8011",
            status_code=200,
            tcell_context=context)
        self.assertEqual(check, "/")

    def test_relative_redirect(self):
        policies_rsp = self.native_agent.update_policies({
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": [],
                    "block": True
                }
            }
        })

        policy = HttpRedirectPolicy(self.native_agent, policies_rsp["enablements"], None)
        self.assertEqual(policy.enabled, True)
        context = ContextBuilder().update_attribute(
            "path", "/some/path"
        ).update_attribute(
            "remote_address", "0.1.1.0"
        ).update_attribute(
            "fullpath", "/some/path"
        ).build()

        check = policy.process_location(
            redirect_url="/admin/login/?next=/admin/",
            from_domain="localhost:8011",
            status_code=200,
            tcell_context=context)
        self.assertEqual(check, "/admin/login/?next=/admin/")
