#!/usr/bin/python3
# @Time    : 2019-06-27
# @Author  : Kevin Kong (kfx2007@163.com)

from jd.comm import Comm
import requests

HOST = "https://api.jd.com/routerjson"
TEST_HOST = "https://api-test.jd.com/routerjson"
AUTH_URL = "https://open-oauth.jd.com/oauth2/to_login"


class DogDong(object):
    """
    京东API
    """

    def __init__(self, appkey, appsecret, access_token, sandbox=False):
        """
        初始化京东API
        """
        self._appkey = appkey
        self._appsecret = appsecret
        self._access_token = access_token
        self._host = TEST_HOST if sandbox else HOST

    comm = Comm()
