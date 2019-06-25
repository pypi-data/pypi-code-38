from abc import abstractmethod

from api.exceptions import IllegalArgumentException
from api.handler.ICacheAble import ICacheAble
from client import ScheduleCacheClient

CACHE_PREFIX = "sobeyficus.cache."
PROCESS_CACHE_PREFIX = "sobeyficus.process.cache."


class ICacheAbleHandler(ICacheAble):
    """
    缓存操作的接口
    """

    @abstractmethod
    def get_code_thread_local(self):
        """
        需要实现的方法,返回一个 thread_local对象
        :return:
        """

    @abstractmethod
    def get_process_thread_local(self):
        """
        需要实现的方法,返回一个 thread_local对象
        :return:
        """

    # region 同执行器的缓存
    def set_cache_value(self, key, value):
        """
        放入缓存
        :param key:
        :param value:
        :return:
        """
        if key is None or value is None:
            raise IllegalArgumentException("设置任务缓存失败,传入的参数不合法")
        ScheduleCacheClient.set_value(self.__generate_key(key), value)

    def set_cache_value_if_absent(self, key, value):
        """
        放入缓存
        :param key:
        :param value:
        :return:
        """
        if key is None or value is None:
            raise IllegalArgumentException("设置任务缓存失败,传入的参数不合法")
        return ScheduleCacheClient.set_if_absent(self.__generate_key(key), value)

    def get_cache_value(self, key):
        """
        获取缓存
        :param key:
        :return:
        """
        if key is None:
            raise IllegalArgumentException("获取任务缓存失败,传入的参数不合法")
        return ScheduleCacheClient.get(self.__generate_key(key))

    def delete_cache_value(self, key):
        """
        删除缓存
        :param key:
        :return:
        """
        if key is None:
            raise IllegalArgumentException("删除任务缓存失败,传入的参数不合法")
        ScheduleCacheClient.delete(self.__generate_key(key))
    # endregion

    # region 同执行计划的缓存
    def set_cache_value_from_process(self, key, value):
        """
        放入缓存
        :param key:
        :param value:
        :return:
        """
        if key is None or value is None:
            raise IllegalArgumentException("设置任务缓存失败,传入的参数不合法")

        tmp = self.__generate_key_4_process(key)

        if tmp is None:
            raise IllegalArgumentException("设置执行计划缓存失败,没有找到执行计划的Id")

        ScheduleCacheClient.set_value(tmp, value)

    def set_cache_value_if_absent_from_process(self, key, value):
        """
        放入缓存
        :param key:
        :param value:
        :return:
        """
        if key is None or value is None:
            raise IllegalArgumentException("设置任务缓存失败,传入的参数不合法")

        tmp = self.__generate_key_4_process(key)

        if tmp is None:
            raise IllegalArgumentException("设置执行计划缓存失败,没有找到执行计划的Id")

        return ScheduleCacheClient.set_if_absent(tmp, value)

    def get_cache_value_from_process(self, key):
        """
        获取缓存
        :param key:
        :return:
        """
        if key is None:
            raise IllegalArgumentException("获取任务缓存失败,传入的参数不合法")

        tmp = self.__generate_key_4_process(key)

        if tmp is None:
            raise IllegalArgumentException("设置执行计划缓存失败,没有找到执行计划的Id")

        return ScheduleCacheClient.get(tmp)

    def delete_cache_value_from_process(self, key):
        """
        删除缓存
        :param key:
        :return:
        """
        if key is None:
            raise IllegalArgumentException("删除任务缓存失败,传入的参数不合法")

        tmp = self.__generate_key_4_process(key)

        if tmp is None:
            raise IllegalArgumentException("设置执行计划缓存失败,没有找到执行计划的Id")

        ScheduleCacheClient.delete(tmp)
    # endregion

    def __generate_key(self, key):
        """
        生成key
        :param key:
        :return:
        """
        return CACHE_PREFIX + self.get_code_thread_local().key + "." + key

    def __generate_key_4_process(self, key):
        """
        生成key
        :param key:
        :return:
        """
        try:
            if self.get_process_thread_local().key is None:
                return None

            return PROCESS_CACHE_PREFIX + self.get_process_thread_local().key + "." + key
        except:
            # 有可能 self.get_process_thread_local().key 为空,那就返回None
            return None

    # region ThreadLocal Code相关
    def set_local_code(self, code):
        """
        设置key
        :param code:
        :return:
        """
        self.get_code_thread_local().key = code

    def clear_local_code(self):
        """
        清空key
        :return:
        """
        self.get_code_thread_local().key = None

    def set_process_id(self,code):
        """
        设置Key
        :param code:
        :return:
        """
        self.get_process_thread_local().key = code

    def clear_process_id(self):
        """
        清空key
        :return:
        """
        self.get_process_thread_local().key = None
    # endregion