# -*- coding: utf-8 -*-

from Cryptodome.Hash import SHA256

from .baseapi import BaseAPI

"""
@author VoiceAI
@desc 本模块是AuthAPI认证
@date 20180928
"""


class AppAuthAPI(BaseAPI):
    def __init__(self, base_url, app_id, access_token=""):
        """

        :param base_url:        声纹云URL地址 string
        :param app_id:          应用ID string
        :param access_token:    访问Token string option
        """
        super(AppAuthAPI, self).__init__(base_url, app_id)
        self._app_secret = ""
        self._nonce = ""
        self._timestamp = 0
        self._access_token = access_token
        self._expires = 7200

    def get_access_token(self):
        """

        :return: 返回访问Token string
        """
        return self._access_token

    def get_expires(self):
        """

        :return: 返回访问Token过期时间 int
        """
        return self._expires

    def app_auth_get(self, app_secret):
        """
        获取Nonce等方便签名获取Token
        :param app_secret:  应用密钥 string
        :return:
            响应数据 object
        """
        self._app_secret = app_secret
        api_response = self.call_common_api("/api/app/auth/get", {})
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
            self._nonce = data["nonce"]
            self._timestamp = data["timestamp"]

        return flag_bool_response, err, data

    def app_auth_token_get(self):
        """
        获取Token
        :return:
            响应数据 object
        """
        content = [self._app_id, self._app_secret, self._nonce, str(self._timestamp)]
        h = SHA256.new()
        content.sort()
        h.update("".join(content).encode("utf8"))
        signature = h.hexdigest()
        req_json = {
            "nonce": self._nonce,
            "timestamp": self._timestamp,
            "signature": signature
        }
        api_response = self.call_common_api("/api/app/auth/token/get", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
            self._access_token = data["access_token"]
            self._expires = data["expires"]

        return flag_bool_response, err, data

    def app_auth_token_refresh(self):
        """
        刷新Token
        :return:
            响应数据 object
        """
        req_json = {
            "access_token": self._access_token
        }
        api_response = self.call_common_api("/api/app/auth/token/refresh", req_json)
        err = api_response["error"]
        data = None
        flag_bool_response = bool(api_response["flag"])
        if not flag_bool_response:
            pass
        else:
            data = api_response["data"]
            self._expires = data["expires"]

        return flag_bool_response, err, data

    def app_auth_token_remove(self):
        """
        移除Token
        :return:
            响应数据 object
        """
        req_json = {
            "access_token": self._access_token
        }
        api_response = self.call_common_api("/api/app/auth/token/remove", req_json)
        err = api_response["error"]
        flag_bool_response = bool(api_response["flag"])
        return flag_bool_response, err
