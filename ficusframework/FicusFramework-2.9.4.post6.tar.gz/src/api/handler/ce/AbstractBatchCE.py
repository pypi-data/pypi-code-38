import threading
from abc import abstractmethod
from datetime import datetime
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.ITaskHandler import ITaskHandler
from api.handler.outputer.IBatchOutputer import IBatchOutputer
from api.model.BatchOutputPipe import BatchOutputPipe
from api.model.FdInputPipe import FdInputPipe
from api.model.ResultVO import *
from client import ComputeExecutionClient
from schedule.utils.log import TaskLogFileAppender


class AbstractBatchCE(ITaskHandler, IBatchOutputer, ICacheAbleHandler):
    """
    自定义批量的CE实现
    """
    # 由于这个的实现有可能是 单例的,所以要使用ThreadLocal
    def __init__(self):
        super().__init__()
        self.__code_local_host = threading.local()
        self.__process_id_local = threading.local()
        self.__execution_message_local = threading.local()

        self.__tasks_local_host = threading.local()

        self.killed = False

    def __action(self, data_compute_execution, output_stream, params, is_finished, messages):
        # 异步线程来对数据进行输入
        try:
            self.set_local_code(
                data_compute_execution.site + "_" + data_compute_execution.projectCode + "_" + data_compute_execution.code)
            self.set_process_id(params.get("__processLogId__"))
            self.__execution_message_local.content = []
            TaskLogFileAppender.prepare_to_log(datetime.strptime(params["__triggerTime__"], "%Y-%m-%d %H:%M:%S"),params["__logId__"])
            self.do_compute(BatchOutputPipe(output_stream, len(data_compute_execution.outputFdCodes)),
                            FdInputPipe(data_compute_execution.sourceFdCodes), params)
        finally:
            # 清理 MessageLocal 和 LocalCode
            is_finished[0] = True
            messages[0] = "success" if self.__execution_message_local.content is None or len(
                self.__execution_message_local.content) == 0 else str(self.__execution_message_local.content)

            self.clear_local_code()
            self.clear_process_id()
            self.__execution_message_local.content = None
            TaskLogFileAppender.end_log()


    def execute(self, params):
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在crawl的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有ce的信息")

        self.__tasks_local_host.tasks = []

        output_stream = Queue()

        killed = False

        with ThreadPoolExecutor(max_workers=2,thread_name_prefix="batch-ce-") as executor:

            # 这个的逻辑是这样的:
            # 1.传入一个 队列进去,然后异步等待这个线程做完
            try:
                data_compute_execution = ComputeExecutionClient.get(params["site_"], params["projectCode_"],
                                                                    params["code_"])

                if data_compute_execution is None:
                    return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{params['site_']}的ce")

                is_finished = [False]
                messages = [None]

                self.__tasks_local_host.tasks.append(executor.submit(self.__action,data_compute_execution,output_stream,params,is_finished,messages))


                # 增加发送结果的线程
                self.__tasks_local_host.tasks.append(
                    executor.submit(self.batch_output, params["code_"], data_compute_execution.outputFdCodes, is_finished, output_stream))


                # 阻塞主线程
                for future in as_completed(self.__tasks_local_host.tasks):
                    try:
                        data = future.result()
                    except Exception as e:
                        return ResultVO(FAIL_CODE, f"执行失败,Code:{params['code_']}的CE,原因:{str(e)}")

                if messages[0] is not None:
                    return ResultVO(SUCCESS_CODE, messages[0])

                return SUCCESS
            finally:
                self.__tasks_local_host.tasks.clear()
                executor.shutdown(wait=True)
                output_stream.queue.clear()

    def kill(self):
        self.killed = True
        if self.__tasks_local_host.tasks is not None:
            for task in self.__tasks_local_host.tasks:
                try:
                    task._stop()
                except:
                    pass

    def is_killed(self):
        return self.killed

    def get_execution_message_cache(self):
        """
        返回message_cache
        :return:
        """
        return self.__execution_message_local.content

    def get_batch_size(self) -> int:
        # TODO 先写死100
        return 100

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
    def do_compute(self, output_stream: BatchOutputPipe, source_fds: FdInputPipe, params: dict):
        """
        真正执行数据挖掘的逻辑
        :param output_stream: 数据的输出
        :param source_fds: ce的输入
        :param params: 需要的参数
        :return:
        """
