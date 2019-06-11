from abc import ABCMeta, abstractmethod


class Pipeline(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, result_items):
        """
        :param result_items: 页面解析后的实体
        :return:
        """
