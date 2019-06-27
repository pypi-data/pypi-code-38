
import requests
from kaola.comm.comm import Comm
from kaola.api.order import Order
from kaola.api.delivery import Deliery
from kaola.api.category import Category
from kaola.api.basic import Basic
from kaola.api.product import Product
from kaola.api.vender import Vender
from kaola.api.service import Service

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

    def get_authorization_code(self, redirect_uri):
        """
        获取授权码
        授权码将在回调的url的参数中，请在url进行解析获取
        """
        url = f"https://oauth.kaola.com/oauth/authorize?response_type=code&client_id={self._app_key}&redirect_uri={redirect_uri}&state=1212&type=101"
        requests.post(url)

    def get_access_token(self, redirect_uri, code):
        """
        获取access_token
        """
        url = f"https://oauth.kaola.com/oauth/token?grant_type=authorization_code&client_id={self._app_key}&redirect_uri={redirect_uri}&code={code}&state=1212&client_secret={self._app_secret}"
        return requests.post(url)

    comm = Comm()
    order = Order()
    delivery = Deliery()
    category = Category()
    basic = Basic()
    product = Product()
    vender = Vender()
    service = Service()
