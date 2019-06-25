import json
import requests
import datetime
from functools import lru_cache

from flask import current_app

from . import WECHAT_API_URL


@lru_cache(None)
def _access_token():
    """
    获取微信access token，本地缓存两个小时
    装饰器vald_token会拦截第二个参数，所以该方法在调用时，只需要接收参数access_token
    :return access_token: 微信调用接口凭证
    """
    access_token = ''
    postUrl = WECHAT_API_URL + 'cgi-bin/token' + \
        '?grant_type=client_credential&appid={}&secret={}' \
        .format(current_app.config.get('WXAPPID'),
                current_app.config.get('WXAPPSECRET'))
    url_resp = requests.get(postUrl)
    if url_resp.status_code == 200:
        url_resp = json.loads(url_resp.text)
        access_token = url_resp["access_token"]
    return access_token, datetime.datetime.now()


@lru_cache(None)
def _jsapi_ticket():
    """
    获取jsapi ticket，本地缓存两个小时
    :return access_token: 微信调用接口凭证
    """
    jsapi_ticket = ''
    access_token = TokenUtil.access_token()
    postUrl = WECHAT_API_URL + \
        "cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % access_token
    url_resp = requests.get(postUrl)
    if url_resp.status_code == 200:
        url_resp = json.loads(url_resp.text)
        jsapi_ticket = url_resp["ticket"]
    return jsapi_ticket, datetime.datetime.now()


class TokenUtil:

    @staticmethod
    def access_token():

        token, create_datetime = _access_token()
        if create_datetime < datetime.datetime.now() - \
           datetime.timedelta(hours=2) or not token:
            _access_token().cache_clear()
            token, create_datetime = _access_token()
        return token

    @staticmethod
    def jsapi_ticket():
        token, create_datetime = _jsapi_ticket()
        if create_datetime < datetime.datetime.now() - \
           datetime.timedelta(hours=2) or not token:
            _jsapi_ticket().cache_clear()
            token, create_datetime = _jsapi_ticket()
        return token
