#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.database import Database

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import DatasourceListener, MultipleBaseDatasource, BaseDatasource
from factdatasource.execptions import DatasourceNotFoundException, FDExecuteException
from libs.utils import Singleton


class MultipleMongoDatasource(DatasourceListener, MultipleBaseDatasource, Singleton):
    """
    管理fd中的所有MONGO类型的数据源
    """

    def __init__(self):
        # source_name --> MongoDatasource
        self._target_dataSources = dict()

    def get_datasource_type(self):
        """
        获取数据源类型
        :return:
        """
        return FactDatasourceTypeEnum.MONGO

    def add_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        添加一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """
        if not source_name or not url:
            raise IllegalArgumentException(f'修改数据源参数错误:source_name、url都不能为空')

        for target in self._target_dataSources.values():
            if target.url == url and target.credentials == credentials:
                # url 和 credentials 都相同，说明是同一个数据库连接就不再重复创建数据源了
                target.add_source_name(source_name)
                self._target_dataSources[source_name] = target
                return None

        # 开始创建数据源
        mongo_data_source = MongoDatasource(source_name, url, credentials)
        mongo_data_source.start()
        self._target_dataSources[source_name] = mongo_data_source

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

        target: MongoDatasource = self._target_dataSources.pop(source_name)
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
        raise DatasourceNotFoundException('未发现数据源%s,请添加后再获取。' % source_name)

    def get_client(self):
        """
        获取数据库操作的client
        :return:
        """
        target: MongoDatasource = self.get_data_source()
        return target.get_client()

    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """
        target: MongoDatasource = self.get_data_source()
        return target.close_client()


class MongoDatasource(BaseDatasource):

    def __init__(self, source_name, url, credentials):
        self.init(source_name, url, credentials)
        # 使用的库
        self.db = None
        # 连接mongo的uri
        self.uri = None
        self.client: MongoClient = None

    def start(self):
        """
        :return:
        """
        self._parse_url()
        self.client = MongoClient(host=self.uri, maxPoolSize=20, connect=False)

    def get_client(self) -> Database:
        return self.client[self.db]

    def close_client(self):
        if self.client:
            self.client.close()

    def _parse_url(self):
        """
        分析url，构造连接mongo的uri
        :return:
        """
        if self.credentials:
            if '@' in self.credentials:
                con_credential = self.credentials[0:self.credentials.find('@')]
                user_db = self.credentials[self.credentials.find('@')+1:]
            else:
                con_credential = self.credentials
                user_db = "admin"
        else:
            con_credential = ''
            user_db = "admin"

        if con_credential and ':' in con_credential:
            uri_credential = quote_plus(con_credential[0:con_credential.find(':')]) + ':' \
                             + quote_plus(con_credential[con_credential.find(':')+1:]) + '@'
        else:
            uri_credential = ''

        if not self.url or '@' not in self.url:
            raise IllegalArgumentException(f'mongo连接信息配置错误，无法进行连接：{self.url}')

        con_url = self.url[0:self.url.find('@')]
        db = self.url[self.url.find('@')+1:]
        if not db:
            raise IllegalArgumentException(f'mongo连接信息未配置使用库，无法进行连接：{self.url}')

        # mongodb://sdba:sdba@localhost:27017,localhost:27018/admin
        _uri = f'mongodb://{uri_credential}{con_url}/{user_db}'

        self.db = db
        self.uri = _uri
        return _uri
