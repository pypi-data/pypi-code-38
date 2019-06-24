#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from elasticsearch import Elasticsearch

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.execptions import DatasourceNotFoundException, FDExecuteException
from factdatasource.dao.FactDatasource import DatasourceListener, MultipleBaseDatasource, BaseDatasource
from libs.utils import Singleton


class MultipleEsDatasource(DatasourceListener, MultipleBaseDatasource, Singleton):
    """
    管理fd中的所有ES类型的数据源
    """

    def __init__(self):
        # source_name --> EsDatasource
        self._target_dataSources = dict()

    def get_datasource_type(self):
        """
        获取数据源类型
        :return:
        """
        return FactDatasourceTypeEnum.ES

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
        es_data_source = EsDatasource(source_name, url, credentials)
        es_data_source.start()
        self._target_dataSources[source_name] = es_data_source

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
        if not source_name:
            raise IllegalArgumentException(f'删除数据源参数错误:source_name不能为空')

        target: EsDatasource = self._target_dataSources.pop(source_name)
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
        target: EsDatasource = self.get_data_source()
        return target.get_client()

    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """
        target: EsDatasource = self.get_data_source()
        return target.close_client()


class EsDatasource(BaseDatasource):

    def __init__(self, source_name, url, credentials):
        self.init(source_name, url, credentials)
        self.client: Elasticsearch = None

    def start(self):
        """
        :return:
        """
        hosts = self._parse_url()
        self.client = Elasticsearch(hosts=hosts)

    def get_client(self):
        return self.client

    def close_client(self):
        # 暂时不需要做什么
        pass

    def _parse_url(self) -> list:
        """
        分析url，构造连接es的url
        :return:
        """
        if ',' in self.url:
            # 说明是多个
            result = str(self.url).split(',')
        else:
            result = [self.url]
        return result
