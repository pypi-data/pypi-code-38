#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/7
import datetime

import pytz

from api.annotation.annotation import TaskHandler
from api.handler.crawl.AbstractSimpleCrawl import AbstractSimpleCrawl
from api.model.FactDatasource import FactDatasource
from schedule import TaskHandlerContext
from schedule.test.suite import DataCrawl
from schedule.test.suite.crawl import AbstractSimpleCrawlTestSuite


@TaskHandler("demoAbstractSimpleCrawl")
class DemoAbstractSimpleCrawl(AbstractSimpleCrawl):

    """CRAWL_python脚本"""
    def do_crawl(self, params: dict):

        date = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        result = {
            "id": 2,
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
        self.task_logger.log(f"缓存值{cache_value}")

        from api.model import OutputWrapper
        return [OutputWrapper.UPSERT(result)]

    def kill(self):
        self.task_logger.log("CRAWL_PYTHON脚本被终止")


class TestAbstractSimpleCrawlTestSuite(AbstractSimpleCrawlTestSuite):

    def mock_target(self):
        return TaskHandlerContext.load_task_handler("demoAbstractSimpleCrawl")

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
