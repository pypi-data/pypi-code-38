# -*- coding: utf-8 -*-
from sdk.sdk_logging import SDKLog
class Config:
    __sandbox = False
    # your app_key
    __app_key = None
    # your secret
    __secret = None
    # your callback url
    __callback_url = None

    __base_url = None

    __log = None

    __host_url = "https://open-api.shop.ele.me"

    __sandbox_host_url = "https://open-api-sandbox.shop.ele.me"
    
    def __init__(self, sandbox, app_key, secret, callback_url=None):
        self.__sandbox = sandbox
        self.__app_key = app_key
        self.__secret = secret
        self.__callback_url = callback_url
        if(self.__log==None):
            self.__log = SDKLog()

    def get_env(self):
        return self.__sandbox

    def get_app_key(self):
        return self.__app_key

    def set_base_url(self, base_url):
        self.__base_url = base_url

    def get_secret(self):
        return self.__secret

    def get_callback_url(self):
        return self.__callback_url

    def set_log(self, log):
        if not(hasattr(log, 'info')):
            raise Exception (' log not has info method!')
        if not (hasattr(log, 'error')):
            raise Exception ('log not has error method!')
        self.__log = log

    def get_log(self):
        return self.__log

    def get_server_url(self):
        if not self.__base_url:
            return self.__sandbox and self.__sandbox_host_url or self.__host_url
        else:
            return self.__base_url

    def get_access_token_url(self):
        return self.get_server_url() + "/token"

    def get_api_server_url(self):
        return self.get_server_url() + "/api/v1/"

    def get_authorize_url(self):
        return self.get_server_url() + "/authorize"

    def get_openId_url(self):
        return self.get_server_url() + "/identity"
