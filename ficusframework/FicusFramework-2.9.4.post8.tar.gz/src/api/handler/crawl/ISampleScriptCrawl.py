import warnings
from abc import abstractmethod

from api.handler.crawl.ISimpleScriptCrawl import ISimpleScriptCrawl

warnings.warn("'ISampleScriptCrawl'类已被废弃,请使用'ISimpleScriptCrawl'类代替 ", DeprecationWarning, 2)


class ISampleScriptCrawl(ISimpleScriptCrawl):
    """
    Python脚本式的Crawl的基类
    """

    @abstractmethod
    def do_crawl(self, params: dict):
        """
        抓取的业务逻辑
        :return: 返回一个 OutputWrapper的 数组
        """
        warnings.warn("'ISampleScriptCrawl'类已被废弃,请使用'ISimpleScriptCrawl'类代替 ", DeprecationWarning, 2)
        pass
