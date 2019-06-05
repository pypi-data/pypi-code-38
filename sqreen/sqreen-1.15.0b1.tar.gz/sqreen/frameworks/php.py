# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Generic WSGI HTTP Request / Response stuff
"""
from collections import defaultdict
from itertools import chain
from logging import getLogger

from ..exceptions import MissingDataException
from .base import BaseRequest
from .ip_utils import get_real_user_ip

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


LOGGER = getLogger(__name__)


class PHPRequest(BaseRequest):
    """ Helper around PHP request
    """

    def __init__(self, environ):
        super(PHPRequest, self).__init__()
        self.environ = environ.get("request")

        self.missing_data = {}

    @property
    def body(self):
        """Return the body of the request if present"""
        return self.environ.get("BODY")

    @property
    def query_params(self):
        """ Return parsed query string from request
        """
        return self.environ.get("PARSED_REQ_PARAMS", {}).get('"GET"')

    @property
    def form_params(self):
        return self.environ.get("PARSED_REQ_PARAMS", {}).get('"POST"')

    @property
    def cookies_params(self):
        return self.environ.get("PARSED_REQ_PARAMS", {}).get('"COOKIE"')

    @property
    def query_params_values(self):
        """ Return only query values as a list
        """
        return list(chain.from_iterable(self.query_params.values()))

    @property
    def remote_addr(self):
        """Remote IP address."""
        return self.environ.get("REMOTE_ADDR")

    @property
    def client_ip(self):
        return get_real_user_ip(
            self.environ.get("REMOTE_ADDR"), *self.iter_client_ips()
        )

    @property
    def hostname(self):
        return self.get_header("HTTP_HOST", self.environ.get("SERVER_NAME"))

    @property
    def method(self):
        return self.environ.get("REQUEST_METHOD")

    @property
    def client_user_agent(self):
        return self.get_header("HTTP_USER_AGENT")

    @property
    def referer(self):
        return self.get_header("HTTP_REFERER", None)

    @property
    def scheme(self):
        return self.environ.get("URL_SCHEME")

    @property
    def server_port(self):
        return self.environ.get("SERVER_PORT")

    @property
    def remote_port(self):
        return self.environ.get("REMOTE_PORT")

    @property
    def path(self):
        return urlparse.urlparse(self.environ.get("REQUEST_URI", "")).path

    @property
    def headers(self):
        return self.environ.get("HEADERS", {})

    @property
    def request_headers(self):
        return defaultdict(str, **self.headers)

    def get_header(self, name, default=""):
        """ Get a specific header name
        """
        return self.headers.get(name, default)

    @property
    def view_params(self):
        return {}

    @property
    def json_params(self):
        return {}

    @property
    def caller(self):

        return [
            "#{count} {file_}({line}) {class_}{type_}{function}".format(
                count=i,
                file_=line.get("file", ""),
                line=line.get("line", "0"),
                class_=line.get("class", ""),
                type_=line.get("type", ""),
                function=line.get("function", ""),
            )
            for i, line in enumerate(self.raw_caller)
        ]

    @property
    def raw_caller(self):
        return self._get_missing_data("#.caller")

    def _get_missing_data(self, data):
        if data in self.missing_data:
            return self.missing_data[data]

        raise MissingDataException(data)
