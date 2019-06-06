# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Pyramid specific WSGI HTTP Request / Response stuff
"""

import os
from itertools import chain
from logging import getLogger

from ..utils import is_json_serializable
from .base import BaseRequest, BaseResponse

LOGGER = getLogger(__name__)


class PyramidRequest(BaseRequest):
    def __init__(self, request):
        super(PyramidRequest, self).__init__()
        self.request = request

        # Cache for params
        self._query_params = None
        self._query_params_values = None
        self._form_params = None
        self._json_body = None

        if self.__class__.DEBUG_MODE is None:
            self.__class__.DEBUG_MODE = self.is_debug()

    @property
    def query_params(self):
        if self._query_params is None:
            # Convert pyramid MultiDict to a normal dict with values as list
            self._query_params = dict(self.request.GET.dict_of_lists())
        return self._query_params

    @property
    def query_params_values(self):
        """ Return only query values as a list
        """
        if self._query_params_values is None:
            self._query_params_values = list(
                chain.from_iterable(self.query_params.values())
            )
        return self._query_params_values

    @property
    def form_params(self):
        # Convert pyramid MultiDict to a normal dict with values as list
        if self._form_params is None:
            form_params = {}
            post_params = self.request.POST
            for param_name in post_params:
                values = post_params.getall(param_name)
                # Ignore any non json serializable value as we don't know
                # how to process them (like cgi.FieldStorage)
                form_params[param_name] = list(
                    filter(is_json_serializable, values)
                )
            self._form_params = form_params
        return self._form_params

    @property
    def cookies_params(self):
        return dict(self.request.cookies)

    @property
    def remote_addr(self):
        """Remote IP address."""
        return self.request.remote_addr

    @property
    def hostname(self):
        return self.request.host

    @property
    def method(self):
        return self.request.method

    @property
    def referer(self):
        return self.request.environ.get("HTTP_REFERER")

    @property
    def client_user_agent(self):
        return self.request.user_agent

    @property
    def route(self):
        """Request route."""
        route = getattr(self.request, "matched_route", None)
        pattern = getattr(route, "pattern", None)
        return pattern

    @property
    def path(self):
        return self.request.path

    @property
    def scheme(self):
        return self.request.scheme

    @property
    def server_port(self):
        return self.request.environ.get("SERVER_PORT")

    @property
    def remote_port(self):
        return self.request.environ.get("REMOTE_PORT")

    @property
    def view_params(self):
        return self.request.matchdict

    @property
    def json_params(self):
        if self._json_body is None:
            try:
                self._json_body = self.request.json_body
            except Exception:
                self._json_body = {}
        return self._json_body

    def get_header(self, name):
        """ Get a specific header
        """
        return self.request.environ.get(name)

    @property
    def headers(self):
        return self.request.environ

    @staticmethod
    def is_debug():
        try:
            return bool(os.environ.get("PYTHON_RELOADER_SHOULD_RUN", False))
        except Exception:
            LOGGER.warning("Exception when checking debug mode", exc_info=1)
            return False


class PyramidResponse(BaseResponse):

    def __init__(self, response):
        self.response = response

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def content_type(self):
        return self.response.headers.get("Content-Type")

    @property
    def content_length(self):
        try:
            return int(self.response.content_length)
        except (ValueError, TypeError):
            return None
