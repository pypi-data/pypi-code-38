import urllib.request
import json
import gzip
import ssl
import http.client
import base64
import string
import datetime
import time

from datetime import timezone

from urllib.parse import urlparse
from urllib.parse import quote
from http.client import HTTPSConnection
from http.client import HTTPConnection
from http.client import HTTPException
from http.client import BadStatusLine


def get_context(untrusted=True, cert_file=None, cert_pass=None):
    """Decodes resp. If the decoded resp is JSON, then a JSON object is returned.

    :param bytes resp: Encoded response returned by request.
    :returns: decoded response or parse JSON object if response is JSON.
    """
    ctx = ssl.create_default_context()

    if untrusted:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    if cert_file is not None:
        ctx.load_cert_chain(cert_file, password=cert_pass)

    return ctx


def encode_auth_header(username, password):
    """
    Encodes username and password for HTTP asic authentication
    """
    encoded = base64.b64encode(bytes(username, 'UTF-8') + b':' + bytes(password, 'UTF-8'))
    header = {'Authorization': b'Basic ' + encoded}
    return header


def _decode_resp(response):
    """Unpacks response

    :param bytes resp: Encoded response returned by request.
    :returns: decoded response or parse JSON object if response is JSON.
    """
    response_headers = response.info()
    encoding = response_headers['Content-Encoding']
    r = response.read()
    if encoding is not None and str(encoding) == "gzip":
        try:
            r = gzip.decompress(r)
        except OSError:
            pass
    return _parse_resp(r)


def _parse_resp(resp):
    """Decodes resp. If the decoded resp is JSON, then a JSON object is returned.

    :param bytes resp: Encoded response returned by request.
    :returns: decoded response or parse JSON object if response is JSON.
    """
    parsed = resp.decode('utf-8')
    try:
        return json.loads(parsed)
    except:
        return parsed


class RequestHandler:

    def __init__(self, ssl_context, header, keep_alive=True, keep_alive_timeout=10):
        """
        Initialize request handler
        """
        self.ssl_context = ssl_context
        self.header = header
        self.keep_alive = keep_alive
        self.keep_alive_timeout = keep_alive_timeout
        self.connection = None
        self.conn_expired = datetime.datetime.now(timezone.utc)
        self.finished_req = True

    def init_connection(self, uri_netloc, timeout):
        """
        Initialize connection if necessary
        :param uri_netloc str: net location
        :returns: True if connection is being reused, False otherwise
        """
        now = datetime.datetime.now(timezone.utc)

        if not self.connection or now > self.conn_expired or not self.keep_alive or not self.finished_req:
            self.close_connection()
            if self.ssl_context:
                self.connection = HTTPSConnection(uri_netloc, timeout=timeout, context=self.ssl_context)
            else:
                self.connection = HTTPConnection(uri_netloc, timeout=timeout)
            return False
        else:
            return True

    def close_connection(self):

        if self.connection:
            self.connection.close()
            self.connection = None

    def connection_needs_closing(self, response):
        """
        Checks header to see if connection needs to be closed
        :param bytes resp: Encoded response returned by request.

        """
        response_headers = response.info()
        con = response_headers['Connection']

        if not con:
            con = response_headers['connection']

        if con and str(con).startswith("close"):
            return True

        return False

    def get(self, url, timeout):
        """Makes a GET request on url.
        The function waits for response till timeout is reached.

        :param str url: Absolute URL to executed the GET request
        :param int timeout: Time till which to wait for response
        :param bool untrusted: request lets true untrusted ssl certificate
        :returns: decoded response. If response is JSON, then JSON object is returned.

        """
        return self._handle_request("GET", url, timeout=timeout)

    def post(self, url, data, timeout):
        """Makes a POST request on url.
        data is sent with the request. data is expected to be a string of JSON object.
        The function waits for response till timeout is reached.

        :param str url: Absolute URL to executed the GET request
        :param str data: stringified JSON data
        :param int timeout: Time till which to wait for response
        :param bool untrusted: request lets true untrusted ssl certificate
        :returns: decoded response. If response is JSON, then JSON object is returned.
        """
        return self._handle_request("POST", url, data=data, timeout=timeout)

    def delete(self, url, timeout):
        """Makes a DELETE request on url.
        The function waits for response till timeout is reached.

        :param str url: Absolute URL to executed the GET request
        :param int timeout: Time till which to wait for response
        :param bool untrusted: request lets true untrusted ssl certificate
        :returns: decoded response. If response is JSON, then JSON object is returned.
        """
        return self._handle_request("DELETE", url, timeout=timeout)

    def _send_request(self, conn, method, path, headers, data=None):

        if method == "POST":
            conn.request(method, path, data, headers=headers)
        else:
            conn.request(method, path, headers=headers)

        return conn.getresponse()

    def _handle_request(self, method, url, data=None, timeout=10):
        """
        Handle request with low level library to retain version compatibility
        """
        uri_p = urlparse(url)
        path = uri_p.path
        path = quote(path)

        reuse = self.init_connection(uri_p.netloc, timeout)
        self.finished_req = False
        headers = {'Accept-Encoding': 'gzip'}

        if method == "POST":
            headers['content-type'] = 'application/json'

        if self.header:
            for key, value in self.header.items():
                headers[key] = value

        if len(uri_p.query) > 0:
            path += '?' + uri_p.query

        try:
            res = self._send_request(self.connection, method, path, headers, data=data)
        except Exception as e:
            if reuse:
                self.close_connection()
                self.init_connection(uri_p.netloc, timeout)
            time.sleep(5)
            res = self._send_request(self.connection, method, path, headers, data=data)

        self.conn_expired = datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=self.keep_alive_timeout)

        if self.connection_needs_closing(res):
            self.close_connection()

        if res.status >= 400:
            msg = _decode_resp(res)
            try:
                msg = str(msg['message'])
            except:
                msg = str(msg)
            raise HTTPException(str(res.status) + " " + str(res.reason) + ": " + msg)

        fin = _decode_resp(res)
        self.finished_req = True
        return fin
