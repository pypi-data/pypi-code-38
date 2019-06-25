#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/8
import threading
from abc import abstractmethod
from datetime import datetime
from unittest.mock import patch, Mock

from munch import Munch

from api.exceptions import IllegalArgumentException
from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.ITaskHandler import ITaskHandler
from api.handler.ce.AbstractBatchCE import AbstractBatchCE
from api.handler.ce.ISimpleScriptCE import ISimpleScriptCE
from api.handler.outputer.ISimpleOutputer import ISimpleOutputer
from api.handler.script import ScriptHandlerHolder
from api.model.FdInputPipe import FdInputPipe
from api.model.ResultVO import ResultVO, FAIL_CODE, SUCCESS
from client import ComputeExecutionClient
from schedule.test.suite import BaseInitTestSuite, PROCESS_LOG_ID, LOG_ID, ScheduleCacheClientMock
from schedule.test.suite import DataComputeExecution


class InnerScriptPythonCrawlTestHandler(ITaskHandler, ISimpleOutputer, ICacheAbleHandler):

    def __init__(self, simple_script_ce: ISimpleScriptCE):
        super().__init__()
        self._simple_script_ce = simple_script_ce
        self.__code_local_host = threading.local()
        self.__process_id_local = threading.local()
        self.__execution_message_local = threading.local()

    def execute(self, params: dict):
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在ce的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有ce的信息")

        # 找到对应的dataCrawl
        data_ce = ComputeExecutionClient.get(params["site_"], params["projectCode_"], params["code_"])

        if data_ce is None or data_ce.type != "CUSTOM":
            return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{params['site_']}的ce,或者该ce类型不为Custom")

        # 赋值 日志的上下文
        from schedule.utils.log.TaskLogger import TaskLogger
        from schedule.utils.log import TaskLogFileAppender
        log_path = TaskLogFileAppender.prepare_to_log(datetime.now(), 0)
        self._simple_script_ce.task_logger = TaskLogger(log_path)

        try:
            self.set_local_code(data_ce.site + "_" + data_ce.projectCode + "_" + data_ce.code)
            self.set_process_id(PROCESS_LOG_ID)
            ScriptHandlerHolder.holder.key = self
            self.__execution_message_local.content = []

            result_list = self._simple_script_ce.do_compute(FdInputPipe(data_ce.sourceFdCodes), params)
        except Exception as e:
            return ResultVO(FAIL_CODE, f"执行失败,Code:{params['site_']}的CE,发生错误:{str(e)}")
        finally:
            # 清理 MessageLocal 和 LocalCode
            self.clear_local_code()
            self.clear_process_id()
            self.__execution_message_local.content = None
            ScriptHandlerHolder.holder.key = None
            self._simple_script_ce.task_logger = None
        return self._send_results(params, result_list, data_ce.outputFdCodes)

    def _send_results(self, params, result_list, output_fd_codes):
        """
        发送结果数据
        :param params:
        :param result_list:
        :param output_fd_codes:
        :return:
        """
        if result_list is None or len(result_list) == 0:
            # 搞完了,没的结果,不处理
            return SUCCESS
        # 有结果,就需要从ce的配置中找到目标的fd,然后调用fd的接口进行保存
        try:
            self.send_output_result(params["code_"], result_list, output_fd_codes)
        except Exception as e:
            self._simple_script_ce.task_logger(
                f"{params['site_']}_{params['projectCode_']}_{params['code_']} 发送结果数据失败,", e)
            return ResultVO(FAIL_CODE, f"发送结果数据失败,错误:{str(e)}")
        return SUCCESS

    def get_code_thread_local(self):
        return self.__code_local_host

    def get_process_thread_local(self):
        return self.__process_id_local

    def get_execution_message_cache(self):
        return self.__execution_message_local.content


