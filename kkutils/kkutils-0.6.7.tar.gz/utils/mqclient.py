#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-09-29 00:59:38
'''
import asyncio
import os
import pickle

import aio_pika
from aio_pika import Message
from utils import Logger


class MQClient:

    def __init__(self, queue='test', workers=10, **kwargs):
        if any([key in kwargs for key in ['host', 'port', 'user', 'pwd']]):
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 5672)
            user = kwargs.pop('user', 'guest')
            pwd = kwargs.pop('pwd', 'guest')
            self.uri = f'amqp://{user}:{pwd}@{host}:{port}'
        elif 'uri' in kwargs:
            self.uri = kwargs.pop('uri')
        elif 'MQ_URI' in os.environ:
            self.uri = os.environ.get('MQ_URI', 'amqp://guest:guest@localhost:5672')
        else:
            host = os.environ.get('MQ_HOST', 'localhost')
            port = os.environ.get('MQ_PORT', 5672)
            user = os.environ.get('MQ_USER', 'guest')
            pwd = os.environ.get('MQ_PWD', 'guest')
            self.uri = f'amqp://{user}:{pwd}@{host}:{port}'

        self.logger = Logger()
        self.queue_name = queue
        self.routing_key = queue
        self.workers = workers
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.uri, loop=self.loop)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, auto_delete=False)
        await self.channel.set_qos(prefetch_count=self.workers)
        self.logger.info(f'rabbitmq server connected: {repr(self.channel)}, queue: {self.queue_name}')

    async def _consumer(self, process):
        async for msg in self.queue:
            try:
                await process(pickle.loads(msg.body))
            except Exception as e:
                self.logger.exception(e)
            finally:
                await msg.ack()

    async def consume(self, process):
        for _ in range(self.workers):
            self.loop.create_task(self._consumer(process))

    async def publish(self, msg):
        await self.channel.default_exchange.publish(Message(pickle.dumps(msg)),
                                                    routing_key=self.routing_key)

    async def shutdown(self):
        await self.channel.close()
        await self.connection.close()
