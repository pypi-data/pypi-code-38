# coding=utf-8
# Copyright (c) 2015 EMC Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import unicode_literals

import inspect
import sys

import six


class ClientException(Exception):
    """The base exception class for all exceptions this library raises."""


class HttpError(ClientException):
    """The base exception class for all HTTP exceptions."""
    http_status = 0
    message = "HTTP Error"

    def __init__(self, message=None, details=None,
                 response=None, request_id=None,
                 url=None, method=None, http_status=None):
        self.http_status = http_status or self.http_status
        self.message = message or self.message
        self.details = details
        self.request_id = request_id
        self.response = response
        self.url = url
        self.method = method
        formatted_string = "%s (HTTP %s)" % (self.message, self.http_status)
        if request_id:
            formatted_string += " (Request-ID: %s)" % request_id
        super(HttpError, self).__init__(formatted_string)


class HttpServerError(HttpError):
    """Server-side HTTP error.

    Exception for cases in which the server is aware that it has
    erred or is incapable of performing the request.
    """
    message = "HTTP Server Error"


class HTTPClientError(HttpError):
    """Client-side HTTP error.

    Exception for cases in which the client seems to have erred.
    """
    message = "HTTP Client Error"


class BadRequest(HTTPClientError):
    """HTTP 400 - Bad Request.

    The request cannot be fulfilled due to bad syntax.
    """
    http_status = 400
    message = "Bad Request"


# _code_map contains all the classes that have http_status attribute.
_code_map = dict(
    (getattr(obj, 'http_status', None), obj)
    for name, obj in six.iteritems(vars(sys.modules[__name__]))
    if inspect.isclass(obj) and getattr(obj, 'http_status', False)
)


def from_response(response, method, url):
    """Returns an instance of :class:`HttpError` or subclass based on response.

    :param response: instance of `requests.Response` class
    :param method: HTTP method used for request
    :param url: URL used for request
    """

    req_id = response.headers.get("x-openstack-request-id")
    # NOTE(hdd) true for older versions of nova and cinder
    if not req_id:
        req_id = response.headers.get("x-compute-request-id")
    kwargs = {
        "http_status": response.status_code,
        "response": response,
        "method": method,
        "url": url,
        "request_id": req_id,
    }
    if "retry-after" in response.headers:
        kwargs["retry_after"] = response.headers["retry-after"]

    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("application/json"):
        try:
            body = response.json()
        except ValueError:
            pass
        else:
            if isinstance(body, dict):
                error = body.get(list(body)[0])
                if isinstance(error, dict):
                    kwargs["message"] = (error.get("message") or
                                         error.get("faultstring"))
                    kwargs["details"] = (error.get("details") or
                                         six.text_type(body))
    elif content_type.startswith("text/"):
        kwargs["details"] = response.text

    try:
        cls = _code_map[response.status_code]
    except KeyError:
        if 500 <= response.status_code < 600:
            cls = HttpServerError
        elif 400 <= response.status_code < 500:
            cls = HTTPClientError
        else:
            cls = HttpError
    return cls(**kwargs)


class SSHExecutionError(ClientException):
    def __init__(self, stdout=None, stderr=None, exit_code=None, cmd=None,
                 description=None):
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout
        self.cmd = cmd
        self.description = description

        if description is None:
            description = "Unexpected error while running command."
        if exit_code is None:
            exit_code = '-'
        message = ('%(description)s\n'
                   'Command: %(cmd)s\n'
                   'Exit code: %(exit_code)s\n'
                   'Stdout: %(stdout)r\n'
                   'Stderr: %(stderr)r') % {'description': description,
                                            'cmd': cmd,
                                            'exit_code': exit_code,
                                            'stdout': stdout,
                                            'stderr': stderr}
        super(SSHExecutionError, self).__init__(message)


class SFtpExecutionError(ClientException):
    message = "[EMC] Failed to execute sftp operation. %(err)s."
