#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/6
import threading
from abc import abstractmethod
from datetime import datetime
from unittest.mock import patch, Mock

from munch import Munch

from api.exceptions import IllegalArgumentException
from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.crawl.AbstractBatchCrawl import AbstractBatchCrawl
from api.handler.crawl.AbstractSimpleCrawl import AbstractSimpleCrawl
from api.handler.crawl.ISimpleScriptCrawl import ISimpleScriptCrawl
from api.handler.outputer.ISimpleOutputer import ISimpleOutputer
from api.handler.script import ScriptHandlerHolder
from api.model.ResultVO import ResultVO, FAIL_CODE, SUCCESS
from client import DataCrawlClient
from schedule.test.suite import BaseInitTestSuite, DataCrawl, PROCESS_LOG_ID, LOG_ID, ScheduleCacheClientMock, \
    TaskLoggerMock
from schedule.utils.log import TaskLogFileAppender
from schedule.utils.log.TaskLogger import TaskLogger


class InnerScriptPythonCrawlTestHandler(ISimpleOutputer, ICacheAbleHandler):

    def __init__(self, simple_script_crawl: ISimpleScriptCrawl):
        super().__init__()
        self._simple_script_crawl: ISimpleScriptCrawl = simple_script_crawl
        self.__code_local_host = threading.local()
        self.__process_id_local = threading.local()
        self.__execution_message_local = threading.local()

    def execute(self, params: dict):
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在crawl的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有Crawl的信息")

        # 找到对应的dataCrawl
        data_crawl = DataCrawlClient.get(params["site_"], params["projectCode_"], params["code_"])

        if data_crawl is None or data_crawl.type != "CUSTOM":
            return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{params['site_']}的Crawl,或者该Crawl类型不为Custom")

        # 赋值 日志的上下文
        # log_path = TaskLogFileAppender.prepare_to_log(datetime.now(), LOG_ID)
        # self._simple_script_crawl.task_logger = TaskLogger(log_path)
        # 这里日志输出到控制台，不向日志文件中中记录
        self._simple_script_crawl.task_logger = TaskLoggerMock()

        try:
            self.set_local_code(data_crawl.site + "_" + data_crawl.projectCode + "_" + data_crawl.code)
            self.set_process_id(PROCESS_LOG_ID)
            ScriptHandlerHolder.holder.key = self
            self.__execution_message_local.content = []
            result_list = self._simple_script_crawl.do_crawl(params)
        except Exception as e:
            return ResultVO(FAIL_CODE, f"执行失败,Code:{params['site_']}的Crawl,发生错误:{str(e)}")
        finally:
            # 清理 MessageLocal 和 LocalCode
            self.clear_local_code()
            self.clear_process_id()
            self.__execution_message_local.content = None

            ScriptHandlerHolder.holder.key = None
            self._simple_script_crawl.task_logger = None
        return self._send_results(params, result_list, data_crawl.outputFdCodes)

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
        # 有结果,就需要从crawl的配置中找到目标的fd,然后调用fd的接口进行保存
        try:
            self.send_output_result(params["code_"], result_list, output_fd_codes)
        except Exception as e:
            self._simple_script_crawl.task_logger(
                f"{params['site_']}_{params['projectCode_']}_{params['code_']} 发送结果数据失败,",e)
            return ResultVO(FAIL_CODE, f"发送结果数据失败,错误:{str(e)}")
        return SUCCESS

    def get_code_thread_local(self):
        return self.__code_local_host

    def get_process_thread_local(self):
        return self.__process_id_local

    def get_execution_message_cache(self):
        return self.__execution_message_local.content


