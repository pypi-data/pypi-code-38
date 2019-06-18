# -*- coding: utf-8 -*-

from __future__ import print_function

from mock import Mock

from django.test import TestCase
from django.http import HttpResponse
from django.test.client import RequestFactory
from django.middleware.common import CommonMiddleware

from tcell_agent.agent import TCellAgent
from tcell_agent.config.configuration import set_config, get_config
from tcell_agent.tests.support.free_native_agent import free_native_agent
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.afterauthmiddleware import AfterAuthMiddleware
from tcell_agent.tests.support.builders import ConfigurationBuilder

try:
    import django
    from django.conf import settings

    settings.configure()
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "mydatabase"
            }
        }
    django.setup()
except RuntimeError:
    print("Django already setup")

try:
    settings.configure()
except Exception:
    pass

settings.DEFAULT_CHARSET = "utf-8"


def update_agent_policies(policy_json):
    tCell_agent = TCellAgent.tCell_agent
    enablements = tCell_agent.native_agent.update_policies(
        policy_json
    ).get("enablements")
    tCell_agent.policies_manager.process_policies(
        enablements,
        policy_json
    )


# pylint: disable=no-member
class GlobalRequestMiddlewareTest(TestCase):
    def setUp(self):
        settings.ALLOWED_HOSTS = ["testserver", "test.tcell.io"]

        self.grm = GlobalRequestMiddleware()
        self.aam = AfterAuthMiddleware()
        self.cm = CommonMiddleware()

        rf = RequestFactory()
        self.request = rf.get("http://test.tcell.io/hello/")

        self.request.session = Mock()
        self.request.session.session_key = "101012301200123"

        configuration = ConfigurationBuilder().update_attribute(
            "reverse_proxy", True
        ).update_attribute(
            "api_key", "Test_-ApiKey=="
        ).update_attribute(
            "app_id", "TestAppId-AppId"
        ).update_attribute(
            "host_identifier", "TestHostIdentifier"
        ).update_attribute(
            "fetch_policies_from_tcell", False
        ).build()
        set_config(configuration)

        TCellAgent.tCell_agent = TCellAgent()
        TCellAgent.tCell_agent.create_native_agent()

    def tearDown(self):
        free_native_agent(TCellAgent.tCell_agent.native_agent.agent_ptr)
        set_config(None)
        TCellAgent.tCell_agent = None

    def test_session_id_is_added(self):
        self.assertEqual(self.grm.process_request(self.request), None)
        self.assertEqual(self.aam.process_request(self.request), None)
        self.assertEqual(self.request._tcell_context.session_id, "101012301200123")

    def test_remote_address_is_added(self):
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_address, "1.1.2.2")

    def test_reverse_proxy_is_added_single(self):
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_FORWARDED_FOR"] = "2.3.3.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_address, "2.3.3.2")

    def test_reverse_proxy_is_added_multiple(self):
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_FORWARDED_FOR"] = "2.2.2.2 ,3.3.3.3,4.4.4.4"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_address, "2.2.2.2")

    def test_reverse_proxy_is_igored(self):
        get_config().reverse_proxy = False
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_FORWARDED_FOR"] = "2.2.2.2,3.3.3.3,4.4.4.4"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_address, "1.1.2.2")

    def test_reverse_proxy_with_custom_header_name(self):
        get_config().reverse_proxy = True
        get_config().reverse_proxy_ip_address_header = "X-ReaL-IP"
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_REAL_IP"] = "2.2.2.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_address, "2.2.2.2")

    def test_reverse_proxy_with_custom_header_name_is_igored(self):
        get_config().reverse_proxy = False
        get_config().reverse_proxy_ip_address_header = "X-ReaL-IP"
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_REAL_IP"] = "2.2.2.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_address, "1.1.2.2")

    def test_redirect_normal(self):
        policy_json = {
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["whitelisted"],
                    "block": False
                }
            }
        }
        update_agent_policies(policy_json)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.session_id, "101012301200123")
        response = HttpResponse("hello world", content_type="application/html")
        response["Location"] = "http://www.yahoo.com/sam/5?x=asfasdfdsa"
        self.request._tcell_context.route_id = "-231123123"
        self.cm.process_response(self.request, response)
        self.grm.process_response(self.request, response)

        self.assertEqual(response["location"], "http://www.yahoo.com/sam/5?x=asfasdfdsa")

    def test_redirect_blocked(self):
        policy_json = {
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["*.google.com", "*yahoo"],
                    "block": True
                }
            }
        }
        update_agent_policies(policy_json)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.session_id, "101012301200123")
        response = HttpResponse("hello world", content_type="application/html")
        response["Location"] = "http://www.yahoo.com/sam/5?x=asfasdfdsa"
        self.request._tcell_context.route_id = "-231123123"

        self.cm.process_response(self.request, response)
        self.grm.process_response(self.request, response)

        self.assertEqual(response["location"], "/")

    def test_redirect_blocked_but_whitelisted(self):
        policy_json = {
            "http-redirect": {
                "version": 1,
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["*.google.com", "*.yahoo.com"],
                    "block": True
                }
            }
        }
        update_agent_policies(policy_json)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.session_id, "101012301200123")
        response = HttpResponse("hello world", content_type="application/html")
        response["Location"] = "http://www.yahoo.com/sam/5?x=asfasdfdsa"
        self.request._tcell_context.route_id = "-231123123"

        self.cm.process_response(self.request, response)
        self.grm.process_response(self.request, response)

        self.assertEqual(response["location"], "http://www.yahoo.com/sam/5?x=asfasdfdsa")