class AbstractSimpleScriptCETestSuite(BaseInitTestSuite):
    """
    CeSimple脚本测试组件
    """
    # region 需要实现的方法
    @abstractmethod
    def mock_target(self) -> ISimpleScriptCE:
        """
        设置ce实例
        :return:
        """

    @abstractmethod
    def mock_fact_datasource(self) -> dict:
        """
        设置FD的基本定义,不区分数据源和主数据
        :return: dict<code,FactDatasource>
        """

    @abstractmethod
    def mock_ce(self) -> DataComputeExecution:
        """
        设置ce的基本定义
        :return: DataComputeExecution
        """
    # endregion

    # region 内部逻辑
    def setUp(self):
        target = self.mock_target()
        if not target:
            raise IllegalArgumentException('测试抓取器实例为空')

        fds = self.mock_fact_datasource()
        if not fds:
            raise IllegalArgumentException('测试数据源为空')

        ce = self.mock_ce()
        if not ce:
            raise IllegalArgumentException('测试抓取器定义为空')

    def __fd_client(self):
        return self._get_datesource_client()

    def __mock_ce(self):
        ce = self.mock_ce()
        return Munch(ce.to_dict())

    @patch('factdatasource.FactDatasourceProxyService.fd_client_proxy')
    @patch('client.ComputeExecutionClient.get')
    def ce_execute(self, mock_ce_get, mock_fd_client):
        """
        执行测试
        :return:
        """
        mock_ce_get.return_value = self.__mock_ce()
        mock_fd_client.return_value = self.__fd_client()

        ce = self.mock_ce()
        ce_param = {
            'site_': ce.site,
            'projectCode_': ce.projectCode,
            'code_': ce.code
        }
        ce_param.update(ce.params)

        target: ISimpleScriptCE = self.mock_target()
        ce_handler = InnerScriptPythonCrawlTestHandler(target)

        if self.distributed_mode():
            # 模拟缓存
            cache_mock = ScheduleCacheClientMock()
            with patch('client.ScheduleCacheClient.set_value', Mock(side_effect=cache_mock.set_value)), \
                 patch('client.ScheduleCacheClient.set_if_absent', Mock(side_effect=cache_mock.set_if_absent)), \
                 patch('client.ScheduleCacheClient.get', Mock(side_effect=cache_mock.get)), \
                 patch('client.ScheduleCacheClient.delete', Mock(side_effect=cache_mock.delete)):
                self.execute(ce_handler, ce_param)
        else:
            self.execute(ce_handler, ce_param)

    def test_ce_execute(self):
        """
        测试入口
        :return:
        """
        self.ce_execute()
    # endregion


class AbstractBatchCETestSuite(BaseInitTestSuite):
    """
    CeSimple脚本测试组件
    """
    # region 需要实现的方法
    @abstractmethod
    def mock_target(self) -> AbstractBatchCE:
        """
        设置ce实例
        :return:
        """

    @abstractmethod
    def mock_fact_datasource(self) -> dict:
        """
        设置FD的基本定义,不区分数据源和主数据
        :return: dict<code,FactDatasource>
        """

    @abstractmethod
    def mock_ce(self) -> DataComputeExecution:
        """
        设置ce的基本定义
        :return: DataComputeExecution
        """
    # endregion

    # region 内部逻辑
    def setUp(self):
        target = self.mock_target()
        if not target:
            raise IllegalArgumentException('测试抓取器实例为空')

        fds = self.mock_fact_datasource()
        if not fds:
            raise IllegalArgumentException('测试数据源为空')

        ce = self.mock_ce()
        if not ce:
            raise IllegalArgumentException('测试抓取器定义为空')

    def __fd_client(self):
        return self._get_datesource_client()

    def __mock_ce(self):
        ce = self.mock_ce()
        return Munch(ce.to_dict())

    @patch('factdatasource.FactDatasourceProxyService.fd_client_proxy')
    @patch('client.ComputeExecutionClient.get')
    def ce_execute(self, mock_ce_get, mock_fd_client):
        """
        执行测试
        :return:
        """
        mock_ce_get.return_value = self.__mock_ce()
        mock_fd_client.return_value = self.__fd_client()

        ce = self.mock_ce()
        ce_param = {
            'site_': ce.site,
            'projectCode_': ce.projectCode,
            'code_': ce.code,
            '__logId__': LOG_ID,
            '__triggerTime__': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '__processLogId__': PROCESS_LOG_ID
        }
        ce_param.update(ce.params)

        target: AbstractBatchCE = self.mock_target()

        if self.distributed_mode():
            # 模拟缓存
            cache_mock = ScheduleCacheClientMock()
            with patch('client.ScheduleCacheClient.set_value', Mock(side_effect=cache_mock.set_value)), \
                 patch('client.ScheduleCacheClient.set_if_absent', Mock(side_effect=cache_mock.set_if_absent)), \
                 patch('client.ScheduleCacheClient.get', Mock(side_effect=cache_mock.get)), \
                 patch('client.ScheduleCacheClient.delete', Mock(side_effect=cache_mock.delete)):
                self.execute(target, ce_param)
        else:
            self.execute(target, ce_param)

    def test_ce_execute(self):
        """
        测试入口
        :return:
        """
        self.ce_execute()
    # endregion

