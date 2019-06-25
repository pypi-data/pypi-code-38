#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/7
import datetime

import pytz

from api.handler.crawl.AbstractBatchCrawl import AbstractBatchCrawl
from api.model.BatchOutputPipe import BatchOutputPipe
from api.model.FactDatasource import FactDatasource
from schedule.test.suite import DataCrawl
from schedule.test.suite.crawl import AbstractBatchCrawlTestSuite


class DemoAbstractBatchCrawl(AbstractBatchCrawl):

    """CRAWL_python脚本"""
    def do_crawl(self, output_stream: BatchOutputPipe, params: dict):

        date = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        result = {
            "id": 3,
            "tv_name": "CCTV-2",
            "epg_name": "Python-CR",
            "rank": 59,
            "date": date
        }
        if params and params.get("name"):
            name = params.get("name")
            result["name"] = name
            self.task_logger.log(f"CRAWL_PYTHON日志测试，接收到环境变量name:{name}")

        self.task_logger.log("CRAWL_PYTHON日志测试，这里输出普通日志")
        try:
            raise Exception('CRAWL_PYTHON日志测试，这里输出错误日志')
        except Exception as e:
            self.task_logger.error(e)

        # 缓存
        self.set_cache_value('name', 'sobey')
        cache_value = self.get_cache_value('name')
        self.task_logger.log(f"缓存值:{cache_value}")

        output_stream.output_for_upsert(result)

    def kill(self):
        self.task_logger.log("CRAWL_PYTHON脚本被终止")


class TestAbstractBatchCrawlTestSuite(AbstractBatchCrawlTestSuite):

    def mock_target(self):
        return DemoAbstractBatchCrawl()

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

    def mock_crawl(self) -> DataCrawl:
        dc = {
            'site': 'S1',
            'projectCode': 'TEST',
            'code': 'test_script_crawl',
            'outputFdCodes': ['test_source'],
            'params': {
                'name': 'sobey'
            }
        }
        return DataCrawl(**dc)

    def test_execute(self):
        self.test_crawl_execute()
