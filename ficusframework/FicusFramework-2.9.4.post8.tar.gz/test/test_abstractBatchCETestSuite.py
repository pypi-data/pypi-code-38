#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/7
import datetime

import pytz

from api.handler.ce.AbstractBatchCE import AbstractBatchCE
from api.model.BatchOutputPipe import BatchOutputPipe
from api.model.FactDatasource import FactDatasource
from api.model.FdInputPipe import FdInputPipe
from schedule.test.suite import DataComputeExecution
from schedule.test.suite.ce import AbstractBatchCETestSuite


class DemoAbstractBatchCE(AbstractBatchCE):
    """CE_python脚本"""
    def do_compute(self, output_stream: BatchOutputPipe, source_fds: FdInputPipe, params: dict):
        date = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        result = {
            "id": 5,
            "tv_name": "CCTV-Python-CE",
            "epg_name": "Python-CE生财有道",
            "rank": 60,
            "date": date
        }
        if params and params.get("name"):
            name = params.get("name")
            result["name"] = name
            self.task_logger.log(f"CE_PYTHON日志测试，接收到环境变量name:{name}")

        self.task_logger.log("CE_PYTHON日志测试，这里输出普通日志")
        try:
            raise Exception('CE_PYTHON日志测试，这里输出错误日志')
        except Exception as e:
            self.task_logger.error(e)

        query_sql = """{"from": 0,"size": 200}"""
        query_result = source_fds.get_fd('test_source').query(query_sql)
        self.task_logger.log(f"CE_PYTHON日志测试，查询结果:{query_result}")

        # 缓存
        self.set_cache_value('name', 'sobey')
        cache_value = self.get_cache_value('name')
        self.task_logger.log(f"缓存值{cache_value}")

        output_stream.output_for_upsert(result)

    def kill(self):
        self.task_logger.log("CE_PYTHON脚本被终止")


class TestAbstractSimpleScriptCETestSuite(AbstractBatchCETestSuite):

    def mock_target(self) -> AbstractBatchCE:
        return DemoAbstractBatchCE()

    def mock_fact_datasource(self) -> dict:
        fd = {
            "code": "test_source",
            "connection": "localhost:9200",
            "credentials": None,
            "model": None,
            "name": "test_source",
            "privilege": None,
            "projectCode": "TEST",
            "site": "S1",
            "tags": [
                "masterData"
            ],
            "target": "es_test",
            "ttl": 0,
            "type": "ES"
        }

        fds = {
            'test_source': FactDatasource(**fd)
        }
        return fds

    def mock_ce(self) -> DataComputeExecution:
        dc = {
            'site': 'S1',
            'projectCode': 'TEST',
            'code': 'test_script_crawl',
            'sourceFdCodes': ['test_source'],
            'outputFdCodes': ['test_source'],
            'params': {
                'name': 'sobey'
            }
        }
        return DataComputeExecution(**dc)

    def test_execute(self):
        self.test_ce_execute()
