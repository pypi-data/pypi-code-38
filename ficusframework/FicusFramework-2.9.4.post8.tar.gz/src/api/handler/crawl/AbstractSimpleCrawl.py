import threading
from abc import abstractmethod
from collections import defaultdict

from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.ITaskHandler import ITaskHandler
from api.handler.outputer.ISimpleOutputer import ISimpleOutputer
from api.model.ResultVO import *
from client import DataCrawlClient


class AbstractSimpleCrawl(ITaskHandler, ISimpleOutputer, ICacheAbleHandler):
    """
        简单的Crawl,只需要继承这个类,并且实现do_crawl方法即可
    """

    # 由于这个的实现有可能是 单例的,所以要使用ThreadLocal
    def __init__(self):
        super().__init__()
        self.__code_local_host = threading.local()
        self.__process_id_local = threading.local()
        self.__execution_message_local = threading.local()
        self.killed = False

    def execute(self, params: dict):
        """
        简单的方式的Crawl,就是 实现上 直接返回数据集合.然后由这个抽象类来负责往fd上去写数据
        :param params: 这个参数里面一定要有crawl.
        :return:
        """
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在crawl的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有Crawl的信息")

        # 找到对应的dataCrawl
        data_crawl = DataCrawlClient.get(params["site_"], params["projectCode_"], params["code_"])

        if data_crawl is None or data_crawl.type != "CUSTOM":
            return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{params['site_']}的Crawl,或者该Crawl类型不为Custom")

        # 每一次新的任务都重置这个标识
        self.killed = False

        try:
            self.set_local_code(data_crawl.site + "_" + data_crawl.projectCode + "_" + data_crawl.code)
            self.set_process_id(params.get("__processLogId__"))
            self.__execution_message_local.content = []
            result_list = self.do_crawl(params)
        except Exception as e:
            return ResultVO(FAIL_CODE, f"执行失败,Code:{params['site_']}的Crawl,发生错误:{str(e)}")
        finally:
            # 清理 MessageLocal 和 LocalCode
            self.clear_local_code()
            self.clear_process_id()
            self.__execution_message_local.content = None

        message = "success" if self.__execution_message_local.content is None or len(
            self.__execution_message_local.content) == 0 else str(self.__execution_message_local.content)

        if result_list is None or len(result_list) == 0:
            # 搞完了,没的结果,不处理
            return ResultVO(SUCCESS_CODE, message)

        # 有结果,就需要从crawl的配置中找到目标的fd,然后调用fd的接口进行保存
        output_fd_codes = data_crawl.outputFdCodes

        insert_cache = defaultdict(list)
        update_cache = defaultdict(list)
        upsert_cache = defaultdict(list)

        for serializableOutputWrapper in result_list:
            output_fd = self.find_output_fd(output_fd_codes, serializableOutputWrapper.index())
            self.put_in_cache(data_crawl.code, insert_cache, update_cache, upsert_cache, output_fd,
                              serializableOutputWrapper)

        self.flush_cache(data_crawl.code, insert_cache, update_cache, upsert_cache)

        return ResultVO(SUCCESS_CODE, message)

    def kill(self):
        """
        由于TaskThread就保证了 同一个ITaskHandler同一时间只能为一个logId服务,因此这里可以直接设置一个成员变量即可,不会有问题
        :return:
        """
        self.killed = True

    def is_killed(self):
        return self.killed

    def get_execution_message_cache(self):
        """
        返回message_cache
        :return:
        """
        return self.__execution_message_local.content

    def get_code_thread_local(self):
        """
        实现上下文的code
        :return:
        """
        return self.__code_local_host

    def get_process_thread_local(self):
        """
        上下文的Id
        :return:
        """
        return self.__process_id_local

    @abstractmethod
    def do_crawl(self, params: dict) -> list:
        """
        真正执行数据挖掘的逻辑
        :param params: 需要存入fd中的数据
        :return:
        """
