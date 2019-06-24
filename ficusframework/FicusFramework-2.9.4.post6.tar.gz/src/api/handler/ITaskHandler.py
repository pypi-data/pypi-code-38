"""
执行器的接口
"""
from abc import abstractmethod

from api.handler import HandlerEnum
from api.handler.IHandler import IHandler
from api.handler.IKillable import IKillable
from api.handler.ILogAbleHandler import ILogAbleHandler


class ITaskHandler(ILogAbleHandler,IHandler,IKillable):

    @abstractmethod
    def execute(self, params):
        """
        执行任务
        :return:
        """

    @abstractmethod
    def get_execution_message_cache(self):
        """
        获取执行消息的写入器
        :return:
        """

    def write_execution_message(self, execution_message):
        """
        写入执行消息
        :param execution_message:
        :return:
        """
        if self.get_execution_message_cache() is not None:
            self.get_execution_message_cache().add(execution_message)

    def handler_enum(self) -> HandlerEnum:
        return HandlerEnum.NORMAL


