from abc import abstractmethod

from api.handler import HandlerEnum
from api.handler.IHandler import IHandler
from api.handler.script.ICacheAbleScript import ICacheAbleScript
from api.handler.IKillable import IKillable
from api.handler.ILogAbleHandler import ILogAbleHandler


class ISimpleScriptCrawl(IKillable, ILogAbleHandler, ICacheAbleScript, IHandler):
    """
    Python脚本式的Crawl的基类
    """

    @abstractmethod
    def do_crawl(self, params: dict):
        """
        抓取的业务逻辑
        :return: 返回一个 OutputWrapper的 数组
        """
        pass

    def handler_enum(self) -> HandlerEnum:
        return HandlerEnum.SCRIPT

    def is_killed(self)->bool:
        """
        判断是否杀掉了
        :return:
        """
        return False