import requests
import urllib3

from core.downloader.Downloader import Downloader
from core.Page import Page

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HttpDownloader(Downloader):
    def __init__(self):
        super().__init__()

    def download(self, request, site):
        """ 下载处理器 """
        url = request.url  # 待请求的链接
        page = Page()
        try:
            resp = requests.request(method=request.method or site.method,
                                    url=url,
                                    headers=request.headers or site.headers,
                                    cookies=request.cookies or site.cookies,
                                    timeout=request.timeout or site.timeOut,
                                    proxies=request.proxies or site.proxy,
                                    verify=request.verify or False,
                                    json=request.json,
                                    data=request.data
                                    )
            page = self.handle_response(request, resp)
            self.on_success(request, resp)
            return page
        except Exception as e:
            self.on_error(request, e)
            page.request = request
            return page

    @staticmethod
    def handle_response(request, response):
        page = Page()
        page.url = request.url
        page.response = response
        page.content = response.content
        page.request = request
        page.headers = response.headers
        page.text = response.text
        page.status_code = response.status_code
        page.download_success = True  # 标记下载成功
        return page

    def set_thread(self, thread_num):
        self.thread_num = thread_num