class AbstractSimpleScriptCrawlTestSuite(BaseInitTestSuite):
    """
    crawlSimple脚本测试组件
    """
    # region 需要实现的方法
    @abstractmethod
    def mock_target(self) -> ISimpleScriptCrawl:
        """
        设置crawl实例
        :return:
        """

    @abstractmethod
    def mock_fact_datasource(self) -> dict:
        """
        设置FD的基本定义,不区分数据源和主数据
        :return: dict<code,FactDatasource>
        """

    @abstractmethod
    def mock_crawl(self) -> DataCrawl:
        """
        设置crawl的基本定义
        :return: DataCrawl
        """
    # endregion

    # region 内部逻辑
    def setUp(self):
        target: ISimpleScriptCrawl = self.mock_target()
        if not target:
            raise IllegalArgumentException('测试抓取器实例为空')

        fds = self.mock_fact_datasource()
        if not fds:
            raise IllegalArgumentException('测试数据源为空')

        crawl = self.mock_crawl()
        if not crawl:
            raise IllegalArgumentException('测试抓取器定义为空')

    def __fd_client(self):
        return self._get_datesource_client()

    @patch('factdatasource.FactDatasourceProxyService.fd_client_proxy')
    @patch('client.DataCrawlClient.get')
    def crawl_execute(self, mock_crawl_get, mock_fd_client):
        """
        执行测试
        :return:
        """
        mock_crawl_get.return_value = self.__mock_crawl()
        mock_fd_client.return_value = self.__fd_client()

        crawl = self.mock_crawl()
        crawl_param = {
            'site_': crawl.site,
            'projectCode_': crawl.projectCode,
            'code_': crawl.code
        }
        crawl_param.update(crawl.params)

        target: ISimpleScriptCrawl = self.mock_target()
        crawl_handler = InnerScriptPythonCrawlTestHandler(target)

        if self.distributed_mode():
            # 模拟缓存
            cache_mock = ScheduleCacheClientMock()
            with patch('client.ScheduleCacheClient.set_value', Mock(side_effect=cache_mock.set_value)), \
                 patch('client.ScheduleCacheClient.set_if_absent', Mock(side_effect=cache_mock.set_if_absent)), \
                 patch('client.ScheduleCacheClient.get', Mock(side_effect=cache_mock.get)), \
                 patch('client.ScheduleCacheClient.delete', Mock(side_effect=cache_mock.delete)):
                    self.execute(crawl_handler, crawl_param)
        else:
            self.execute(crawl_handler, crawl_param)

    def __mock_crawl(self):
        crawl = self.mock_crawl()
        return Munch(crawl.to_dict())

    def test_crawl_execute(self):
        """
        测试入口
        :return:
        """
        self.crawl_execute()
    # endregion


class AbstractSimpleCrawlTestSuite(BaseInitTestSuite):
    """
    crawlSimple脚本测试组件
    """

    # region 需要实现的方法
    @abstractmethod
    def mock_target(self) -> AbstractSimpleCrawl:
        """
        设置crawl实例
        :return:
        """

    @abstractmethod
    def mock_fact_datasource(self) -> dict:
        """
        设置FD的基本定义,不区分数据源和主数据
        :return: dict<code,FactDatasource>
        """

    @abstractmethod
    def mock_crawl(self) -> DataCrawl:
        """
        设置crawl的基本定义
        :return: DataCrawl
        """
    # endregion

    # region 内部逻辑
    def setUp(self):
        target: AbstractSimpleCrawl = self.mock_target()
        if not target:
            raise IllegalArgumentException('测试抓取器实例为空')

        fds = self.mock_fact_datasource()
        if not fds:
            raise IllegalArgumentException('测试数据源为空')

        crawl = self.mock_crawl()
        if not crawl:
            raise IllegalArgumentException('测试抓取器定义为空')

    def __fd_client(self):
        return self._get_datesource_client()

    def __mock_crawl(self):
        crawl = self.mock_crawl()
        return Munch(crawl.to_dict())

    @patch('factdatasource.FactDatasourceProxyService.fd_client_proxy')
    @patch('client.DataCrawlClient.get')
    def crawl_execute(self, mock_crawl_get, mock_fd_client):
        """
        执行测试
        :return:
        """
        mock_crawl_get.return_value = self.__mock_crawl()
        mock_fd_client.return_value = self.__fd_client()

        crawl = self.mock_crawl()
        crawl_param = {
            'site_': crawl.site,
            'projectCode_': crawl.projectCode,
            'code_': crawl.code
        }
        crawl_param.update(crawl.params)

        target: AbstractSimpleCrawl = self.mock_target()

        # 这里日志输出到控制台，不向日志文件中中记录
        target.task_logger = TaskLoggerMock()

        if self.distributed_mode():
            # 模拟缓存
            cache_mock = ScheduleCacheClientMock()
            with patch('client.ScheduleCacheClient.set_value', Mock(side_effect=cache_mock.set_value)), \
                 patch('client.ScheduleCacheClient.set_if_absent', Mock(side_effect=cache_mock.set_if_absent)), \
                 patch('client.ScheduleCacheClient.get', Mock(side_effect=cache_mock.get)), \
                 patch('client.ScheduleCacheClient.delete', Mock(side_effect=cache_mock.delete)):
                self.execute(target, crawl_param)
        else:
            self.execute(target, crawl_param)

    def test_crawl_execute(self):
        """
        测试入口
        :return:
        """
        self.crawl_execute()
    # endregion


