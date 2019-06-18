import unittest

from mock import Mock, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.flaskinst.headers import flask_add_headers
from tcell_agent.tests.support.builders import ContextBuilder


class FlaskHeadersTest(unittest.TestCase):

    def test_flask_add_headers(self):
        tcell_context = ContextBuilder().update_attribute(
            "path", "GET"
        ).update_attribute(
            "method", "/"
        ).update_attribute(
            "route_id", "route_id"
        ).update_attribute(
            "session_id", "session_id"
        ).build()

        request = Mock(_tcell_context=tcell_context)
        response = Mock(headers={"Content-Type": "text/html"})

        mock = Mock()
        mock.get_headers = Mock(return_value=[{"name": "Content-Security-Policy",
                                               "value": "normalvalue; report-uri https://www.example.com/xys"}])
        with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
            flask_add_headers(request, response)
            patched_get_policy.assert_called_once_with(PolicyTypes.HEADERS)
            mock.get_headers.assert_called_once_with(tcell_context)
            self.assertEqual(response.headers,
                             {"Content-Security-Policy": "normalvalue; report-uri https://www.example.com/xys",
                              "Content-Type": "text/html"})

    def test_flask_add_header_with_existing_header(self):
        tcell_context = ContextBuilder().update_attribute(
            "path", "GET"
        ).update_attribute(
            "method", "/"
        ).update_attribute(
            "route_id", "route_id"
        ).update_attribute(
            "session_id", "session_id"
        ).build()

        request = Mock(_tcell_context=tcell_context)
        response = Mock(headers={"Content-Type": "text/html",
                                 "Content-Security-Policy": "default-src \"none\""})

        mock = Mock()
        mock.get_headers = Mock(return_value=[{"name": "Content-Security-Policy",
                                               "value": "normalvalue; report-uri https://www.example.com/xys"}])
        with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
            flask_add_headers(request, response)
            patched_get_policy.assert_called_once_with(PolicyTypes.HEADERS)
            mock.get_headers.assert_called_once_with(tcell_context)
            self.assertEqual(response.headers,
                             {"Content-Security-Policy": "default-src \"none\", normalvalue; report-uri https://www.example.com/xys",
                              "Content-Type": "text/html"})
