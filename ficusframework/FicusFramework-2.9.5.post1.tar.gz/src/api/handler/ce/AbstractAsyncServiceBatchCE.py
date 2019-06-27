import threading
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from queue import Queue

import requests

from api.handler.IAsyncAble import IAsyncAble
from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.ITaskHandler import ITaskHandler
from api.handler.outputer.IBatchOutputer import IBatchOutputer
from api.model.AsyncServiceRequest import AsyncServiceRequest, SendType
from api.model.BatchOutputPipe import BatchOutputPipe
from api.model.FdInputPipe import FdInputPipe
from api.model.ResultVO import ResultVO, FAIL_CODE, SUCCESS, DOING, SUCCESS_CODE
from client import ComputeExecutionClient
from schedule.utils.log import TaskLogFileAppender


class AbstractAsyncServiceBatchCE(ITaskHandler, IBatchOutputer, ICacheAbleHandler, IAsyncAble):
    """
    调用 异步服务的Batch处理器
    """

    # 由于这个的实现有可能是 单例的,所以要使用ThreadLocal
    def __init__(self):
        super().__init__()
        self.__code_local_host = threading.local()
        self.__process_id_local = threading.local()
        self.__execution_message_local = threading.local()

        self.__tasks_local_host = threading.local()

        self.killed = False

    def execute(self, params):
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在crawl的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有ce的信息")

        self.__tasks_local_host.tasks = []

        output_stream = Queue()

        self.killed = False

        # 找到对应的ce
        data_compute_execution = ComputeExecutionClient.get(params["site_"], params["projectCode_"],
                                                            params["code_"])

        if data_compute_execution is None:
            return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{params['site_']}的ce")

        try:
            # 这里构造的其实就是 与执行器交互的 协议
            self.set_local_code(
                data_compute_execution.site + "_" + data_compute_execution.projectCode + "_" + data_compute_execution.code)
            self.set_process_id(params.get("__processLogId__"))
            TaskLogFileAppender.prepare_to_log(datetime.strptime(params["__triggerTime__"], "%Y-%m-%d %H:%M:%S"),
                                               params["__logId__"])
            request = self.generate_request(FdInputPipe(data_compute_execution.sourceFdCodes), params)
        finally:
            self.clear_local_code()
            self.clear_process_id()
            TaskLogFileAppender.end_log()

        if request is None:
            # 返回为空,直接就返回了
            return SUCCESS

        jobId = params.get("__jobId__")
        taskLogId = params.get("__logId__")

        if request.send_type is not None and request.send_type == SendType.NOT_NEED_SEND:
            # 如果发送类型不为空,并且是不需要真正的发送出去 ,直接本地调用
            resultVO = self.do_finish(taskLogId, request.body, request.header, params, 3)
            resultVO.msg = "success with no send to actor"
            return resultVO
        else:
            # 需要发送任务给执行器,现在同步和异步任务都是一样的.
            # 发送请求
            # region 补充头
            import config
            headers = {
                'Reply-To': f"http://{config.server_ip or config.find_host_ip()}:{config.server_port or 5000}/async/response/{jobId}/{taskLogId}"}
            if request.header is not None:
                headers.update(request.header)
            # endregion

            global r
            try:
                if "GET" == request.method:
                    r = requests.get(request.url, headers=headers)
                elif "POST" == request.method:
                    if request.body is None:
                        r = requests.post(request.url, headers=headers)
                    else:
                        r = requests.post(request.url, json=request.body, headers=headers)
                elif "PATCH" == request.method:
                    if request.body is None:
                        r = requests.patch(request.url, headers=headers)
                    else:
                        r = requests.patch(request.url, data=request.body, headers=headers)
                elif "PUT" == request.method:
                    if request.body is None:
                        r = requests.put(request.url, headers=headers)
                    else:
                        r = requests.put(request.url, data=request.body, headers=headers)
                elif "DELETE" == request.method:
                    r = requests.delete(request.url, headers=headers)
                elif "HEAD" == request.method:
                    r = requests.head(request.url, headers=headers)
            except Exception as e:
                return ResultVO(FAIL_CODE, f"任务:{taskLogId} 请求{request.url} 失败,请求出错: {str(e)}")

            if r.status_code != 200 or r.content is None:
                return ResultVO(FAIL_CODE, f"任务:{taskLogId} 请求{request.url} 失败,请求出错: {r.content}")

        return DOING

    def __action(self, response, header: dict, task_status: int, data_compute_execution, output_stream, params,
                 is_finished, messages):
        """
        异步线程来对数据进行输入
        :param data_compute_execution:
        :param output_stream:
        :param params:
        :param is_finished:
        :param messages:
        :return:
        """
        try:
            self.set_local_code(
                data_compute_execution.site + "_" + data_compute_execution.projectCode + "_" + data_compute_execution.code)
            self.set_process_id(params.get("__processLogId__"))
            self.__execution_message_local.content = []
            TaskLogFileAppender.prepare_to_log(datetime.strptime(params["__triggerTime__"], "%Y-%m-%d %H:%M:%S"),
                                               params["__logId__"])
            messages[0] = self.do_compute(response, header, task_status,
                                          BatchOutputPipe(output_stream, len(data_compute_execution.outputFdCodes)),
                                          FdInputPipe(data_compute_execution.sourceFdCodes), params)
        finally:
            # 清理 MessageLocal 和 LocalCode
            is_finished[0] = True

            self.clear_local_code()
            self.clear_process_id()
            self.__execution_message_local.content = None
            TaskLogFileAppender.end_log()

    def do_finish(self, task_log_id: int, response, header: dict, ficus_param: dict, task_status: int) -> ResultVO:
        """
        完成的回调处理
        :param task_log_id:
        :param response:
        :param header:
        :param ficus_param:
        :param task_status:
        :return:
        """
        if ficus_param is None or len(ficus_param) == 0 or ("site_" not in ficus_param) or (
                "projectCode_" not in ficus_param) or (
                "code_" not in ficus_param):
            # 不存在crawl的信息,没法执行
            self.task_logger.error(Exception(f"执行失败,没有Ce的信息,taskId:{task_log_id}"))
            return ResultVO(FAIL_CODE, "执行失败,没有Ce的信息")

        self.__tasks_local_host.tasks = []
        output_stream = Queue()

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="async-batch-ce-") as executor:
            try:
                data_compute_execution = ComputeExecutionClient.get(ficus_param["site_"], ficus_param["projectCode_"],
                                                                    ficus_param["code_"])
                if data_compute_execution is None:
                    return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{ficus_param['code_']}的ce")

                is_finished = [False]
                messages = [None]

                self.__tasks_local_host.tasks.append(
                    executor.submit(self.__action, response, header, task_status, data_compute_execution, output_stream,
                                    ficus_param, is_finished, messages))

                # 增加发送结果的线程
                self.__tasks_local_host.tasks.append(
                    executor.submit(self.batch_output, ficus_param["code_"], data_compute_execution.outputFdCodes,
                                    is_finished,
                                    output_stream))
                # 阻塞主线程
                for future in as_completed(self.__tasks_local_host.tasks):
                    try:
                        data = future.result()
                    except Exception as e:
                        return ResultVO(FAIL_CODE, f"执行失败,Code:{ficus_param['code_']}的CE,原因:{str(e)}")

                if messages[0] is not None:
                    return ResultVO(SUCCESS_CODE, messages[0])
                else:
                    return DOING
            finally:
                self.__tasks_local_host.tasks.clear()
                executor.shutdown(wait=True)
                output_stream.queue.clear()

    # region 固定方法相关
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

    # endregion

    # region 需要实现的抽象方法
    @abstractmethod
    def generate_request(self, input_pipe: FdInputPipe, params: dict) -> AsyncServiceRequest:
        """
        生成异步任务的请求的抽象方法
        :param input_pipe:
        :param params:
        :return:
        """
        pass

    @abstractmethod
    def do_compute(self, response, header: dict, task_status: int, output_stream: BatchOutputPipe,
                   source_fds: FdInputPipe, ficus_param: dict) -> str:
        """
        异步任务的返回
        :param response:
        :param header:
        :param task_status:
        :param output_stream:
        :param source_fds:
        :param ficus_param:
        :return:
        """
        pass
    # endregion
