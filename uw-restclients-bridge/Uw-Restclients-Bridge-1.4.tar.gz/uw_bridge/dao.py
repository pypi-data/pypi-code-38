"""
Contains Bridge DAO implementations.
"""

from base64 import urlsafe_b64encode
import logging
import os
from os.path import abspath, dirname
from restclients_core.dao import DAO


logger = logging.getLogger(__name__)


class Bridge_DAO(DAO):
    def service_name(self):
        return 'bridge'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _get_basic_auth(self):
        return "{0}:{1}".format(
            self.get_service_setting(
                "BASIC_AUTH_KEY", ""),
            self.get_service_setting(
                "BASIC_AUTH_SECRET", ""))

    def _custom_headers(self, method, url, headers, body):
        credentials = self._get_basic_auth().encode()
        headers["Authorization"] = "Basic {0}".format(
            urlsafe_b64encode(credentials).decode("ascii"))
        return headers

    def _edit_mock_response(self, method, url, headers, body, response):
        if response.status == 404 and method != "GET":
            alternative_url = "{0}.{1}".format(url, method)
            backend = self.get_implementation()
            new_resp = backend.load(method, alternative_url, headers, body)
            response.status = new_resp.status
            response.data = new_resp.data
            logger.debug("{0} ==>STATUS: {1:d}",
                         alternative_url, response.status)

    def is_mock(self):
        return self.get_implementation().is_mock()
