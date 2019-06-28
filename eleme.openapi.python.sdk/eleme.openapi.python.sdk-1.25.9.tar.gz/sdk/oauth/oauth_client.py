# -*- coding: utf-8 -*-
#from sdk.sdk_logging import ISDKLog

import base64
try:
    from urllib2 import urlopen, Request, quote
    from urlparse import urlparse
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, Request, quote
    from urllib.parse import urlparse, urlencode

from sdk.exception.unauthorized_exception import UnauthorizedException
from sdk.exception.identity_exception import IdentityException

import sys
if sys.version < '3':
    reload(sys)
    sys.setdefaultencoding('utf8')


class OAuthClient:
    def __init__(self, config):
        self.client_id = config.get_app_key()
        self.secret = config.get_secret()
        self.callback_url = config.get_callback_url()
        self.request_url = config.get_access_token_url()
        self.authorize_url = config.get_authorize_url()
        self.openId_request_url = config.get_openId_url()   # openId request
        self.log = config.get_log()

    # 根据key和secret获取token（客户端授权模式）
    def get_token_in_client_credentials(self):
        data = {"grant_type": "client_credentials"}
        return self.do_request(data, self.request_url, "oauth")

    # 构造授权URL（授权码模式）
    def get_auth_url(self, state, scope):
        url = self.authorize_url
        client_id = self.client_id
        response_type = "code"
        callback_url = quote(self.callback_url)
        return "%s?response_type=%s&client_id=%s&state=%s&redirect_uri=%s&scope=%s" % (
            url, response_type, client_id, state, callback_url, scope)

    # 根据auth_code获取token（授权码模式）
    def get_token_by_auth_code(self, code):
        callback_url = self.callback_url
        data = {"grant_type": "authorization_code",
                "code": code,
                "redirect_uri": callback_url,
                "client_id": self.client_id}

        return self.do_request(data, self.request_url, "oauth")

    # 根据refresh_token刷新获取token（授权码模式）
    def get_token_by_refresh_token(self, refresh_token, scope):
        data = {"grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": scope}

        return self.do_request(data, self.request_url, "oauth")

    
    # 根据code 获取openId
    def get_openId_by_code(self, code):
        callback_url = self.callback_url
        data = {"grant_type": "authorization_code",
                "code": code,
                "redirect_uri": callback_url,
                "client_id": self.client_id}
        
        return self.do_request(data, self.openId_request_url, "openId")

    def do_request(self, body, request, sign):
        data = urlencode(body).encode("ascii")
        header = self.get_headers()
        self.log.info(sign + u"oauth client request body: {},headers:{}".format(data, header))
        req = Request(request, data, header)
        result = None
        try:
            response = urlopen(req)
            result = response.read()
        except Exception as e:
            self.log.error(sign + " client request error :" + e.read().decode())
            if sign is "oauth":
                raise UnauthorizedException(e.read().decode())
            else:
                raise IdentityException(e.read().decode())
        self.log.info(sign + " client response :" + result.decode())
        return result.decode()

    def get_headers(self):
        slice = u"{}:{}".format(self.client_id, self.secret)
        value = base64.b64encode(self.get_bytes(slice))
        headers = {
            "Authorization": "Basic " + value.decode(),
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Content-Encoding": "gzip, deflate",
            "User-Agent": "eleme-openapi-python-sdk"
        }
        return headers

    def get_bytes(self, value):
        import sys
        if sys.version > '3':
            return bytes(value, 'utf-8')
        else:
            return bytes(value)





