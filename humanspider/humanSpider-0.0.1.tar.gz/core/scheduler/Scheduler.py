from abc import ABCMeta, abstractmethod


class Scheduler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def put(self, request):
        """
        向队列中增加任务
        """

    @abstractmethod
    def get(self):
        """
        从队列中获取任务
        """

    @abstractmethod
    def close(self):
        """
        关闭队列
        """
