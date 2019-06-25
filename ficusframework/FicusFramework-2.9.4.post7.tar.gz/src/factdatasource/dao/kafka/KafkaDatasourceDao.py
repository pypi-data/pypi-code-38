#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/2/21
from confluent_kafka.cimpl import Consumer, Producer

from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from factdatasource.dao.kafka.MultipleKafkaDatasource import CustomKafkaClient
from libs.utils import Singleton


class KafkaDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.KAFKA)
        return data_source

    @property
    def client(self) -> CustomKafkaClient:
        return self.datasource.get_client()

    @property
    def producer(self) -> Producer:
        return self.client.producer

    @property
    def consumer(self) -> Consumer:
        return self.client.consumer


