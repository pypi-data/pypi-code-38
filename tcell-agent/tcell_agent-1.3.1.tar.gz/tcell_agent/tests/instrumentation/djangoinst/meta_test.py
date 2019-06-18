import unittest

from django.utils.datastructures import MultiValueDict
from mock import MagicMock, patch

from tcell_agent.instrumentation.djangoinst.meta import MAXIMUM_BODY_SIZE, \
    initialize_tcell_context, get_appsensor_meta, set_response, \
    parse_body, set_request
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation.djangoinst.models import TCellDjangoRequest
from tcell_agent.tests.support.builders import ContextBuilder


class InitializeTcellContextTest(unittest.TestCase):
    def test_initialize_tcell_context(self):
        request = MagicMock()
        request.META = MagicMock(return_value={"HTTP_REFERER": "referrer",
                                               "HTTP_USER_AGENT": "user-agent"})
        request.method = MagicMock(return_value="GET")
        request.path = MagicMock(return_value="/some/path")
        request.get_full_path = MagicMock(return_value="/some/path?param=hi")
        request.build_absolute_uri = MagicMock(return_value="http://localhost/some/path?param=hi")
        with patch("tcell_agent.instrumentation.djangoinst.meta.better_ip_address",
                   return_value="1.1.1.1") as patched_better_ip_address:
            initialize_tcell_context(request)
            tcell_context = request._tcell_context
            self.assertTrue(patched_better_ip_address.called)
            self.assertIsNotNone(tcell_context.referrer, "referrer")
            self.assertIsNotNone(tcell_context.user_agent, "user-agent")
            self.assertIsNotNone(tcell_context.remote_address, "1.1.1.1")
            self.assertIsNotNone(tcell_context.method, "GET")
            self.assertIsNotNone(tcell_context.path, "/some/path")
            self.assertIsNotNone(tcell_context.fullpath, "/some/path?param=hi")
            self.assertIsNotNone(tcell_context.uri, "http://localhost/some/path?param=hi")
            self.assertIsNone(tcell_context.route_id)


class GetAppsensorMetaTest(unittest.TestCase):
    class FakeRequest(object):
        def __init__(self, tcell_context, encoding):
            self._tcell_context = tcell_context
            self.encoding = encoding

    def test_get_appsensor_meta(self):
        tcell_context = ContextBuilder().update_attribute(
            "remote_address", "1.1.1.1"
        ).update_attribute(
            "method", "GET"
        ).update_attribute(
            "user_agent", "user-agent"
        ).update_attribute(
            "uri", "http://localhost/some/path?param=hi"
        ).update_attribute(
            "path", "/some/path"
        ).update_attribute(
            "route_id", None
        ).update_attribute(
            "session_id", "session-id"
        ).update_attribute(
            "user_id", "user-id"
        ).build()
        request = self.FakeRequest(tcell_context, "UTF-8")

        appsensor_meta = get_appsensor_meta(request)
        self.assertEqual(appsensor_meta.remote_address, "1.1.1.1")
        self.assertEqual(appsensor_meta.method, "GET")
        self.assertEqual(appsensor_meta.user_agent_str, "user-agent")
        self.assertEqual(appsensor_meta.location, "http://localhost/some/path?param=hi")
        self.assertEqual(appsensor_meta.path, "/some/path")
        self.assertEqual(appsensor_meta.route_id, None)
        self.assertEqual(appsensor_meta.session_id, "session-id")
        self.assertEqual(appsensor_meta.user_id, "user-id")
        self.assertEqual(appsensor_meta.encoding, "UTF-8")


