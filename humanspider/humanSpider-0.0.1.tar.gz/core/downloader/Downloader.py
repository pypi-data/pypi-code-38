from abc import ABCMeta, abstractmethod

from core.common import logger


class Downloader(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.thread_num = 1

    @abstractmethod
    def download(self, request, site):
        """ 下载处理器 """

    def set_thread(self, thread_num):
        """ 设置并发数 """
        self.thread_num = thread_num

    @staticmethod
    def on_success(request, response):
        logger.info('[Suc] {} 下载页面：{} 成功！ '.format(response.status_code, request.url))

    @staticmethod
    def on_error(request, e):
        logger.error('[Fail] 下载页面:{} 出现异常：{}'.format(request.url, e))



