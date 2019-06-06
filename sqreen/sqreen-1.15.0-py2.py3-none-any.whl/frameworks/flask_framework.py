# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Flask specific WSGI HTTP Request / Response stuff
"""

from itertools import chain
from logging import getLogger
from traceback import format_stack

from .base import BaseRequest, BaseResponse

try:
    # Python 2
    import urlparse
except ImportError:
    import urllib.parse as urlparse


LOGGER = getLogger(__name__)


class FlaskRequest(BaseRequest):
    def __init__(self, request):
        super(FlaskRequest, self).__init__()
        self.request = request

        # Convert flask QueryDict to a normal dict with values as list
        self.converted_get = dict(self.request.args.lists())

        # Cache for params
        self._query_params_values = None
        self._form_params = None
        self._cookies_params = None

        if self.__class__.DEBUG_MODE is None:
            self.__class__.DEBUG_MODE = self.is_debug()

    @property
    def query_params(self):
        return self.converted_get

    @property
    def query_params_values(self):
        """ Return only query values as a list
        """
        if self._query_params_values is None:
            self._query_params_values = list(
                chain.from_iterable(self.converted_get.values())
            )
        return self._query_params_values

    @property
    def form_params(self):
        if self._form_params is None:
            self._form_params = dict(self.request.form)
        return self._form_params

    @property
    def cookies_params(self):
        if self._cookies_params is None:
            self._cookies_params = dict(self.request.cookies)
        return self._cookies_params

    @property
    def json_params(self):
        return self.request.get_json(silent=True)

    @property
    def remote_addr(self):
        """Remote IP address."""
        return self.request.environ.get("REMOTE_ADDR")

    @property
    def hostname(self):
        parsed = urlparse.urlparse(self.request.url_root)
        return parsed.netloc

    @property
    def method(self):
        return self.request.method

    @property
    def referer(self):
        return self.request.referrer

    @property
    def client_user_agent(self):
        return self.request.user_agent.string

    @property
    def route(self):
        """Request route."""
        url_rule = getattr(self.request, "url_rule", None)
        # If a custom rule_class is used in the app, the rule attribute might
        # be missing.
        return getattr(url_rule, "rule", None)

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
        return str(self.request.environ.get("REMOTE_PORT"))

    def get_header(self, name):
        """ Get a specific header
        """
        return self.request.environ.get(name)

    @property
    def headers(self):
        return self.request.environ

    @property
    def caller(self):
        return format_stack()

    @property
    def view_params(self):
        return self.request.view_args

    @staticmethod
    def is_debug():
        try:
            from flask import current_app

            return current_app.config.get("DEBUG", False)
        except Exception:
            LOGGER.warning("Exception when checking debug mode", exc_info=1)
            return False


class FlaskResponse(BaseResponse):

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
            return int(self.response.headers.get("Content-Length"))
        except (ValueError, TypeError):
            return None
