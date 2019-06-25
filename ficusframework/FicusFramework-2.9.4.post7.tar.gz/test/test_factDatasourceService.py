#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/31
from unittest import TestCase

from factdatasource.dao.jdbc.MultipleJdbcDatasource import MultipleJdbcDatasource
from service.FactDatasourceService import FactDatasourceService


def register_default_datasource():
    # ficus数据库配置
    credentials = 'sobeyhive:$0bEyHive&2o1Six'
    url = 'jdbc:mysql://localhost:3306/ficus'
    datasource = MultipleJdbcDatasource.instance()
    datasource.add_datasource_type(datasource.DEFAULT_DATASOURCE, url, credentials)


class TestFactDatasourceService(TestCase):

    def test_get_fd_by_code(self):
        register_default_datasource()
        fd_service = FactDatasourceService.instance()
        fd = fd_service.get_fd_by_code('test_source_1')
        print(fd.get_source_name())

        fdx = fd_service.get_fd_by_code('test_source_x')
        print(fdx)

    def test_exists_fds(self):
        register_default_datasource()
        fd_service = FactDatasourceService.instance()
        fd_codes = ['test_source_1', 'test_source_2']
        # fd_codes = ['test_source_1', 'test_source_2', 'test_source_x']
        # fd_codes = ['test_source_x']
        is_exists = fd_service.exists_fds(fd_codes)
        print(is_exists)
