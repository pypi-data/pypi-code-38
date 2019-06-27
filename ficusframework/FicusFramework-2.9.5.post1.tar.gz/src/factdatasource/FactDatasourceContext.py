#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
from abc import abstractmethod

from api.model.Page import Page


class FactDatasourceContext(object):

    @abstractmethod
    def fd(self):
        """
        返回各自保存的fd对象
        :return:
        """

    @abstractmethod
    def size(self) -> int:
        """
        返回数据总长度
        :return: 数据条数:long
        """

    @abstractmethod
    def is_empty(self) -> bool:
        """
        返回是否存在数据
        :return: boolean
        """

    @abstractmethod
    def collect(self, size: int) -> list:
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """

    @abstractmethod
    def query(self, query: str, parameters: dict = None) -> Page:
        """
        使用查询语句查询数据
        查询语句query支持${}和#{}这两种参数占位符，其中值放在parameters中，
        在除JDBC以外的FD中${}和#{}两种占位符是没有区别的，都是直接替换，
        在JDBC中是有区别的，JDBC中的${}是直接进行替换的，#{}这种占位符会转换为sqlalchemy中的:key这种占位符，参数会传到sqlalchemy中进行处理。
        比如 'SELECT * FROM `sc_dataproject` WHERE site=#{site} AND ttl=${ttl}'   {'site': 'S1','ttl': '1'}
        这种经过占位符处理后会转为 'SELECT * FROM `sc_dataproject` WHERE site=:site AND ttl=1'

        parameters支持的默认参数：
            'pageNum_': 页数
            'pageSize_': 每页数量
            'needCount_': 是否进行总数查询
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """

    @abstractmethod
    def inserts(self, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        result_list里边存放的应该是一个dict或者一个可序列化的obj，这个dict的key不能以:开头
        :param result_list: 要保存的数据
        :return: None
        """

    @abstractmethod
    def updates(self, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的,主键的key要求使用'id'
        result_list里边存放的应该是一个dict或者一个可序列化的obj，这个dict的key不能以:开头
        :param result_list: 要修改的数据
        :return: None
        """

    @abstractmethod
    def inserts_or_updates(self, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的,主键的key要求使用'id'
        result_list里边存放的应该是一个dict或者一个可序列化的obj，这个dict的key不能以:开头
        :param result_list: 要添加或者需要修改的数据
        :return: None
        """

    @abstractmethod
    def delete_all(self):
        """
        清空数据
        :return: None
        """

    @abstractmethod
    def delete(self, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :param query: 完整的删除语句
        :return: None
        """

    # @abstractmethod
    # def get_fact_datasource_fields(self):
    #     """
    #     获取fd的字段
    #     :return: List<FactDatasourceField>
    #     """
