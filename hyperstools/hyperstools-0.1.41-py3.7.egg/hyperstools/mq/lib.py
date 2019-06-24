# encoding: utf-8
import json
import logging
import pickle
import urllib
from traceback import format_exc

import django
import pika
from django.conf import settings

from .consumer import Consumer
from .publisher import Publisher
from hyperstools import compat

LOGGER = logging.getLogger("tools")
defaultMq = compat.defaultMq


class Queue(object):
    def __init__(self, identify: dict, logger=None, **kwargs):
        """初始化rabbitmq的认证信息
        如果identify不存在host、port等key时，则从settings.RABBITMQ中取默认值

        :identify: dict: 认证信息， 如 {'user': 'xxx', 'password': 'xxx', 'queue': 'xxx'}
        :returns: None

        """
        host = identify.get("host", defaultMq["host"])
        port = identify.get("port", defaultMq["port"])
        user = identify.get("user", defaultMq["user"])
        password = identify.get("password", defaultMq["password"])
        vhost = identify.get("vhost", defaultMq["vhost"])
        exchange = identify.get("exchange", identify["queue"])
        routing_key = identify.get("routing_key", identify["queue"])
        exchange_type = identify.get("exchange_type", "direct")
        heartbeat = identify.get('heartbeat', 30 * 60)
        vhost = urllib.parse.quote_plus(vhost)

        self._logger = logger or LOGGER

        url = f"amqp://{user}:{password}@{host}:{port}/{vhost}?heartbeat={heartbeat}"
        self._identify = {
            "url": url,
            "exchange": exchange,
            "routing_key": routing_key,
            'queue': identify['queue'],
            "exchange_type": exchange_type,
        }
        self._kwargs = kwargs

    def publish(self, message: dict, encoder: str = "json"):
        """发布消息的处理函数
        用法
        with Queue(settings.RABBITMQ) as queue:
            queue.publish({'a': 'b'})

        :message: dict: 消息体
        :returns: None

        """
        if encoder == "pickle":
            body = pickle.dumps(message)
        else:
            body = json.dumps(message, ensure_ascii=False)
        messages = [body]
        pub = Publisher(self._identify, messages, logger=self._logger, **self._kwargs).run()

    def listen(self, callback):
        consumer = Consumer(self._identify, callback, logger=self._logger, **self._kwargs)
        consumer.run()

    def __call__(self, callback):
        """注册listen的回调函数
        在调用callback函数之前，会先尝试使用json.loads 解析消息
        然后尝试使用pickle.loads 解析消息，
        如果解析消息失败，则直接返回ack,
        解析成功后会调用
        close_old_connections, 再调用callback函数
        其中回调消息会经过异常处理

        用法

        @Queue(settings.RABBITMQ)
        def listen(body: dict):
            pass

        listen()

        :callback: 消费者的回调函数
        :returns: None

        """

        def inner():
            return self.listen(callback)

        return inner

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
