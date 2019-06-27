import threading
from datetime import datetime

from api.handler import HandlerEnum
from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.ITaskHandler import ITaskHandler
from api.handler.outputer.ISimpleOutputer import ISimpleOutputer
from api.handler.script import ScriptPythonFactory, ScriptHandlerHolder
from api.model.FdInputPipe import FdInputPipe
from api.model.ResultVO import *
from client import ComputeExecutionClient, DataCrawlClient
from schedule.utils.log import FrameworkHandlerLogger


class ScriptPythonTaskHandler(ITaskHandler,ISimpleOutputer, ICacheAbleHandler):
    """
    Python脚本的执行器
    """

    # 由于这个的实现有可能是 单例的,所以要使用ThreadLocal

    def __init__(self, job_id, update_time, script_source):
        super().__init__()
        self.__code_local_host = threading.local()
        self.__process_id_local = threading.local()
        self.__execution_message_local = threading.local()

        self.job_id = job_id
        self.update_time = update_time
        self.script_source = script_source
        self.killed = False
        self.current_task = None

    def update_time(self):
        return self.update_time

    def execute(self, params):
        """
        执行Python脚本的处理
        :param params:
        :return:
        """
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在ce的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有找到执行器的信息")

        self.killed = False

        # 获取ce定义
        dataComputeExecution = ComputeExecutionClient.get(params["site_"], params["projectCode_"], params["code_"])

        if dataComputeExecution is None:
            # 说明有可能是crawl
            dataCrawl = DataCrawlClient.get(params["site_"], params["projectCode_"], params["code_"])
            if dataCrawl is None:
                ResultVO(FAIL_CODE, "执行失败,没有找到执行器的信息")
            return self.do_crawl(dataCrawl, params)

        return self.do_script_compute_execution(dataComputeExecution,params)


    def kill(self):
        self.killed = True

        if  self.current_task is not None:
            try:
                self.current_task.kill()
            except Exception as e:
                FrameworkHandlerLogger.log_error(
                    f"当前正在执行的任务强制停止失败: {str(e)}")

        ScriptPythonFactory.destroy_instance(f"ScriptPython{self.job_id}")

    def is_killed(self):
        return self.killed

    def get_execution_message_cache(self):
        """
        返回message_cache
        :return:
        """
        return self.__execution_message_local.content

    def get_code_thread_local(self):
        return self.__code_local_host

    def get_process_thread_local(self):
        """
        上下文的Id
        :return:
        """
        return self.__process_id_local

    def do_crawl(self, dataCrawl, params):
        """
        执行动态的crawl
        :param dataCrawl:
        :param params:
        :return:
        """
        # 这里动态的加载script源文件
        instance = ScriptPythonFactory.load_instance(f"ScriptPython{self.job_id}", self.script_source,"IHandler")

        if instance.handler_enum() == HandlerEnum.NORMAL:
            return self.__inner_do_normal_crawl(instance,params)
        else:
            return self.__inner_do_script_crawl(instance, dataCrawl, params)

    def do_script_compute_execution(self, dataComputeExecution, params):
        """
        执行ce的脚本
        :param dataComputeExecution:
        :param params:
        :return:
        """

        # 这里动态的加载script源文件
        instance = ScriptPythonFactory.load_instance(f"ScriptPython{self.job_id}", self.script_source,"IHandler")

        if instance.handler_enum() == HandlerEnum.NORMAL:
            return self.__inner_do_normal_compute_execution(instance, params)
        else:
            return self.__inner_do_script_compute_execution(instance, dataComputeExecution, params)


    def _send_results(self,params, resultList,outputFdCodes):
        """
        发送结果数据
        :param params:
        :param resultList:
        :param outputFdCodes:
        :return:
        """
        if resultList is None or len(resultList) == 0:
            # 搞完了,没的结果,不处理
            return SUCCESS
        # 有结果,就需要从crawl的配置中找到目标的fd,然后调用fd的接口进行保存

        try:
            self.send_output_result(params["code_"], resultList, outputFdCodes)
        except Exception as e:
            FrameworkHandlerLogger.log_error(
                f"{params['site_']}_{params['projectCode_']}_{params['code_']} 发送结果数据失败,",e)
        return SUCCESS

    def __inner_do_script_crawl(self, instance, dataCrawl, params):
        simpleScriptCrawl = instance
        self.current_task = simpleScriptCrawl

        # 赋值 日志的上下文
        from schedule.utils.log.TaskLogger import TaskLogger
        from schedule.utils.log import TaskLogFileAppender
        simpleScriptCrawl.task_logger = TaskLogger(
            TaskLogFileAppender.get_log_file_path(datetime.strptime(params["__triggerTime__"], "%Y-%m-%d %H:%M:%S"),
                                                  params["__logId__"]))

        try:
            self.set_local_code(
                f"{dataCrawl.site}_{dataCrawl.projectCode}_{dataCrawl.code}")
            self.set_process_id(params.get("__processLogId__"))
            ScriptHandlerHolder.holder.key = self
            resultList = simpleScriptCrawl.do_crawl(params)
        except Exception as e:
            FrameworkHandlerLogger.log_error(
                f"{dataCrawl.site}_{dataCrawl.projectCode}_{dataCrawl.code} 执行失败,", e)
            return ResultVO(FAIL_CODE,
                            f"{dataCrawl.site}_{dataCrawl.projectCode}_{dataCrawl.code} 执行失败,{str(e)}")
        finally:
            self.clear_local_code()
            self.clear_process_id()
            ScriptHandlerHolder.holder.key = None
            self.current_task = None
            simpleScriptCrawl.task_logger = None

        return self._send_results(params, resultList, dataCrawl.outputFdCodes)

    def __inner_do_normal_crawl(self, instance, params):
        self.current_task = instance

        # TODO 这里可能需要补充一些 taskThread里面的东西
        try:
            return instance.execute(params)
        finally:
            # 如果是普通的,就不能把current_task设置为空
            # self.current_task = None
            pass

    def __inner_do_script_compute_execution(self, instance, dataComputeExecution, params):
        simpleScriptCE = instance
        self.current_task = simpleScriptCE

        # 赋值 日志的上下文
        from schedule.utils.log.TaskLogger import TaskLogger
        from schedule.utils.log import TaskLogFileAppender
        simpleScriptCE.task_logger = TaskLogger(
            TaskLogFileAppender.get_log_file_path(datetime.strptime(params["__triggerTime__"], "%Y-%m-%d %H:%M:%S"),
                                                  params["__logId__"]))

        try:
            self.set_local_code(
                f"{dataComputeExecution.site}_{dataComputeExecution.projectCode}_{dataComputeExecution.code}")
            self.set_process_id(params.get("__processLogId__"))
            ScriptHandlerHolder.holder.key = self
            resultList = simpleScriptCE.do_compute(FdInputPipe(dataComputeExecution.sourceFdCodes), params)
        except Exception as e:
            FrameworkHandlerLogger.log_error(
                f"{dataComputeExecution.site}_{dataComputeExecution.projectCode}_{dataComputeExecution.code} 执行失败,", e)
            return ResultVO(FAIL_CODE,
                            f"{dataComputeExecution.site}_{dataComputeExecution.projectCode}_{dataComputeExecution.code} 执行失败,{str(e)}")
        finally:
            self.clear_local_code()
            self.clear_process_id()
            ScriptHandlerHolder.holder.key = None
            self.current_task = None
            simpleScriptCE.task_logger = None

        return self._send_results(params, resultList, dataComputeExecution.outputFdCodes)

    def __inner_do_normal_compute_execution(self, instance, params):
        self.current_task = instance

        # TODO 这里可能需要补充一些 taskThread里面的东西
        try:
            return instance.execute(params)
        finally:
            # 如果是普通的,就不能把current_task设置为空
            # self.current_task = None
            pass
