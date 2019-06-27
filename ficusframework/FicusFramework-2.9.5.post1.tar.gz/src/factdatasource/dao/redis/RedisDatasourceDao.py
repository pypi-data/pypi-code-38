#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/2/21
from redis import StrictRedis

from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from libs.utils import Singleton


class RedisDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.REDIS)
        return data_source

    @property
    def client(self) -> StrictRedis:
        return self.datasource.get_client()

