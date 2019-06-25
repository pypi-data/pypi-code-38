import threading
from abc import abstractmethod
from datetime import datetime

from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.ITaskHandler import ITaskHandler
from api.handler.ce.IMessageCE import IMessageCE
from api.handler.outputer.ISimpleOutputer import ISimpleOutputer
from api.model.FdInputPipe import FdInputPipe
from api.model.ResultVO import ResultVO, FAIL_CODE, SUCCESS
from schedule.utils.log import TaskLogFileAppender, FrameworkHandlerLogger


class AbstractMessageCE(ITaskHandler, IMessageCE, ISimpleOutputer, ICacheAbleHandler):
    """
    消息类型的CE的抽象类
    """

    # 由于这个的实现有可能是 单例的,所以要使用ThreadLocal
    def __init__(self):
        super().__init__()
        self.params = None
        self.dataComputeExecution = None
        self.__code_local_host = threading.local()
        self.__process_id_local = threading.local()
        self.__execution_message_local = threading.local()

    def message(self,data):
        """
        实现 消息接收后的处理
        :param data:
        :return:
        """

        if self.dataComputeExecution is None:
            # 表示还没有初始化
            return

        resultList = None
        try:
            self.set_local_code(f"{self.dataComputeExecution.site}_{self.dataComputeExecution.projectCode}_{self.dataComputeExecution.code}")
            self.set_process_id(self.params.get("__processLogId__"))
            TaskLogFileAppender.prepare_to_log(datetime.strptime(self.params["__triggerTime__"], "%Y-%m-%d %H:%M:%S"),
                                               self.params["code_"])
            resultList = self.do_compute(FdInputPipe(self.dataComputeExecution.sourceFdCodes),data.decode('utf-8'),self.params)
        except Exception as e:
            FrameworkHandlerLogger.log_error(f"{self.dataComputeExecution.site}_{self.dataComputeExecution.projectCode}_{self.dataComputeExecution.code} 接收到消息执行失败,",e)
            return
        finally:
            self.clear_local_code()
            self.clear_process_id()
            TaskLogFileAppender.end_log()

        if  resultList is None or len(resultList)==0:
            # 搞完了,没的结果,不处理
            return

        # 有结果,就需要从crawl的配置中找到目标的fd,然后调用fd的接口进行保存
        outputFdCodes = self.dataComputeExecution.outputFdCodes

        try:
            self.send_output_result(self.dataComputeExecution.code,resultList,outputFdCodes)
        except Exception as e:
            FrameworkHandlerLogger.log_error(f"{self.dataComputeExecution.site}_{self.dataComputeExecution.projectCode}_{self.dataComputeExecution.code} 发送结果数据失败,",e)

    def execute(self, params):
        """
        必须的方法实现
        :param params:
        :return:
        """
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在crawl的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有ce的信息")

        # 这里始终进行刷新赋值,是为了获取最新的ce的变动
        self.params = params

        if  self.dataComputeExecution is not None:
            # 说明已经初始化过了, 就不需要再初始化了
            from client import ComputeExecutionClient
            self.dataComputeExecution = ComputeExecutionClient.get(params["site_"], params["projectCode_"], params["code_"])
            if self.dataComputeExecution is None:
                return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{params['code_']}的Ce")

            return SUCCESS

        return self.init_message_ce(params["site_"], params["projectCode_"], params["code_"])


    def kill(self):
        """
        处理关闭的方法
        :return:
        """
        self.stop()

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
    def do_compute(self, source_fds: FdInputPipe,value, params: dict):
        """
        真正执行数据挖掘的逻辑
        :param output_stream: 数据的输出
        :param source_fds: ce的输入
        :param params: 需要的参数
        :return: list   List<OutputWrapper<Serializable>>
        """