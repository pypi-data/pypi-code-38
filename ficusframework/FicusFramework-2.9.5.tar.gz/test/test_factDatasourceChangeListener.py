#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/2/26
from unittest import TestCase

from api.model.FactDatasource import FactDatasource
from factdatasource.FactDatasourceContextHolder import FactDatasourceContextHolder
from factdatasource.dao.kafka.MultipleKafkaDatasource import MultipleKafkaDatasource
from factdatasource.message.FactDatasourceMessageHanlder import FactDatasourceChangeListener, wait_using_fd


class TestFactDatasourceChangeListener(TestCase):

    def test_message(self):
        # self.send_message()

        datasource = MultipleKafkaDatasource.instance()
        url = 'localhost:9092'
        datasource.add_datasource_type(datasource.DEFAULT_KAFKA_DATASOURCE, url, None)
        # 启动FD改变事件消息监听
        listener = FactDatasourceChangeListener.instance()
        listener.daemon = False
        listener.start()

    def test_wait_using_fd(self):
        fd_context = FactDatasourceContextHolder.instance()
        action = 1
        fd_data = {
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
        fd = FactDatasource(**fd_data)
        wait_using_fd(fd_context, action, fd)


