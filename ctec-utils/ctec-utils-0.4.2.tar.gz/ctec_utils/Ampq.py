# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import traceback

import json
import pika


class AsyncPublish:
    """
    未测试异步发送队列
    """

    def __init__(self, host: str, port: int, user: str, password: str, vhost: str, log=None):
        credentials = pika.PlainCredentials(user, password)
        self.parameters = pika.ConnectionParameters(host, port, vhost,
                                                    credentials)
        self.connection = None
        self.channel = None
        self.exchange = None
        self.data = ""
        self.routing_key = ""
        self.log = log

    def get_connection(self):
        return pika.SelectConnection(parameters=self.parameters,
                                     on_open_callback=self.on_open)

    def on_open(self, connection):
        connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.routing_key,
                                   body=self.data,
                                   properties=pika.BasicProperties(content_type='text/plain',
                                                                   delivery_mode=1))
        self.connection.close()

    def stop(self):
        try:
            self.channel.close()
            self.connection.close()
        except Exception as e:
            return e

    def send(self, data, exchange: str, routing_key="", flag=3) -> bool:
        if flag > 0:
            try:
                self.data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
                self.exchange = exchange
                self.routing_key = routing_key
                self.connection = self.get_connection()
                self.connection.ioloop.start()
                if self.log:
                    self.log.debug("exchange={}, routing_key={}, data={} 发送成功".format(exchange, routing_key, data))
            except KeyboardInterrupt:
                self.stop()
                if (self.connection is not None and
                        not self.connection.is_closed):
                    # Finish closing
                    self.connection.ioloop.start()
                flag -= 1
                self.stop()
                self.connection = self.get_connection()
                self.send(data, exchange, routing_key)
                return False
            return True
        else:
            if self.log:
                self.log.debug("发送exchange={}, routing_key={}失败,数据：{}".format(exchange, routing_key, data))
            return False


class Publish:
    """
    同步rabbitmq队列
    """

    def __init__(self, host: str, port: int, user: str, password: str, vhost: str, heartbeat: int = 60,
                 log=None, flag=3):
        self.params = {"host": host, "port": port, "user": user,
                       "password": password, "vhost": vhost, "heartbeat": heartbeat}
        self.log = log
        if flag > 0:
            try:
                self.connection = self.get_connection()
                self.channel = self.connection.channel()
            except Exception as e:
                if self.log:
                    self.log.error("创建队列对象失败-->%s" % e.args)
                flag -= 1
                self.__init__(host=host, port=port, user=user, password=password, vhost=vhost, log=log, flag=flag)
        else:
            if self.log:
                self.log.debug("创建对象失败3次")

    def get_connection(self):
        credentials = pika.PlainCredentials(self.params["user"], self.params["password"])
        parameters = pika.ConnectionParameters(self.params["host"], self.params["port"], self.params["vhost"],
                                               credentials, heartbeat=self.params["heartbeat"])
        return pika.BlockingConnection(parameters=parameters)

    def stop(self):
        try:
            self.channel.close()
            self.connection.close()
        except Exception as e:
            return e

    def send(self, data, exchange: str, routing_key="", flag=3) -> bool:
        data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
        if flag > 0:
            try:
                self.channel.basic_publish(exchange=exchange,
                                           routing_key=routing_key,
                                           body=data,
                                           properties=pika.spec.BasicProperties(delivery_mode=2))
                if self.log:
                    self.log.debug("发送exchange={},routing_key={}成功,数据：{}".format(exchange, routing_key, data))
            except Exception as e:
                if self.log:
                    self.log.error("发送exchange={},routing_key={}异常,数据：{}".format(exchange, routing_key,
                                                                                 traceback.format_exc()))
                flag -= 1
                self.__init__(host=self.params["host"], port=self.params["port"], log=self.log,
                              password=self.params["password"], user=self.params["user"], vhost=self.params["vhost"])
                return self.send(data, exchange, routing_key)
            return True
        else:
            if self.log:
                self.log.error("发送exchange={}, routing_key={}失败,数据：{}".format(exchange, routing_key, data))
            return False

    def __del__(self):
        self.stop()
