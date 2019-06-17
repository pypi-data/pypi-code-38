# 
# Copyright 2014, 2019 by Delphix
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
This module contains the HttpClient which wraps the httplib module.
"""

import logging
try:
    import http.client as httplib
except ImportError:
    import httplib
import socket
import time

DEFAULT_PORT = 80
OK = httplib.OK  # 200
CREATED = httplib.CREATED  # 201
ACCEPTED = httplib.ACCEPTED  # 202
BAD_REQUEST = httplib.BAD_REQUEST  # 400
NOT_FOUND = httplib.NOT_FOUND  # 404
REFRESH_HTTP_CONNECTION_TIMEOUT = 0.5
HTTP_SOCKET_TIMEOUT = 3


class HttpClient(object):
    """
    A wrapper around the standard HTTP module "httplib".
    """
    def __init__(self, address, http_connection=httplib.HTTPConnection):
        """
        Creates a new http client

        :param str address: Hostname or IP address to the server. This can also
          include a port number, e.g. "mydomain.com:8080". Port 80 is used
          as default.
        """
        self._address = address
        self._http_connection = http_connection
        self._time_since_last_reconnection = None
        self._conn = None

    def _repack_response(self, response):
        """
        Repacks the java-ish response from the apache http client as a
        more conventient python data structure

        :param response: The :class:`org.apache.http.HttpResponse`
                         to repack
        :rtype: A tuple (status_code, headers, data), where:

                :status_code: The HTTP status code (200 for OK, etc)
                :headers: A dictionary mapping header names to header values
                :data: The body of the response.
        """
        return (response.status,
                dict(response.getheaders()),
                response.read())

    def _has_timed_out(self):
        if self._time_since_last_reconnection is None:
            return True
        delta = (time.time() - self._time_since_last_reconnection) / 60
        return delta >= REFRESH_HTTP_CONNECTION_TIMEOUT

    def _request(self, method, path, data, headers):
        if not headers:
            headers = {}
        log = logging.getLogger("delphixpy.v1_8_0.http_client")
        if not path.startswith('/'):
            path = '/' + path
        try:
            if self._has_timed_out():
                self._conn = self._http_connection(self._address,
                                              timeout=HTTP_SOCKET_TIMEOUT * 60)
            if isinstance(data, str):
                data = data.encode("utf-8")

            self._conn.request(method, path, data, headers)
        except httplib.ImproperConnectionState:
            try:
                log.warning("Connection was in a improper state, trying to "
                            "reconnect")
                self._conn = self._http_connection(
                    self._address,
                    timeout=HTTP_SOCKET_TIMEOUT * 60)
                self._conn.request(method, path, data, headers)
            except httplib.HTTPException as e:
                msg = ("Request failed with %s on second attempt: %s" %
                       (type(e).__name__, e))
                log.error(msg)
                raise IOError(msg)
        except httplib.HTTPException as e:
            msg = "%s: %s" % (type(e).__name__, e)
            log.error(msg)
            raise IOError(msg)
        try:
            response = self._conn.getresponse()
        except httplib.HTTPException as e:
            msg = "%s when reading response: %s" % (type(e).__name__, e)
            log.error(msg)
            raise IOError(msg)
        except socket.timeout:
            msg = "HTTP socket timed out during %s to '%s'" % (method, path)
            log.error(msg)
            raise IOError(msg)
        # Only update connection timestamp if the request was completely
        # successful
        self._time_since_last_reconnection = time.time()
        return response

    def get(self, path, headers=None):
        """
        Performs a HTTP GET request to path.

        :param path: The path part of the URL as a string
        :param headers: (optional) A dictionary of headers
        :rtype: A tuple (status_code, headers, data), where:

                :status_code: The HTTP status code (200 for OK, etc)
                :headers: A dictionary mapping header names to header values
                :data: The body of the response.
        :raises: `IOError` if the request failed.
        """
        log = logging.getLogger("delphixpy.v1_8_0.http_client")
        log.debug("%s: GET(%s, %s)", self._address, path, headers)
        response = self._request("GET", path, None, headers)
        return self._repack_response(response)

    def post(self, path, data, headers=None):
        """
        Performs a HTTP POST to path.

        :param path: The path part of the URL as a string
        :param data: The data (http body) to be sent with the request
        :param headers: (optional) A dictionary of headers (strings)
        :rtype: A tuple (status_code, headers, data), where:

                :status_code: The HTTP status code (200 for OK, etc)
                :headers: A dictionary mapping header names to header values
                :data: The body of the response.
        :raises: `IOError` if the request failed.
        """
        log = logging.getLogger("delphixpy.v1_8_0.http_client")
        log.debug("%s: POST(%s, %s, %s)", self._address, path, data, headers)
        response = self._request("POST", path, data, headers)
        return self._repack_response(response)

class HttpsClient(HttpClient):
    """
    A wrapper around the standard HTTPS module "httplib".
    """
    def __init__(self, address, https_connection=httplib.HTTPSConnection):
        """
        Creates a new https client

        :param str address: Hostname or IP address to the server. This can also
          include a port number, e.g. "mydomain.com:8080". Port 80 is used
          as default.
        """
        if not issubclass(https_connection, httplib.HTTPSConnection):
            raise Exception(
                "{cls} requires https_connection"
                " to be a subclass of {parent_cls}".format(
                    cls=self.__class__.__name__,
                    parent_cls="httplib.HTTPSConnection",
            ))
        super(HttpsClient, self).__init__(address, https_connection)