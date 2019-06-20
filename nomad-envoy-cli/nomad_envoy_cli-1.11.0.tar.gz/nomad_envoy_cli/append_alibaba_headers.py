import base64
import datetime
import hashlib
import hmac
import json
import logging
import os
import sys
import uuid
from copy import deepcopy

from urllib3.util import parse_url
from urllib3.util.url import Url

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.propagate = False
out_handler = logging.StreamHandler(sys.stdout)
out_handler.setLevel(logging.INFO)
log.addHandler(out_handler)

logger = logging.getLogger(__name__)

__all__ = ['append_alibaba_headers',
           'keep_configuration_in_RESTClientObject',
           'AppendAlibabaHeaders']

"""
Append Alibaba authentication headers based on original full HTTP request.

This Python implementation is modified from
https://github.com/aliyun/api-gateway-nodejs-sdk

---------------------------

Example Swagger Client usage:

class TestAlicloudApigateway(unittest.TestCase):
    store = 'samarkand.youzan.foreveryoung'

    @classmethod
    def setUpClass(cls):
        configuration = nomad_envoy_cli.Configuration()
        configuration.host = os.environ["ALICLOUD_APIGATEWAY_HOST"] + "/envoy"
        configuration.api_key = {
            "x-ca-key": os.environ["ALICLOUD_APIGATEWAY_APP_KEY"],
            "x-ca-stage": os.environ["ALICLOUD_STAGE"],
        }
        configuration.alibaba = {"ALICLOUD_APIGATEWAY_APP_SECRET": os.environ[
            "ALICLOUD_APIGATEWAY_APP_SECRET"]}

        cls.order_api = OrderApi(ApiClient(configuration))
        cls.product_api = ProductApi(ApiClient(configuration))

    def test_order(self):
        result = self.order_api.get_order_by_field(
            self.store, _request_timeout=60 * 1000)

        self.assertEqual(result.code, 200)
        self.assertTrue(len(result.data.orders) > 0,
                        "we at least have one order.")
"""


def append_alibaba_headers(func):
    """
    A Python decorator to modify the request made by Swagger Client.

    The original method is RESTClientObject.request:

        def request(self, method, url, query_params=None, headers=None,
                body=None, post_params=None, _preload_content=True,
                _request_timeout=None):
            pass
    """

    def wrapper(*args, **kw):
        # 1. Re-organize parameters
        self = args[0]
        method = args[1]
        url = args[2]
        query_params = kw.get('query_params', {})
        headers = kw.get('headers', {})
        body = kw.get('body', {}) or {}

        # Since our API is slow, then let our client be ready to wait.
        kw["_request_timeout"] = 60 * 30  # 30 seconds

        # 2. Translating original Node.js code into below Python code.
        aah = AppendAlibabaHeaders(self.configuration, method, url,
                                   query_params, headers, body)
        headers = aah.result()

        # 3 .Write things back to args and kw if we changed anything.
        kw["headers"] = headers

        if os.environ.get("NOMAD_DEBUG", None) == "TRUE":
            log.info("""  --------- debug Alibaba Client request ---------
method: %s
url: %s
query_params: %s
headers: %s
body: %s

            """ % (
                method,
                url,
                json_dumps_unicode(query_params),
                json_dumps_unicode(headers),
                json_dumps_unicode(body)
            ))

        return func(*args, **kw)

    return wrapper


def keep_configuration_in_RESTClientObject(func):
    """
    We need to access "configuration" inside of @append_alibaba_headers.
    """

    def wrapper(*args, **kw):
        self = args[0]
        configuration = args[1]
        self.configuration = configuration
        func(*args, **kw)

    return wrapper


