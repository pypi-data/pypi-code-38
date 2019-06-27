#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/6
import logging
import sys
import time
from abc import abstractmethod
from unittest import TestCase

from munch import Munch


class BaseInitTestSuite(TestCase):
    client = None

    @abstractmethod
    def mock_fact_datasource(self) -> dict:
        """
        设置FD的基本定义,不区分数据源和主数据
        :return: dict<code,FactDatasource>
        """

    def distributed_mode(self) -> bool:
        """
        是否使用分布式的FD，默认使用， 如果要使用ficus中心模式的FD，覆盖此方法
        :return:
        """
        return True

    def centralized_mode_config_path(self) -> str:
        """
        ficus中心模式时，配置文件夹路径,如果sys.path[0]不能满足路径配置，覆盖此方法
        :return:
        """
        return sys.path[0]

    def execute(self, target, param):
        print(f'开始对{param.get("code_")}进行测试')
        start = time.time()
        try:
            from api.model.ResultVO import ResultVO
            result: ResultVO = target.execute(param)
            print(f'测试结果:{result.msg}')
            # 验证结果
            from api.model.ResultVO import SUCCESS
            self.assertEqual(result.code, SUCCESS.code)
        finally:
            print(f'测试结束用时{time.time()-start}')

    def _get_datesource_client(self):
        if self.client is not None:
            return self.client

        from config.BootstrapPropertyLoader import init_from_yaml_property,init_from_environ_property
        config_path = self.centralized_mode_config_path()
        init_from_yaml_property(config_path)
        # 尝试从环境变量中获取 bootstrap里面的信息
        init_from_environ_property()

        if self.distributed_mode():
            from factdatasource.FactDatasourceProxyService import DistributedFactDatasourceProxy
            self.client = DistributedFactDatasourceProxy.instance()
            # 注册所有的数据源
            self.__register_fact_datasource()
        else:
            # from config.BootstrapPropertyLoader import init_from_yaml_property
            # init_from_yaml_property(self.centralized_mode_config_path())
            from init import app
            app.log.info('初始化加载配置')

            from factdatasource.FactDatasourceProxyService import CentralizedFactDatasourceProxy
            self.client = CentralizedFactDatasourceProxy.instance()
        return self.client

    def __register_fact_datasource(self):
        fds = self.mock_fact_datasource()
        from factdatasource.FactDatasourceContextHolder import FactDatasourceContextHolder
        fd_context_holder = FactDatasourceContextHolder.instance()
        for fd in fds.values():
            fd_context_holder.add_fact_datasource(fd)


class ScheduleCacheClientMock(object):
    _cache = dict()

    def set_value(self, key, value):
        if key is None or value is None:
            return
        self._cache[key] = value

    def set_if_absent(self, key, value):
        if key is None or value is None:
            return False

        if key in self._cache.keys():
            return False

        self._cache[key] = value

    def get(self, key):
        if key is None:
            return None
        value = self._cache.get(key)
        if value is not None:
            if isinstance(value, dict):
                return Munch(value)
            else:
                return value
        else:
            return None

    def delete(self, key):
        if key is None:
            return
        del self._cache[key]


class DataCrawl(object):
    def __init__(self, site, projectCode, code, outputFdCodes: list, params: dict = None, **kwargs):
        """
        :param site: 站点，一般定义为S1
        :param projectCode:
        :param code: crawl的唯一标示
        :param outputFdCodes:  输出主数据 list类型 list<fd_code>
        :param params: 执行参数
        :param type:  固定值 CUSTOM
        :param kwargs:  其他参数
        """
        self.site = site
        self.projectCode = projectCode
        self.code = code
        self.params = params
        self.outputFdCodes = outputFdCodes
        self.type = 'CUSTOM'
        self.__fields = {
            'site': site,
            'projectCode': projectCode,
            'code': code,
            'outputFdCodes': outputFdCodes,
            'params': params,
            'type': 'CUSTOM'
        }
        self.__fields.update(**kwargs)

    def to_dict(self):
        return self.__fields


class DataComputeExecution(object):
    def __init__(self, site, projectCode, code, sourceFdCodes: list, outputFdCodes: list, params: dict = None, **kwargs):
        """
        :param site: 站点，一般定义为S1
        :param projectCode:
        :param code: crawl的唯一标示
        :param sourceFdCodes:  输入数据源 list类型 list<fd_code>
        :param outputFdCodes:  输出主数据 list类型 list<fd_code>
        :param params: 执行参数
        :param type:  固定值 CUSTOM
        :param kwargs:  其他参数
        """
        self.site = site
        self.projectCode = projectCode
        self.code = code
        self.params = params
        self.sourceFdCodes = sourceFdCodes
        self.outputFdCodes = outputFdCodes
        self.type = 'CUSTOM'
        self.__fields = {
            'site': site,
            'projectCode': projectCode,
            'code': code,
            'sourceFdCodes': sourceFdCodes,
            'outputFdCodes': outputFdCodes,
            'params': params,
            'type': 'CUSTOM'
        }
        self.__fields.update(**kwargs)

    def to_dict(self):
        return self.__fields


class TaskLoggerMock(object):

    def log(self, append_log: str):
        print(append_log)

    def error(self, e: Exception):
        # sys.stderr.write(str(e))
        logging.exception(e)


PROCESS_LOG_ID = "TEST_PROCESS_LOG_ID"
LOG_ID = 0