class SetResponseTest(unittest.TestCase):
    class FakeResponse(object):
        def __init__(self, status_code, content):
            self.status_code = status_code
            self.content = content

    def test_set_response(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.response_processed = True
        appsensor_meta.response_content_bytes_len = -1
        appsensor_meta.response_code = "500"
        set_response(
            appsensor_meta,
            self.FakeResponse,
            self.FakeResponse("200", "")
        )
        self.assertTrue(appsensor_meta.response_processed)
        self.assertEqual(appsensor_meta.response_content_bytes_len, -1)
        self.assertEqual(appsensor_meta.response_code, "500")

        appsensor_meta.response_processed = False
        set_response(
            appsensor_meta,
            self.FakeResponse,
            self.FakeResponse("200", "some content")
        )
        self.assertTrue(appsensor_meta.response_processed)
        self.assertEqual(appsensor_meta.response_content_bytes_len, 12)
        self.assertEqual(appsensor_meta.response_code, "200")


class ParseBodyTest(unittest.TestCase):
    class FakeRequest(object):
        def __init__(self, content_type, post_dict, body):
            self.META = {
                "CONTENT_TYPE": content_type
            }
            self.POST = post_dict
            self.body = body
            self.FILES = None

    def test_content_length_is_none(self):
        req = TCellDjangoRequest(self.FakeRequest("application/text", {"post": "value"}, ""))
        req.content_length = None
        post_body, json_dict = parse_body(req)
        self.assertEqual(post_body, {"post": "value"})
        self.assertEqual(json_dict, None)

    def test_content_length_is_zero(self):
        req = TCellDjangoRequest(self.FakeRequest("application/text", {"post": "value"}, ""))
        req.content_length = 0
        post_body, json_dict = parse_body(req)
        self.assertEqual(post_body, {"post": "value"})
        self.assertEqual(json_dict, None)

    def test_content_length_exceeds_maximum(self):
        req = TCellDjangoRequest(self.FakeRequest("application/text", {"post": "value"}, ""))
        req.content_length = MAXIMUM_BODY_SIZE
        post_body, json_dict = parse_body(req)
        self.assertEqual(post_body, {"post": "value"})
        self.assertEqual(json_dict, None)

    def test_content_type_is_multipart(self):
        body = "boundary---- alkdsjfladjf ----\n\rContent-Disposition: form-data; post=\"value\""
        request = self.FakeRequest("Multipart/Form-Data; UTF-8",
                                   {"post": "value"},
                                   body)
        tcell_request = TCellDjangoRequest(request)
        tcell_request.content_length = len(request.body)
        post_body, json_dict = parse_body(tcell_request)
        self.assertEqual(post_body, {"post": "value"})
        self.assertEqual(json_dict, body)

    def test_parse_body(self):
        request = self.FakeRequest("application/Json; UTF-8",
                                   None,
                                   "{\"param\":\"val\"}")
        tcell_request = TCellDjangoRequest(request)
        tcell_request.content_length = len(request.body)
        post_dict, request_body = parse_body(tcell_request)
        self.assertEqual(post_dict, None)
        self.assertEqual(request_body, "{\"param\":\"val\"}", "UTF-8")


class SetRequestTest(unittest.TestCase):
    class FakeFile(object):
        def __init__(self, filename):
            self.name = filename

    class FakeFiles(object):
        def __init__(self, filenames):
            self.filenames = filenames

        def getlist(self, filename):  # pylint: disable=no-self-use
            return [SetRequestTest.FakeFile(filename)]

        def keys(self):
            return self.filenames

    class FakeRequest(object):
        def __init__(self,
                     content_length=None,
                     get_dict=None,
                     cookies_dict=None,
                     filenames=None):
            self.META = {
                "CONTENT_LENGTH": content_length
            }
            self.GET = get_dict
            self.COOKIES = cookies_dict
            self.FILES = SetRequestTest.FakeFiles(filenames)

    def test_already_processed_request(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.request_processed = True
        appsensor_meta.get_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}
        appsensor_meta.json_dict = {}
        appsensor_meta.post_dict = {}
        appsensor_meta.request_content_bytes_len = -1
        appsensor_meta.files_dict = {}

        request = self.FakeRequest()
        set_request(appsensor_meta, request)

        self.assertTrue(appsensor_meta.request_processed)
        self.assertEqual(appsensor_meta.get_dict, {})
        self.assertEqual(appsensor_meta.cookie_dict, {})
        self.assertEqual(appsensor_meta.headers_dict, {})
        self.assertEqual(appsensor_meta.json_dict, {})
        self.assertEqual(appsensor_meta.post_dict, {})
        self.assertEqual(appsensor_meta.request_content_bytes_len, -1)
        self.assertEqual(appsensor_meta.files_dict, {})

    def test_set_request(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.encoding = "UTF-8"
        appsensor_meta.request_processed = False
        appsensor_meta.get_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}
        appsensor_meta.json_dict = {}
        appsensor_meta.request_content_bytes_len = -1
        appsensor_meta.files_dict = {}

        request = self.FakeRequest(content_length=100,
                                   get_dict={"get-param": "value"},
                                   cookies_dict={"cookie-param": "value"},
                                   filenames=["filename-one", "filename-two"])
        with patch("tcell_agent.instrumentation.djangoinst.meta.parse_body",
                   return_value=[{"post-param": "value"},
                                 '{"json-param": "value"}']) as patched_parse_body:
            set_request(appsensor_meta, request)
            self.assertTrue(patched_parse_body.called)
            self.assertTrue(appsensor_meta.request_processed)
            self.assertEqual(appsensor_meta.get_dict, {"get-param": "value"})
            self.assertEqual(appsensor_meta.cookie_dict, {"cookie-param": "value"})
            self.assertEqual(appsensor_meta.headers_dict, {'content-length': [100]})
            self.assertEqual(appsensor_meta.request_body, '{"json-param": "value"}')
            self.assertEqual(appsensor_meta.post_dict, {"post-param": "value"})
            self.assertEqual(appsensor_meta.request_content_bytes_len, 100)
            self.assertEqual(appsensor_meta.files_dict,
                             MultiValueDict({"filename-one": ["filename-one"], "filename-two": ["filename-two"]}))
