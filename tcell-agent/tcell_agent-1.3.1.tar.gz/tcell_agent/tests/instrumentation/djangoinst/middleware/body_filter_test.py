# -*- coding: utf-8 -*-

from __future__ import print_function

from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpResponse
from django.middleware.common import CommonMiddleware

try:
    import django
    from django.conf import settings

    settings.configure()
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "mydatabase",
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

from mock import Mock

from tcell_agent.agent import TCellAgent
from tcell_agent.config.configuration import set_config
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.afterauthmiddleware import AfterAuthMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.body_filter_middleware import BodyFilterMiddleware
from tcell_agent.tests.support.free_native_agent import free_native_agent
from tcell_agent.tests.support.builders import ConfigurationBuilder


def update_agent_policies(policy_json):
    tCell_agent = TCellAgent.tCell_agent
    enablements = tCell_agent.native_agent.update_policies(
        policy_json
    ).get("enablements")
    tCell_agent.policies_manager.process_policies(
        enablements,
        policy_json
    )


class BodyFilterMiddlewareTest(TestCase):
    _multiprocess_can_split_ = False

    def setUp(self):
        settings.ALLOWED_HOSTS = ["testserver", "test.tcell.io"]

        self.grm = GlobalRequestMiddleware()
        self.aam = AfterAuthMiddleware()
        self.cmw = CommonMiddleware()
        self.bfm = BodyFilterMiddleware()

        request_factory = RequestFactory()
        self.request = request_factory.get("http://test.tcell.io/hello/")

        self.request.session = Mock()
        self.request.session.session_key = "101012301200123"

        configuration = ConfigurationBuilder().update_attribute(
            "js_agent_api_base_url", "http://api.tcell.com/"
        ).update_attribute(
            "js_agent_url", "https://jsagent.tcell.io/tcellagent.min.js"
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

    def test_body_inject(self):
        policy_json = {
            "jsagentinjection": {
                "excludes": [],
                "enabled": True,
                "state": "Enabled",
                "version": 1,
                "api_key": "000-000-1-2323",
                "policy_id": "jsagentinjection-v1-47"
            },
        }
        update_agent_policies(policy_json)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cmw.process_request(self.request)
        response = HttpResponse("<html>\n<head>Title</head><body>hello world</body><html>", content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cmw.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"<html>\n<head><script src=\"https://jsagent.tcell.io/tcellagent.min.js\" " + \
            b"tcellappid=\"TestAppId-AppId\" tcellapikey=\"000-000-1-2323\" tcellbaseurl=\"http://api.tcell.com/\"" + \
            b"></script>Title</head><body>hello world</body><html>"
        self.assertEqual(response.content, expected)

    def test_non_html_body_inject(self):
        policy_json = {
            "csp-headers": {
                "policy_id": "nyzd",
                "data": {
                    "options": {
                        "js_agent_api_key": "000-000-1-2323"
                    }
                }
            }
        }
        update_agent_policies(policy_json)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cmw.process_request(self.request)
        resp = b"\x08\x01\x10\x01(\xc1\xca\x03JN\n\tajaxtoken\x1282cfc663150b955a7b8aad324f33364d5965f1a7397a545df76dea8bf\x18\x00 \x80\xc4\xff\x0e"
        response = HttpResponse(resp, content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cmw.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"""\x08\x01\x10\x01(\xc1\xca\x03JN\n\tajaxtoken\x1282cfc663150b955a7b8aad324f33364d5965f1a7397a545df76dea8bf\x18\x00 \x80\xc4\xff\x0e"""
        self.assertEqual(response.content, expected)

    def test_utf8_html_body_inject(self):
        policy_json = {
            "jsagentinjection": {
                "excludes": [],
                "enabled": True,
                "state": "Enabled",
                "version": 1,
                "api_key": "000-000-1-2323",
                "policy_id": "jsagentinjection-v1-47"
            },
        }
        update_agent_policies(policy_json)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cmw.process_request(self.request)
        response = HttpResponse(u"<html>\n<head>Müller</head><body>holá mundo</body><html>", content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cmw.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"<html>\n<head><script src=\"https://jsagent.tcell.io/tcellagent.min.js\" " + \
            b"tcellappid=\"TestAppId-AppId\" tcellapikey=\"000-000-1-2323\" tcellbaseurl=\"http://api.tcell.com/\"" + \
            b"></script>M\xc3\xbcller</head><body>hol\xc3\xa1 mundo</body><html>"
        self.assertEqual(response.content, expected)

    def test_jsagent_inserted_once_with_multiple_head_tags(self):
        policy_json = {
            "jsagentinjection": {
                "excludes": [],
                "enabled": True,
                "state": "Enabled",
                "version": 1,
                "api_key": "000-000-1-2323",
                "policy_id": "jsagentinjection-v1-47"
            },
        }
        update_agent_policies(policy_json)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cmw.process_request(self.request)
        response = HttpResponse(u"<html>\n<head>foo</head><body></body><head>bar</head><html>", content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cmw.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"<html>\n<head><script src=\"https://jsagent.tcell.io/tcellagent.min.js\" " + \
            b"tcellappid=\"TestAppId-AppId\" tcellapikey=\"000-000-1-2323\" tcellbaseurl=\"http://api.tcell.com/\"" + \
            b"></script>foo</head><body></body><head>bar</head><html>"
        self.assertEqual(response.content, expected)
