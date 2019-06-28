
import requests
from kaola.comm.comm import Comm
from kaola.api.order import Order
from kaola.api.delivery import Deliery
from kaola.api.category import Category
from kaola.api.basic import Basic
from kaola.api.product import Product
from kaola.api.vender import Vender
from kaola.api.service import Service
from hashlib import md5

TEST_HOST = "http://openapi-test.kaola.com/router"
HOST = "https://openapi.kaola.com/router"


class KaoLa(object):

    def __init__(self, app_key, app_secret, v="1.0", access_token=None, sandbox=False):
        """
        初始化考拉API
        v1版本授权码固定
        v2版本需要用户授权获取
        timezone: 非UTC时区需传入本地服务器所在时区
        """
        self._app_key = app_key
        self._app_secret = app_secret
        self._v = v
        self._host = TEST_HOST if sandbox else HOST
        if v == "1.0":
            self._access_token = access_token
        else:
            # [TODO] 2.0版本获取access_token且有时效限制
            pass

    def set_access_token(self, token):
        """
        设置access_token
        """
        self._access_token = token

    def check_authorization_state(self, redirect_uri, state):
        """
        验证state是否合法
        """
        return md5(redirect_uri.encode("utf-8")).hexdigest().upper()[5:12] == state

    def get_access_token(self, code, redirect_uri):
        """
        获取access_token
        """
        state = md5(redirect_uri.encode("utf-8")).hexdigest().upper()[5:12]
        token_url = f"https://oauth.kaola.com/oauth/token?grant_type=authorization_code&client_id={self._app_key}&redirect_uri={redirect_uri}&code={code}&state={state}&client_secret={self._app_secret}"
        res = requests.post(token_url).json()
        return res.get("access_token", None)

    def generate_authorization_code_url(self, redirect_uri):
        """
        获取访问带有回调参数的authorization_code的URL
        """
        state = md5(redirect_uri.encode("utf-8")).hexdigest().upper()[5:12]
        return f"https://oauth.kaola.com/oauth/authorize?response_type=code&client_id={self._app_key}&redirect_uri={redirect_uri}&state={state}&type=101"

    comm = Comm()
    order = Order()
    delivery = Deliery()
    category = Category()
    basic = Basic()
    product = Product()
    vender = Vender()
    service = Service()
