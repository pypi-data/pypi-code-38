import asyncio
import json
import logging

import aioamqp

from .app import Component


class AMQPServer(Component):
    CONNECTION_DELAY = 1

    def __init__(self, app, config, handler):
        super(AMQPServer, self).__init__()
        self.app = app
        self.loop = app.loop
        self.config = {
            'host': config.get('host', 'localhost'),
            'port': config.get('port', ),
            'virtualhost': config.get('virtualhost', '/'),
            'login': config.get('login', 'guest'),
            'password': config.get('password', 'guest'),
            'durable': config.get('durable', True),
        }
        self.exchange_name = config.get('exchange_name', 'mocker')
        self.exchange_type = config.get('exchange_type', 'topic')
        self.exchange_durable = config.get('exchange_durable', True)
        self.transport = None
        self.protocol = None
        self.channel = None
        self.consumer = handler(self)
        self.consumers_list = []
        self.started = []

    async def prepare(self):
        self.app.log_info("Preparing to start AMQP server...")
        self.consumers_list = self.consumer.routes

    async def start(self):
        while True:
            try:
                await self.connect()
                await self.channel.exchange_declare(
                    exchange_name=self.exchange_name,
                    type_name=self.exchange_type,
                    durable=self.exchange_durable,
                )
                for route in self.consumers_list:
                    # name, queue_name, func
                    await self.channel.queue_declare(
                        queue_name=route['queue_name'],
                        #durable=self.config['durable'],
                    )
                    await self.channel.queue_bind(          # TODO: timeout
                        exchange_name=self.exchange_name,
                        queue_name=route['queue_name'],
                        routing_key=route['routing_key']
                    )
                    await self.channel.basic_consume(       # TODO: get tag
                        route['handler'],
                        queue_name=route['queue_name']
                    )
                    self.app.log_info("Start consumer '%s'." % route['route_name'])
            except Exception as e:
                await asyncio.sleep(5)
                self.app.log_err('AMQP connect error: %s %s' % (self.__class__.__name__, str(e)))
                self.app.log_err('DSN: %s' % json.dumps(self.config))
                self.app.log_err('Trying to reconnect to rabbit...')
            else:
                break

    async def stop(self):
        # TODO: сделать через basic_cancel и тег
        # await self.channel.stop_consuming()
        await self.disconnect()
        self.app.log_info("Stop AMQP server.")

    # async def heartbeat(self, protocol):
    #     while True:
    #         await asyncio.sleep(30)  # issue manual heartbeat every 20 seconds
    #         await protocol.send_heartbeat()

    async def connect(self):
        try:
            self.transport, self.protocol = await aioamqp.connect(
                **self.config,
                loop=self.loop,
                on_error=self.error_callback,
                heartbeat=30
            )
            self.channel = await self.protocol.channel()
            # asyncio.ensure_future(self.heartbeat(self.protocol))
        except aioamqp.AmqpClosedConnection as e:
            self.app.log_info('[x] Connection error %s' % str(e))
            await asyncio.sleep(self.CONNECTION_DELAY)
            await self.connect()

    async def disconnect(self):
        if self.transport and self.protocol:
            await self.protocol.close()
            self.transport.close()

    async def error_callback(self, error):
        if isinstance(error, aioamqp.AmqpClosedConnection):
            await asyncio.sleep(self.CONNECTION_DELAY)
            self.app.log_info("Restarting AMQP server.")
            await self.start()
