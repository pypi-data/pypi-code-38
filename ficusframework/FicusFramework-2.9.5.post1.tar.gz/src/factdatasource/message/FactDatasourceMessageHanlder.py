#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
import json
import logging
import threading
import time

from confluent_kafka.cimpl import KafkaError, KafkaException
from munch import Munch

from api.model.FactDatasource import FactDatasource, FactDatasourceTypeEnum
from factdatasource.FactDatasourceContextHolder import FactDatasourceContextHolder
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from factdatasource.dao.kafka.MultipleKafkaDatasource import CustomKafkaClient
from libs.utils import Singleton

log = logging.getLogger('Ficus')


def wait_using_fd(fd_context_holder: FactDatasourceContextHolder, action: int, fact_datasource: FactDatasource):
    def listen_using_fd():
        fd_code = fact_datasource.code
        if fd_context_holder.is_using_fact_datasource(fd_code):
            while fd_context_holder.is_using_fact_datasource(fd_code):
                log.debug(f'监听到数据源{fd_code}的{action}事件，等待数据源使用完毕')
                time.sleep(0.5)

        if action == FactDatasourceChangeListener.ACTION_UPDATE:
            fd_context_holder.update_fact_datasource(fact_datasource)
        elif action == FactDatasourceChangeListener.ACTION_DELETE:
            fd_context_holder.remove_fact_datasource(fact_datasource)

    thread = threading.Thread(name='wait_using_fd', target=listen_using_fd, daemon=True)
    thread.start()


class FactDatasourceChangeListener(threading.Thread, Singleton):
    """
    监听数据源消息
    """
    ACTION_ADD = 0
    ACTION_UPDATE = 1
    ACTION_DELETE = 2

    FACT_DATASOURCE_CHANGE_TOPIC = 'springCloudBus'

    def __init__(self):
        threading.Thread.__init__(self)

        client: CustomKafkaClient = get_multiple_datesource(FactDatasourceTypeEnum.KAFKA).get_client()
        self.producer = client.producer
        self.consumer = client.consumer
        self.running = False
        # 守护线程运行
        self.daemon = True

    @property
    def fd_context_holder(self):
        return FactDatasourceContextHolder.instance()

    def run(self):
        if self.running:
            log.warning(f'FD监听线程已启动无需重复启动')
            return
        self.running = True

        # 这里关心已使用过的FD的修改和删除消息，添加应该不需要关心
        # 这里监听到消息有两件事， 1. fd_context的事件处理  2. 多数据源的事件处理
        # 3.修改和删除需要判断该数据源是否正在使用，如果正在使用需要等待使用完成后在进行修改
        self.consumer.subscribe([self.FACT_DATASOURCE_CHANGE_TOPIC])

        while self.running:
            try:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        # Error
                        raise KafkaException(msg.error())
                else:
                    # 进行消息的处理
                    message = Munch(json.loads(msg.value()))
                    # 只处理FactDatasourceChangeEvent事件
                    if message.type == 'FactDatasourceChangeEvent':
                        self.deal_message(message)
            except Exception as e:
                log.exception(f"监听FactDatasourceChange消息出现问题,", e)
            finally:
                if self.running == False:
                    # 把消息队列关闭掉
                    self.consumer.close()

    def stop(self):
        self.running = False

    def deal_message(self, change_event):
        action = change_event.action
        fact_datasource = FactDatasource(**change_event.factDatasource)
        fd_code = fact_datasource.code

        if action == self.ACTION_ADD:
            # 不关心添加数据源事件
            return

        if self.fd_context_holder.is_loaded_fact_datasource(fd_code):
            # 本地数据源还没有使用不进行处理
            return

        if self.fd_context_holder.is_using_fact_datasource(fd_code):
            wait_num = 0
            while self.fd_context_holder.is_using_fact_datasource(fd_code):
                log.debug(f'监听到数据源{fd_code}的{action}事件，等待数据源使用完毕')
                wait_num += 1
                time.sleep(0.5)
                # 5秒都还在使用的话就只能使用新线程来处理了,否则无法处理后续的事件
                if wait_num > 10:
                    wait_using_fd(self.fd_context_holder, action, fact_datasource)
                    return

        if action == self.ACTION_UPDATE:
            self.fd_context_holder.update_fact_datasource(fact_datasource)
        elif action == self.ACTION_DELETE:
            self.fd_context_holder.remove_fact_datasource(fact_datasource)
