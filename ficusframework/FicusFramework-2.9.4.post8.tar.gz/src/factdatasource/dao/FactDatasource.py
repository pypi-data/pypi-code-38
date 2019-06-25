#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
import threading
from abc import abstractmethod

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.execptions import CustomerDaoContextNotFoundException


class DatasourceListener(object):
    """
    用于监听数据源变化后的动作的
    """

    @abstractmethod
    def get_datasource_type(self) -> FactDatasourceTypeEnum:
        """
        获取数据源类型
        :return:
        """

    @abstractmethod
    def add_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        添加一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """

    @abstractmethod
    def update_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        修改一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """

    @abstractmethod
    def delete_datasource_type(self, source_name: str):
        """
        删除一个数据源
        :param source_name:
        :return:
        """


class Datasource(object):
    """基础数据源操作"""

    @abstractmethod
    def get_client(self):
        """
        获取数据库操作的client
        :return:
        """

    @abstractmethod
    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """


class MultipleBaseDatasource(Datasource):
    """封装数据源的基本操作"""

    @abstractmethod
    def get_data_source(self):
        """
        获取数据源的基本信息
        :return:
        """

    def determine_current_lookup_key(self):
        """
        获取当前线程操作的数据源
        :return:
        """
        source_name = customer_dao_context_holder.get_source()
        if source_name is None:
            raise CustomerDaoContextNotFoundException('未设置上下文的数据源，无法执行操作。')
        return source_name


class BaseDatasource(Datasource):

    def init(self, source_name, url, credentials):
        if not source_name or not url:
            raise IllegalArgumentException(f'创建数据源失败，参数错误：{source_name},{url}')

        self._url = url
        self._credentials = credentials

        self._source = set()
        self._source.add(source_name)

    @abstractmethod
    def start(self):
        """分析url并开始连接数据库,设置客户端"""

    @abstractmethod
    def get_client(self):
        """
        获取数据操作的客户端
        :return:
        """

    @abstractmethod
    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """

    @property
    def url(self):
        return self._url

    @property
    def credentials(self):
        return self._credentials

    def add_source_name(self, ref_source_name):
        """
        当多个source使用同一个连接时，调用该方法，将该source纳入管理
        :param ref_source_name:
        :return:
        """
        self._source.add(ref_source_name)

    def remove_source_name(self, ref_source_name):
        """
        删除引用
        :param ref_source_name:
        :return:
        """
        self._source.remove(ref_source_name)

    def only_one_source(self):
        """判断该数据源是否只被一个FD享用"""
        return len(self._source) == 1


class CustomerDaoContextHolder(object):
    """
    线程的上下文,用于切换数据源. Key是系统的名字
    """

    def __init__(self):
        self.__context_holder = threading.local()
        # 由于需要在不同的线程中来判断某一个数据源是否正在使用，所以这里个添加一个变量来记录正在使用的数据源
        self.__global_context = list()

    def set_source(self, source_name: str):
        self.__context_holder.source_name = source_name
        self.__global_context.append(source_name)

    def get_source(self):
        try:
            return self.__context_holder.source_name
        except AttributeError as error:
            return None

    def clear_source(self):
        self.__global_context.remove(self.__context_holder.source_name)
        self.__context_holder.source_name = None

    def is_using(self, source_name: str):
        return source_name in self.__global_context


customer_dao_context_holder = CustomerDaoContextHolder()

