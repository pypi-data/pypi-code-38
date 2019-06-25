import json
import requests
from urllib.parse import urlencode

from flask import current_app

from . import WECHAT_API_URL


class Authorized(object):
    """
    用户同意授权
    """

    def __init__(self):
        self.app_id = current_app.config.get('WXAPPID')
        self.app_secret = current_app.config.get('WXAPPSECRET')

    def get_code(self, redirect_url, state):
        """
        获取code, 并跳转到指定界面
        """
        params = urlencode({"redirect_uri": redirect_url})
        base_url = "https://open.weixin.qq.com/"
        request_url = base_url + \
            "connect/oauth2/authorize?appid={}".format(self.app_id) + \
            "&{}".format(params) + \
            "&response_type=code&scope=snsapi_userinfo&" + \
            "state={}".format(state) + "#wechat_redirect"
        return request_url

    def get_access_token(self, code):
        """
        通过code换取网页授权access_token
        """
        request_url = WECHAT_API_URL + \
            "sns/oauth2/access_token?appid=" + self.app_id + \
            "&secret=" + self.app_secret + \
            "&code=" + code + \
            "&grant_type=authorization_code"
        response = requests.get(request_url)
        if response.status_code == 200:
            the_page = response.text
            jsonreturn = json.loads(the_page)
            if 'errcode' not in jsonreturn:
                return jsonreturn["access_token"], jsonreturn["openid"]
        return None, None

    def get_user_info(self, access_token, openId):
        request_url = WECHAT_API_URL + \
            "cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN"\
            .format(access_token, openId)
        response = requests.get(request_url)
        if response.status_code == 200:
            the_page = response.text
            jsonreturn = json.loads(the_page)
            if 'errcode' not in jsonreturn:
                return jsonreturn
        return {}
