#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/23
import json

from pika import BlockingConnection

from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from libs.utils import Singleton, JSONEncoder


class AmqpDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.AMQP)
        return data_source

    @property
    def client(self) -> BlockingConnection:
        return self.datasource.get_client()

    def basic_publish_topic(self, exchange: str, routing_key: str, message):
        """
        发送topic消息
        :param exchange:
        :param routing_key:
        :param message:可以一次发送多个消息，多个消息共享一个channel
        :type message: str or list
        :return:
        """
        with self.client.channel() as channel:
            channel.exchange_declare(exchange=exchange, exchange_type='topic')
            if isinstance(message, list):
                for mess in message:
                    if not isinstance(mess, str):
                        mess = json.dumps(mess, cls=JSONEncoder)
                        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=mess)
                    else:
                        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=mess)
            else:
                if not isinstance(message, str):
                    message = json.dumps(message, cls=JSONEncoder)
                channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
