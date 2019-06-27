#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/30
from unittest import TestCase

from factdatasource.FactDatasourceContextHolder import FactDatasourceContextHolder
from factdatasource.dao.jdbc.MultipleJdbcDatasource import MultipleJdbcDatasource


def register_default_datasource():
    # ficus数据库配置
    credentials = 'sobeyhive:$0bEyHive&2o1Six'
    url = 'jdbc:mysql://localhost:3306/ficus'
    datasource = MultipleJdbcDatasource.instance()
    datasource.add_datasource_type(datasource.DEFAULT_DATASOURCE, url, credentials)


class TestDistributedFactDatasourceProxy(TestCase):

    def test_size(self):
        register_default_datasource()
        fd_context_holder = FactDatasourceContextHolder.instance()
        fd_context1 = fd_context_holder.get_fact_datasource('test_source_1')
        size = fd_context1.size()
        print(f'数据源test_source_1长度{size}')

        fd_context2 = fd_context_holder.get_fact_datasource('test_source_2')
        size = fd_context2.size()
        print(f'数据源test_source_2长度{size}')

        print(fd_context2.collect(5))

        print(fd_context1.collect(5))
