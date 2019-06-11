from core.common import *


class Site(object):
    """
    爬虫基本配置
    """
    def __init__(self):
        self.domain = DOMAIN
        self.defaultCookies = DEFAULT_COOKIES  # 默认cookie
        self.cookies = {}  # dict类型的cookie
        self.sleepTime = SLEEP_TIME  # 抓取间隔时间
        self.retryNum = RETRY_NUM  # 重试次数
        self.retrySleepTime = RETRY_SLEEP_TIME  # 重试间隔时间
        self.timeOut = TIMEOUT  # 默认超时时间
        self.headers = HEADERS
        self._method = "GET"
        self._proxy = None  # 代理，dict类型
        self.json = None  # post json
        self.data = None  # post str data

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        if isinstance(proxy, dict):
            self._proxy = proxy
        else:
            raise TypeError('The parameter must be "dict" ')
