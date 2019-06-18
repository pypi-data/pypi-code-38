import unittest

from mock import Mock, patch

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.flaskinst.meta import create_meta, \
    initialize_tcell_context, update_meta_with_response
from tcell_agent.sanitize.sanitize_utils import USE_PYTHON_2_HASH
from tcell_agent.tests.support.builders import ConfigurationBuilder
from tcell_agent.tests.support.context_library import ConfigContext
from tcell_agent.utils.multi_value_dict import MultiValueDict


class MetaTest(unittest.TestCase):
    def test_create_meta(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.remote_address = "1.2.3.4"
        tcell_context.route_id = "12345"
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        a_file = Mock(filename="file1")

        request = Mock(
            json=None,
            encoding="utf-8",
            content_length=0,
            _tcell_context=tcell_context,
            files=MultiValueDict({"param1": [a_file]}),
            form=MultiValueDict({"form_param_name": ["form_param_value1", "form_param_value2"]}),
            cookies={},
            view_args={},
            url="/",
            path="/",
            environ={"REQUEST_METHOD": "GET"},
            args=MultiValueDict({"query_param_name": ["query_param_value1", "query_param_value2"]}))

        create_meta(request)

        self.assertIsNotNone(request._appsensor_meta)

        appsensor_meta = request._appsensor_meta
        self.assertEqual(appsensor_meta.remote_address, "1.2.3.4")
        self.assertEqual(appsensor_meta.method, "GET")
        self.assertEqual(appsensor_meta.user_agent_str, None)
        self.assertEqual(appsensor_meta.location, "/")
        self.assertEqual(appsensor_meta.path, "/")
        self.assertEqual(appsensor_meta.route_id, "12345")
        self.assertEqual(appsensor_meta.get_dict,
                         MultiValueDict({"query_param_name": ["query_param_value1", "query_param_value2"]}))
        self.assertEqual(appsensor_meta.cookie_dict, {})
        self.assertEqual(appsensor_meta.request_content_bytes_len, 0)
        self.assertEqual(appsensor_meta.post_dict,
                         MultiValueDict({"form_param_name": ["form_param_value1", "form_param_value2"]}))
        self.assertEqual(appsensor_meta.path_dict, {})
        self.assertEqual(appsensor_meta.files_dict, MultiValueDict({"param1": ["file1"]}))
        self.assertEqual(appsensor_meta.headers_dict, {})

    def test_update_meta_with_response(self):
        appsensor_meta = AppSensorMeta()

        response = Mock(content_length=0)

        update_meta_with_response(appsensor_meta, response, 302)

        self.assertEqual(appsensor_meta.response_code, 302)
        self.assertEqual(appsensor_meta.response_content_bytes_len, 0)

    def test_initialize_tcell_context(self):
        request = Mock(
            environ={
                "REMOTE_ADDR": "192.168.1.115",
                "REQUEST_METHOD": "GET",
                "HTTP_USER_AGENT": "Mozilla"},
            url_rule=Mock(rule="/"))

        with ConfigContext(ConfigurationBuilder().build()):
            with patch("tcell_agent.instrumentation.flaskinst.meta.start_timer") as patched_start_timer:
                initialize_tcell_context(request)

                self.assertTrue(patched_start_timer.called)
                self.assertIsNotNone(request._tcell_context)

                context = request._tcell_context

                self.assertEqual("Mozilla", context.user_agent)
                self.assertEqual("192.168.1.115", context.remote_address)
                if USE_PYTHON_2_HASH:
                    self.assertEqual("-8927252616038890182", context.route_id)
                else:
                    self.assertEqual("98246921", context.route_id)