class AppendAlibabaHeaders(object):
    sign_headers = {}
    content_type_form = 'application/x-www-form-urlencoded'

    def __init__(self,
                 configuration,  # SwaggerClient.Configuration
                 method: str,
                 url: str,
                 query_params: dict,
                 headers: dict,
                 body: dict):
        self.configuration = configuration
        self.method = method
        self.url = url
        self.query_params = query_params
        if isinstance(self.query_params, list):
            self.query_params = {i[0]: i[1] for i in self.query_params}
        self.body = body

        self.original_data_dict = {}
        self.original_data_dict.update(self.query_params)
        self.original_data_dict.update(self.body)

        self.x_ca_timestamp = int(datetime.datetime.now().timestamp() * 1000)
        # TODO client would reuse the request, maybe should re-generate nonce.
        self.x_ca_nonce = str(uuid.uuid4())
        self.headers = {k.lower(): headers[k] for k in headers.keys()}
        self.content = None

    def initial_headers(self, headers):
        d = {
            'x-ca-timestamp': self.x_ca_timestamp,
            'x-ca-key': self.configuration.api_key.get("x-ca-key", ""),
            'x-ca-nonce': self.x_ca_nonce,
            'x-ca-stage': self.configuration.api_key.get("x-ca-stage", "test"),
            'accept': 'application/json',
        }
        d.update(headers)
        d.update({"content-type": self.request_content_type})
        d.update(self.sign_headers)
        return d

    def get_sign_header_keys(self, headers: dict, sign_headers: dict) -> list:
        sign_keys = [h for h in headers
                     if h.startswith("x-ca-") or h in sign_headers]
        return list(sorted(sign_keys))

    def get_signed_headers_string(self, sign_headers: list, headers: dict) -> \
            str:
        return "\n".join([h + ":" + str(headers[h]) for h in sign_headers])

    def build_string_to_sign(self,
                             method,
                             headers,
                             signed_headers_str,
                             url: Url,
                             data) -> str:
        lf = "\n"

        content_type = headers.get('content-type', '')

        buffer = [
            method,
            headers.get('accept', ""),
            headers.get('content-md5', ""),
            content_type,
            headers.get('date', None),
        ]

        if signed_headers_str:
            buffer.append(signed_headers_str)

        buffer.append(self.build_url(url, content_type, data))

        return lf.join([v or "" for v in buffer])

    def build_url(self, url: Url, content_type, data=None) -> str:
        new_query = deepcopy(self.query_params or {})
        if content_type.startswith(self.content_type_form):
            new_query.update(data or {})

        query_list = []
        for k in sorted(new_query.keys()):
            if new_query[k] is not None:
                query_list.append(k + "=" + str(new_query[k]))
            else:
                query_list.append(k)
        query_str = "&".join(query_list)
        return url.path + "?" + query_str if query_str else url.path

    def sign(self, string_to_sign) -> str:
        assert hasattr(self.configuration, "platform_parameters"), \
            "Please assgin a dictionary called \"platform_parameters\" to " + \
            "self.configuration before use this Alibaba Swagger Client."

        secret = self.configuration.platform_parameters[
            "ALICLOUD_APIGATEWAY_APP_SECRET"].encode("utf-8")
        m = hmac.new(secret, digestmod=hashlib.sha256)
        m.update(string_to_sign.encode('utf-8'))
        return base64.b64encode(m.digest()).decode('utf-8')

    @property
    def request_content_type(self):
        # note: Samarkand use JSON as the default format.
        return self.headers.get("content-type", "application/json")

    @property
    def is_content_type_form(self):
        return self.request_content_type.startswith(self.content_type_form)

    def result(self) -> dict:
        auth_headers = self.initial_headers(self.headers)

        if (self.method.upper() == "POST") and (not self.is_content_type_form):
            # querystring.stringify_obj(self.original_data_dict)
            # TODO could we avoid another duplicate json.dumps in rest#request
            # this md5 works, verified by changing this string a bit.
            self.content = json.dumps(self.body)
            auth_headers["content-md5"] = md5(self.content)

        sign_header_keys = self.get_sign_header_keys(auth_headers,
                                                     self.sign_headers)
        auth_headers['x-ca-signature-headers'] = ','.join(sign_header_keys)
        signed_headers_str = self.get_signed_headers_string(sign_header_keys,
                                                            auth_headers)

        self.stringToSign = self.build_string_to_sign(self.method,
                                                      auth_headers,
                                                      signed_headers_str,
                                                      parse_url(self.url),
                                                      self.body)

        auth_headers['x-ca-signature'] = self.sign(self.stringToSign)

        return auth_headers


def md5(content: str) -> str:
    m = hashlib.md5()
    m.update(content.encode('utf-8'))
    return base64.b64encode(m.digest()).decode("utf-8")


def json_dumps_unicode(obj):
    """
    Change Python default json.dumps acting like JavaScript, including allow
    Chinese characters and no space between any keys or values.
    """
    return json.dumps(obj,
                      ensure_ascii=False,
                      separators=(',', ':')
                      )
