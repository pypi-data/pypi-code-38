#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from confluent_kafka.cimpl import Producer, Consumer

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from config.annotation import Value
from factdatasource.dao.FactDatasource import DatasourceListener, MultipleBaseDatasource, BaseDatasource, \
    customer_dao_context_holder
from factdatasource.execptions import DatasourceNotFoundException, FDExecuteException
from libs.utils import Singleton


class CustomKafkaClient(object):

    def __init__(self, producer: Producer = None, consumer: Consumer = None):
        if not producer and not consumer:
            raise IllegalArgumentException('参数不能同时为空')
        self._producer_ = producer
        self._consumer_ = consumer

    @property
    def producer(self) -> Producer:
        return self._producer_

    @property
    def consumer(self) -> Consumer:
        return self._consumer_


class MultipleKafkaDatasource(DatasourceListener, MultipleBaseDatasource, Singleton):
    """
    管理fd中的所有KAFKA类型的数据源
    """

    DEFAULT_KAFKA_DATASOURCE = '_ficus4py_default_kafka_datasource'

    def __init__(self):
        # source_name --> KafkaDatasource
        self._target_dataSources = dict()

    def get_datasource_type(self):
        """
        获取数据源类型
        :return:
        """
        return FactDatasourceTypeEnum.KAFKA

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
        # 由于每个kafka的fd中group.id都不一样，所以kafka数据源不能多个fd共享
        # 开始创建数据源
        kafka_data_source = KafkaDatasource(source_name, url, credentials)
        kafka_data_source.start()
        self._target_dataSources[source_name] = kafka_data_source

    def update_datasource_type(self, source_name: str, url: str, credentials: str):
        """
        修改一个数据源
        :param source_name:
        :param url:
        :param credentials:
        :return:
        """
        if not source_name:
            raise IllegalArgumentException(f'修改数据源参数错误:source_name不能为空')

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

        target: KafkaDatasource = self._target_dataSources.pop(source_name)
        if target:
            target.close_client()

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

    def determine_current_lookup_key(self):
        """KAFKA中需要设置默认的数据源，所以这里需要重写该方法"""
        source_name = customer_dao_context_holder.get_source()
        if source_name is None:
            return self.DEFAULT_KAFKA_DATASOURCE
        return source_name

    def get_client(self):
        """
        获取数据库操作的client
        :return:
        """
        target: KafkaDatasource = self.get_data_source()
        return target.get_client()

    def close_client(self):
        """
        关闭客户端，关闭连接
        :return:
        """
        target: KafkaDatasource = self.get_data_source()
        return target.close_client()


class KafkaDatasource(BaseDatasource):

    def __init__(self, source_name, url, credentials):
        self.init(source_name, url, credentials)
        self._group_id = source_name
        self.client: CustomKafkaClient = None

    def start(self):
        """
        TODO kafka还没有支持密码验证
        :return:
        """
        producer_conf = {
            'bootstrap.servers': self.url
        }
        producer = Producer(producer_conf)

        consumer_conf = {
            'bootstrap.servers': self.url,
            'group.id': self._group_id
        }
        consumer = Consumer(consumer_conf)

        self.client = CustomKafkaClient(producer, consumer)

    def get_client(self) -> CustomKafkaClient:
        return self.client

    def close_client(self):
        if self.client and self.client.consumer:
            self.client.consumer.close()


@Value("${kafka.ip}")
def kafka_ip():
    pass


@Value("${kafka.timeout}")
def kafka_timeout():
    pass


def register_kafka_default_datasource():
    """
    注册默认的数据源
    :return:
    """
    datasource = MultipleKafkaDatasource.instance()
    url = kafka_ip()
    datasource.add_datasource_type(datasource.DEFAULT_KAFKA_DATASOURCE, url, None)







