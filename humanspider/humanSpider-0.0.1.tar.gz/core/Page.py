import copy
import json
from bs4 import BeautifulSoup
from lxml import etree


class Page(object):
    """
    页面对象
    """

    def __init__(self):
        self.targetRequests = []  # 新加入的任务列表
        self.status_code = None
        self.headers = None
        self.content = None
        self.text = None
        self.request = None
        self.url = None
        self.response = None
        self._success = False

    def get_html(self, decode='utf-8'):
        """ 页面文本转html对象 """
        try:
            html = etree.HTML(self.content.decode(decode))
            return html
        except Exception:
            raise Exception

    def get_soup(self, decode='utf-8'):
        """ 页面文本转BeautifulSoup对象 """
        try:
            soup = BeautifulSoup(self.content.decode(decode), 'lxml')
            return soup
        except Exception:
            raise Exception

    def get_json(self, decode='utf-8'):
        """ 页面文本转json对象 """
        try:
            json_obj = json.loads(self.content.decode(decode))
            return json_obj
        except Exception:
            raise Exception

    def add_request_task(self, request):
        """ 接收新的request对象 """
        self.targetRequests.append(request)

    def add_url_task(self, url):
        """ 接收任务url，并使用默认配置 """
        request = self.request
        request.url = url
        self.targetRequests.append(copy.deepcopy(request))

    @property
    def download_success(self):
        """ 标识下载状态 """
        return self._success

    @download_success.setter
    def download_success(self, fail_or_suc):
        self._success = fail_or_suc

