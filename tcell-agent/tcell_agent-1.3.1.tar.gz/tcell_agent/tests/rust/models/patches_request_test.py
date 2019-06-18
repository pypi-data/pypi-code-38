import unittest

from django.utils.datastructures import MultiValueDict

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.rust.models.patches_request import PatchesRequest


class RequestResponseTest(unittest.TestCase):
    def test_create_patches_request(self):
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

        request_response = PatchesRequest(appsensor_meta)
        request_response["query_params"] = sorted(request_response["query_params"], key=lambda k: k['name'])
        request_response["post_params"] = sorted(request_response["post_params"], key=lambda k: k['name'])

        self.assertEqual(
            request_response,
            {
                "full_uri": "http://192.168.1.1/some/path?xss_param=<script>",
                "method": "GET",
                "path": "/some/path",
                "remote_address": "192.168.1.1",
                'post_params': [{'name': 'file_param', 'value': '<script>'},
                                {'name': 'some_value', 'value': '1234'},
                                {'name': 'xss_param', 'value': '<script>'},
                                {'name': 'xss_param', 'value': 'not script'}],
                'query_params': [{'name': 'user', 'value': 'Steve Jobs'},
                                 {'name': 'xss_param', 'value': '<script>'},
                                 {'name': 'xss_param', 'value': 'not script'}],
                "headers": [{"name": "xss_param", "value": "<script>"}],
                "cookies": [{"name": "xss_param", "value": "<script>"}],
                "request_bytes_length": 1024
            }
        )
