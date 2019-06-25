#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from enum import Enum

from redis import StrictRedis

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.execptions import DatasourceNotFoundException, FDExecuteException
from factdatasource.dao.FactDatasource import DatasourceListener, MultipleBaseDatasource, BaseDatasource
from libs.utils import Singleton


class RedisTypeEnum(Enum):
    SINGLE = 'SINGLE '  # 单节点
    CLUSTER = 'CLUSTER'  # 集群
    SENTINEL = 'SENTINEL'  # 哨兵


class MultipleRedisDatasource(DatasourceListener, MultipleBaseDatasource, Singleton):
    """
    管理fd中的所有REDIS类型的数据源
    """

    def __init__(self):
        # source_name --> RedisDatasource
        self._target_dataSources = dict()

    def get_datasource_type(self):
        """
        获取数据源类型
        :return:
        """
        return FactDatasourceTypeEnum.REDIS

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
        redis_data_source = RedisDatasource(source_name, url, credentials)
        redis_data_source.start()
        self._target_dataSources[source_name] = redis_data_source

    def update_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        修改一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """
        if not source_name:
            raise IllegalArgumentException(f'删除数据源参数错误:source_name不能为空')

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

        target: RedisDatasource = self._target_dataSources.pop(source_name)
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
        target: RedisDatasource = self.get_data_source()
        return target.get_client()

    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """
        target: RedisDatasource = self.get_data_source()
        return target.close_client()


class RedisDatasource(BaseDatasource):

    def __init__(self, source_name, url, credentials):
        self.init(source_name, url, credentials)
        self.client: StrictRedis = None

    def start(self):
        """
        TODO 连接池暂时就用默认的连接池
        :return:
        """
        conn_url = self._parse_url()
        type = conn_url[0]

        kwargs = {
            "decode_responses": True
        }

        if type == RedisTypeEnum.CLUSTER:
            from rediscluster import StrictRedisCluster
            self.client = StrictRedisCluster(startup_nodes=conn_url[1], **kwargs)
        elif type == RedisTypeEnum.SENTINEL:
            from redis.sentinel import Sentinel
            sentinel = Sentinel(conn_url[2], **kwargs)
            self.client = sentinel.master_for(conn_url[1])
        else:
            self.client = StrictRedis.from_url(conn_url[1], **kwargs)

    def get_client(self):
        return self.client

    def close_client(self):
        if self.client:
            self.client.connection_pool.disconnect()

    def _parse_url(self):
        """
        根据配置将url转换为可以直接连接的url
        REIDS原始配置如下:
        单机：ip:port
        集群（英文逗号分割）： ip:port,ip:port,ip:port
        哨兵（第一个表示主节点名字，英文分号分割）：MASTERNAME;哨兵IP1:PORT1;哨兵IP2:PORT2;哨兵IP3:PORT3
        :return:
        """

        # 获取密码
        password = None
        if self.credentials:
            if ':' in self.credentials:
                password = str(self.credentials).split(':', 1)[1]
            else:
                password = self.credentials

        result = []

        if ',' in self.url:
            # 集群配置
            type = RedisTypeEnum.CLUSTER
            for url_split in str(self.url).split(','):
                url_tmp = {}
                if ':' in url_split:
                    url_tmp['host'] = url_split.split(':', 1)[0]
                    url_tmp['port'] = int(url_split.split(':', 1)[1])
                else:
                    url_tmp['host'] = url_split
                if password:
                    url_tmp['password'] = password

                result.append(url_tmp)
            return (type, result, )
        elif ';' in self.url:
            # 哨兵配置  [('localhost', 26379)]
            type = RedisTypeEnum.SENTINEL
            url_split = str(self.url).split(';')
            if len(url_split) < 2:
                raise IllegalArgumentException(f'redis连接信息配置错误，无法进行连接：{self.url}')
            # 第一个是主节点名字
            master_service = url_split[0]

            for host_port in url_split[1:]:
                if ':' in host_port:
                    result.append((host_port.split(':', 1)[0], host_port.split(':', 1)[1]))
                else:
                    result.append((host_port,))
            return (type, master_service, result, )
        else:
            # 普通单节点
            type = RedisTypeEnum.SINGLE
            #构造url:  redis://[:password]@localhost:6379/0
            password = ':'+str(password)+'@' if password else ''
            url = f'redis://{password}{self.url}'
            return (type, url)


