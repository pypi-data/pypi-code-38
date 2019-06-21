import re
import requests
import core.user_agent as user_agent
from bs4 import BeautifulSoup

_request_types = {
    1: {"Info": "Get without proxies", 'Method': "get"},
    2: {"Info": "Get with proxies", 'Method': "get"},
    3: {"Info": "Post without proxies", 'Method': "post"},
    4: {"Info": "Post with proxies", 'Method': "post"}
}

_proxy_types = {1: {"name": "Tor", 'http': 'socks5://', 'https': 'socks5://'},
                2: {"name": "PublicProxy", 'http': '', 'https': ''},
                3: {"name": "PublicProxy", 'http': '', 'https': ''}}


class Response:
    def __init__(self, data):
        self.data = data
        self.content = None  # html converted to bs object
        self.content_raw = None  # raw not converted to bs object
        self.text = None # html text
        self.url = None
        self.headers = None
        self.content_load()

    def content_load(self):
        if type(self.data) == requests.models.Response:
            self.url = self.data.url
            self.content_raw = self.data.content
            self.content = BeautifulSoup(self.data.content, 'lxml')
            self.text = self.data.text
            self.headers = self.data.headers
            return
        self.content = self.data


class Request:

    def __init__(self):
        self.ses = requests.session()
        self.url = None
        self.proxy = None
        self.timeout = 60
        self.payload = {}
        self.preserve = True  # preserve session
        self.proxy_type = 1
        self.ip = "127.0.0.1"
        self.port = "9150"
        self.request_type = 1
        self.response = None
        self.args = None
        self.verify = True
        self.headers = None

    def session(self):
        if self.ses is None or self.preserve is False:
            ses = requests.session()
            if self.headers is not None:
                self.headers = self.headers
            else:
                ses.headers['User-Agent'] = user_agent.get()
            ses.verify =self.verify
            self.ses = ses

        ua = self.ses.headers.get('User-Agent')
        if ua is not None:
            if re.search('python', ua) is not None:
                self.ses.headers['User-Agent'] = user_agent.get()

    def go(self, url, download=False, args=None):
        self.args = args
        self.url = url
        self.session()
        self.prepare_proxy()
        method = _request_types.get(self.request_type).get('Method')
        if args is not None:
            response = getattr(self, method)(args=args)
        else:
            response = getattr(self, method)()

        if download is True:
            if type(response) is dict:
                return response
            return response.content
        else:
            self.response = Response(self.test_response(response))
        return self.response

    def prepare_proxy(self):

        self.proxy = {
            'http': '{0}{1}:{2}'.format(_proxy_types.get(self.proxy_type).get('http'),self.ip, self.port),
            'https': '{0}{1}:{2}'.format(_proxy_types.get(self.proxy_type).get('https'),self.ip, self.port)}

    @staticmethod
    def test_response(response):
        if type(response)is dict:
            return response
        if type(response) is int:
            return {"RequestError": "BadIp"}
        if 399 < int(response.status_code) < 500:
            return {"RequestError": "Blocked"}
        if int(response.status_code) > 499:
            return {"RequestError": "Page server is down"}
        return response

    def get(self, args=None):
        try:
            if self.request_type is 1:
                return self.ses.get(self.url,timeout=self.timeout)
            if self.request_type is 2:
                return self.ses.get(self.url, proxies=self.proxy, timeout=self.timeout)
        except Exception as e:
            return {'RequestError': "{}".format(str(e))}

    def post(self, args=None):
        try:
            if args is None:
                args = {}
            args.update({"timeout": self.timeout})
            if self.args is not None:
                args.update(self.args)
            if self.request_type is 3:
                if args.get('data') is None:
                    return self.ses.post(self.url, self.payload, **args)
                if args.get('data') is not None:
                    return self.ses.post(self.url, **args)
            if self.request_type is 4:
                args.update({"proxies": self.proxy})
                if args.get('data') is None:
                    return self.ses.post(self.url, self.payload, **args)
                if args.get('data') is not None:
                    return self.ses.post(self.url, **args)
        except Exception as e:
            return {'RequestError': "{}".format(str(e))}
