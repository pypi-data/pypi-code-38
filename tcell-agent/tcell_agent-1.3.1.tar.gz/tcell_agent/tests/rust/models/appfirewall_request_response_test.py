import json
import unittest

from django.utils.datastructures import MultiValueDict
from werkzeug.datastructures import ImmutableMultiDict

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.rust.models.appfirewall_request_response import AppfirewallRequestResponse


class BadData(object):
    def __init__(self, my_id):
        self.me = str(my_id)

    def __repr__(self):
        return self.me


class AppfirewallRequestTest(unittest.TestCase):

    def test_create_request(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.path = "/some/path"
        appsensor_meta.location = "http://192.168.1.1/some/path?xss_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.request_content_bytes_len = 1024
        appsensor_meta.response_content_bytes_len = 2048
        appsensor_meta.get_dict = MultiValueDict({"user": ["Steve Jobs"], "xss_param": ["<script>", "not script"]})
        appsensor_meta.path_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = MultiValueDict({"some_value": ["1234"], "xss_param": ["<script>", "not script"]})
        appsensor_meta.files_dict = MultiValueDict({"file_param": ["<script>"]})
        appsensor_meta.cookie_dict = {"xss_param": "<script>"}
        appsensor_meta.headers_dict = MultiValueDict({"xss_param": ["<script>"]})
        appsensor_meta.user_agent_str = "Mozilla"
        appsensor_meta.content_type = "application/x-www-form-urlencoded"
        appsensor_meta.request_body = "post_param=script"

        request_response = AppfirewallRequestResponse(appsensor_meta)
        request_response["query_params"] = sorted(request_response["query_params"], key=lambda k: k['name'])
        request_response["post_params"] = sorted(request_response["post_params"], key=lambda k: k['name'])

        self.assertEqual(
            request_response,
            {
                "method": "GET",
                "status_code": 200,
                "route_id": "12345",
                "path": "/some/path",
                'post_params': [{'name': 'file_param', 'value': '<script>'},
                                {'name': 'some_value', 'value': '1234'},
                                {'name': 'xss_param', 'value': '<script>'},
                                {'name': 'xss_param', 'value': 'not script'}],
                'query_params': [{'name': 'user', 'value': 'Steve Jobs'},
                                 {'name': 'xss_param', 'value': '<script>'},
                                 {'name': 'xss_param', 'value': 'not script'}],
                "headers": [{"name": "xss_param", "value": "<script>"}],
                "cookies": [{"name": "xss_param", "value": "<script>"}],
                "path_params": [{"name": "xss_param", "value": "<script>"}],
                "remote_address": "192.168.1.1",
                "session_id": "session_id",
                "user_id": "user_id",
                "user_agent": "Mozilla",
                "request_bytes_length": 1024,
                "response_bytes_length": 2048,
                "full_uri": "http://192.168.1.1/some/path?xss_param=<script>",
                "database_result_sizes": [],
                "sql_exceptions": [],
                "content_type": "application/x-www-form-urlencoded",
                "request_body": "post_param=script"
            }
        )

    def test_create_request_flask(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.path = "/some/path"
        appsensor_meta.location = "http://192.168.1.1/some/path?xss_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.request_content_bytes_len = 1024
        appsensor_meta.response_content_bytes_len = 2048
        appsensor_meta.get_dict = ImmutableMultiDict({"user": ["Steve Jobs"], "xss_param": ["<script>", "not script"]})
        appsensor_meta.path_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = ImmutableMultiDict({"some_value": ["1234"], "xss_param": ["<script>", "not script"]})
        appsensor_meta.files_dict = ImmutableMultiDict({"file_param": ["<script>"]})
        appsensor_meta.cookie_dict = {"xss_param": "<script>"}
        appsensor_meta.headers_dict = MultiValueDict({"xss_param": ["<script>"]})
        appsensor_meta.user_agent_str = "Mozilla"
        appsensor_meta.content_type = "application/x-www-form-urlencoded"
        appsensor_meta.request_body = "post_param=script"

        request_response = AppfirewallRequestResponse(appsensor_meta)
        request_response["query_params"] = sorted(request_response["query_params"], key=lambda k: k['name'])
        request_response["post_params"] = sorted(request_response["post_params"], key=lambda k: k['name'])

        self.assertEqual(
            request_response,
            {
                "method": "GET",
                "status_code": 200,
                "route_id": "12345",
                "path": "/some/path",
                'post_params': [{'name': 'file_param', 'value': '<script>'},
                                {'name': 'some_value', 'value': '1234'},
                                {'name': 'xss_param', 'value': '<script>'},
                                {'name': 'xss_param', 'value': 'not script'}],
                'query_params': [{'name': 'user', 'value': 'Steve Jobs'},
                                 {'name': 'xss_param', 'value': '<script>'},
                                 {'name': 'xss_param', 'value': 'not script'}],
                "headers": [{"name": "xss_param", "value": "<script>"}],
                "cookies": [{"name": "xss_param", "value": "<script>"}],
                "path_params": [{"name": "xss_param", "value": "<script>"}],
                "remote_address": "192.168.1.1",
                "session_id": "session_id",
                "user_id": "user_id",
                "user_agent": "Mozilla",
                "request_bytes_length": 1024,
                "response_bytes_length": 2048,
                "full_uri": "http://192.168.1.1/some/path?xss_param=<script>",
                "database_result_sizes": [],
                "sql_exceptions": [],
                "content_type": "application/x-www-form-urlencoded",
                "request_body": "post_param=script"
            }
        )

    def test_for_bad_data_in_request(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.method = "GET"
        appsensor_meta.route_id = "12345"
        appsensor_meta.path = "/some/path"
        appsensor_meta.get_dict = MultiValueDict({"bad_data": [BadData(1)]})
        appsensor_meta.post_dict = MultiValueDict({"post_bad_data": [BadData(2)]})
        appsensor_meta.content_type = "application/x-www-form-urlencoded"
        appsensor_meta.request_body = BadData(3)
        appsensor_meta.headers_dict = MultiValueDict({"header_bad_data": [BadData(4)]})
        appsensor_meta.cookie_dict = {"cookie_bad_data": BadData(5)}
        appsensor_meta.path_dict = {"path_bad_data": BadData(6)}
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.location = "http://192.168.1.1/some/path?xss_param=<script>"
        appsensor_meta.session_id = BadData(8)
        appsensor_meta.user_id = BadData(9)
        appsensor_meta.user_agent_str = "Mozilla"
        appsensor_meta.request_content_bytes_len = 1024
        appsensor_meta.response_content_bytes_len = 2048
        appsensor_meta.files_dict = MultiValueDict({"file_bad_data": [BadData(7)]})
        # skipping sql exceptions because they're constructed as strings
        appsensor_meta.csrf_reason = BadData(10)

        request_response = AppfirewallRequestResponse(appsensor_meta)

        jsun = json.dumps(request_response)
        self.assertIsNotNone(jsun)