class AbstractBatchCrawlTestSuite(BaseInitTestSuite):
    """
    crawlSimple脚本测试组件
    """
    # region 需要实现的方法
    @abstractmethod
    def mock_target(self) -> AbstractBatchCrawl:
        """
        设置crawl实例
        :return:
        """

    @abstractmethod
    def mock_fact_datasource(self) -> dict:
        """
        设置FD的基本定义,不区分数据源和主数据
        :return: dict<code,FactDatasource>
        """

    @abstractmethod
    def mock_crawl(self) -> DataCrawl:
        """
        设置crawl的基本定义
        :return: DataCrawl
        """
    # endregion

    # region 内部逻辑
    def setUp(self):
        target: AbstractBatchCrawl = self.mock_target()
        if not target:
            raise IllegalArgumentException('测试抓取器实例为空')

        fds = self.mock_fact_datasource()
        if not fds:
            raise IllegalArgumentException('测试数据源为空')

        crawl = self.mock_crawl()
        if not crawl:
            raise IllegalArgumentException('测试抓取器定义为空')

    def __fd_client(self):
        return self._get_datesource_client()

    def __mock_crawl(self):
        crawl = self.mock_crawl()
        return Munch(crawl.to_dict())

    @patch('factdatasource.FactDatasourceProxyService.fd_client_proxy')
    @patch('client.DataCrawlClient.get')
    def crawl_execute(self, mock_crawl_get, mock_fd_client):
        """
        执行测试
        :return:
        """
        mock_crawl_get.return_value = self.__mock_crawl()
        mock_fd_client.return_value = self.__fd_client()

        crawl = self.mock_crawl()
        crawl_param = {
            'site_': crawl.site,
            'projectCode_': crawl.projectCode,
            'code_': crawl.code,
            '__logId__': LOG_ID,
            '__triggerTime__': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '__processLogId__': PROCESS_LOG_ID
        }
        crawl_param.update(crawl.params)

        target: AbstractBatchCrawl = self.mock_target()

        # 这里日志输出到控制台，不向日志文件中中记录
        target.task_logger = TaskLoggerMock()

        if self.distributed_mode():
            # 模拟缓存
            cache_mock = ScheduleCacheClientMock()
            with patch('client.ScheduleCacheClient.set_value', Mock(side_effect=cache_mock.set_value)), \
                 patch('client.ScheduleCacheClient.set_if_absent', Mock(side_effect=cache_mock.set_if_absent)), \
                 patch('client.ScheduleCacheClient.get', Mock(side_effect=cache_mock.get)), \
                 patch('client.ScheduleCacheClient.delete', Mock(side_effect=cache_mock.delete)):
                self.execute(target, crawl_param)
        else:
            self.execute(target, crawl_param)

    def test_crawl_execute(self):
        """
        测试入口
        :return:
        """
        self.crawl_execute()
    # endregion
