#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/23

from stomp.connect import StompConnection11

from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from libs.utils import Singleton


class StompDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.JMS)
        return data_source

    @property
    def client(self) -> StompConnection11:
        return self.datasource.get_client()

    def send(self, destination, body, content_type=None, headers=None, **keyword_headers):
        """
        发送消息
        :param destination:
        :param body:
        :param content_type:
        :param headers:
        :param keyword_headers:
        :return:
        """
        self.client.send(destination, body, content_type, headers, **keyword_headers)
