#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from stomp.connect import stomp, StompConnection11

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import DatasourceListener, MultipleBaseDatasource, BaseDatasource
from factdatasource.execptions import DatasourceNotFoundException, FDExecuteException
from libs.utils import Singleton


class MultipleStompDatasource(DatasourceListener, MultipleBaseDatasource, Singleton):
    """
    管理fd中的所有STOMP类型的数据源  stomp类的数据源在ficus中的类型是JMS
    """

    def __init__(self):
        # source_name --> StompDatasource
        self._target_dataSources = dict()

    def get_datasource_type(self):
        """
        获取数据源类型
        :return:
        """
        return FactDatasourceTypeEnum.JMS

    def add_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        添加一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """
        if not source_name or not url:
            raise IllegalArgumentException(f'添加数据源参数错误:source_name、url都不能为空')

        for target in self._target_dataSources.values():
            if target.url == url and target.credentials == credentials:
                # url 和 credentials 都相同，说明是同一个数据库连接就不再重复创建数据源了
                target.add_source_name(source_name)
                self._target_dataSources[source_name] = target
                return

        # 开始创建数据源
        stomp_data_source = StompDatasource(source_name, url, credentials)
        stomp_data_source.start()
        self._target_dataSources[source_name] = stomp_data_source

    def update_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        修改一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """
        if not source_name or not url:
            raise IllegalArgumentException(f'修改数据源参数错误:source_name、url都不能为空')

        self.delete_datasource_type(source_name)
        self.add_datasource_type(source_name, url, credentials)

    def delete_datasource_type(self, source_name: str):
        """
        删除一个数据源
        :param source_name:
        :return:
        """
        target: StompDatasource = self._target_dataSources.pop(source_name)
        if target:
            if target.only_one_source():
                target.close_client()
            else:
                target.remove_source_name(source_name)

    def get_data_source(self):
        """
        获取数据源的基本信息
        :return:
        """
        source_name = self.determine_current_lookup_key()
        if not source_name:
            raise FDExecuteException('未设置操作源,无法获取数据源信息。')

        if source_name in self._target_dataSources.keys():
            return self._target_dataSources[source_name]
        raise DatasourceNotFoundException('未发现数据源%s。' % source_name)

    def get_client(self):
        """
        获取数据库操作的client
        :return:
        """
        target: StompDatasource = self.get_data_source()
        return target.get_client()

    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """
        target: StompDatasource = self.get_data_source()
        return target.close_client()


class StompDatasource(BaseDatasource):

    def __init__(self, source_name, url, credentials):
        self.init(source_name, url, credentials)
        self.client: StompConnection11 = None

    def start(self):
        """
        :return:
        """
        url = self._parse_url()
        con_param = {'wait': True}
        if self.credentials:
            credentials_list = self.credentials.split(':')
            con_param['username'] = credentials_list[0]
            con_param['passcode'] = credentials_list[1] if len(credentials_list) > 1 else ''
        self.client = stomp.Connection(url)
        self.client.connect(**con_param)

    def get_client(self):
        return self.client

    def close_client(self):
        self.client.disconnect()

    def _parse_url(self) -> list:
        """
        分析url，构造连接stomp的url
        url
        :return: [('localhost', 61613),('localhost', 61613)]
        """
        result = []
        if ',' in self.url:
            # 说明是多个
            for url_port in self.url.split(','):
                url_list = url_port.split(':')
                port = int(url_list[1]) if len(url_list) > 1 else 61613
                result.append((str(url_list[0]), port))
        else:
            url_list = self.url.split(':')
            port = int(url_list[1]) if len(url_list) > 1 else 61613
            result.append((str(url_list[0]), port))
        return result
