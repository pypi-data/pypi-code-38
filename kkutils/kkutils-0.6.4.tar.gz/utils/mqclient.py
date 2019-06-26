#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-09-29 00:59:38
'''
import asyncio
import json
import os

import aio_pika
from aio_pika import Message
from utils import JSONEncoder
from utils import Logger
from utils import to_bytes


class MQClient:

    def __init__(self, queue='test', prefetch=10, **kwargs):
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

        self.queue_name = queue
        self.routing_key = queue
        self.prefetch = prefetch
        self.loop = asyncio.get_event_loop()
        self.logger = Logger()
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.uri, loop=self.loop)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, auto_delete=False)
        await self.channel.set_qos(prefetch_count=self.prefetch)
        self.logger.info(f'rabbitmq server connected: {repr(self.channel)}, queue: {self.queue_name}')

    async def consume(self, process):
        # await self.queue.consume(process)
        async for message in self.queue:
            await process(message)
            await message.ack()

    async def publish(self, doc):
        msg = json.dumps(doc, cls=JSONEncoder).encode() if isinstance(doc, dict) else to_bytes(doc)
        await self.channel.default_exchange.publish(Message(msg), routing_key=self.routing_key)

    async def shutdown(self):
        await self.channel.close()
        await self.connection.close()
