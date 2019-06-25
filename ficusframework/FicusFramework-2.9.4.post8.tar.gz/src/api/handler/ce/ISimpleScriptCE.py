from abc import abstractmethod

from api.handler import HandlerEnum
from api.handler.IHandler import IHandler
from api.handler.script.ICacheAbleScript import ICacheAbleScript
from api.handler.IKillable import IKillable
from api.handler.ILogAbleHandler import ILogAbleHandler
from api.model.FdInputPipe import FdInputPipe


class ISimpleScriptCE(IKillable, ILogAbleHandler, ICacheAbleScript, IHandler):
    """
    Python脚本式的CE的基类
    """

    @abstractmethod
    def do_compute(self, source_fds: FdInputPipe, params: dict):
        """
        计算器的业务逻辑
        :param source_fds: 输入源FD
        :param params: 计算器上下文参数
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
