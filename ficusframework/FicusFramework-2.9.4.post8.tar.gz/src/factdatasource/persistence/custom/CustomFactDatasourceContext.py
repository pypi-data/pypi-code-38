#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import logging

from api.model.FactDatasource import FactDatasource
from factdatasource.execptions import NotSupportedFDException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext

log = logging.getLogger('Ficus')


class CustomFactDatasourceContext(AbstractFactDatasourceContext):

    def __init__(self, fact_datasource: FactDatasource):
        raise NotSupportedFDException('暂时不支持该FD类型')
        super(AbstractFactDatasourceContext, self).__init__(fact_datasource)

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """

    def query(self, query: str, parameters: dict):
        """
        使用查询语句查询数据
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """

    def delete_all(self):
        """
        清空数据
        :return:
        """

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :return:
        """

