from abc import ABCMeta, abstractmethod


class PageProcessor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, page):
        """
        页面处理方法
        """

    @abstractmethod
    def get_site(self):
        """
        爬虫全局配置
        """
