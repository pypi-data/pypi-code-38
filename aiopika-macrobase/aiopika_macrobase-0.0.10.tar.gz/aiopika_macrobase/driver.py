import asyncio
from typing import List, Dict, Type

from macrobase_driver.driver import MacrobaseDriver
from macrobase_driver.hook import HookHandler

from .config import AiopikaDriverConfig
from .hook import AiopikaHookNames
from .result import AiopikaResult, AiopikaResultAction
from .method import Method
from .router import Router, HeaderMethodRouter
from .serializers import deserialize
from .exceptions import AiopikaException, DeserializeFailedException, ContentTypeNotSupportedException,\
    ResultDeliveryFailedException

import uvloop
from aio_pika import connect_robust, Connection, IncomingMessage, Channel, Queue

from structlog import get_logger
log = get_logger('AiopikaDriver')


class AiopikaDriver(MacrobaseDriver):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.name is None:
            self.name = 'Aiopika Driver'

        self._connection = None
        self._channel: Channel = None
        self._queue: Queue = None

        self.config = AiopikaDriverConfig()
        self._hooks: Dict[AiopikaHookNames, List[HookHandler]] = {}
        self._methods: Dict[str, Method] = {}

        self._router: Router = None
        self.router_cls: Type[Router] = HeaderMethodRouter

    def update_config(self, config: AiopikaDriverConfig):
        """
        Update driver config

        Args:
            config (AiopikaDriverConfig): Driver config object

        Returns:
            None
        """
        self.config.update(config)

    def add_hook(self, name: AiopikaHookNames, handler):
        if name not in self._hooks:
            self._hooks[name] = []

        self._hooks[name].append(HookHandler(self, handler))

    def add_method(self, method: Method):
        self._methods[method.identifier] = method

    def add_methods(self, methods: List[Method]):
        self._methods.update({method.identifier: method for method in methods})

    async def process_message(self, message: IncomingMessage, *args, **kwargs):
        async with message.process(ignore_processed=self.config.IGNORE_PROCESSED):
            log.info(f'Message <IncomingMessage correlation_id: {message.correlation_id}> received')

            await self._process_message(message)

    async def _process_message(self, message: IncomingMessage):
        try:
            result = await self._get_method_result(message, self._router.route(message))
        except Exception as e:
            requeue = e.requeue if isinstance(e, AiopikaException) else self.config.REQUEUE_IF_FAILED

            log.error(e)
            result = AiopikaResult(action=AiopikaResultAction.nack, requeue=requeue)
            await self._process_result(message, result, ignore_reply=True)
            return

        await self._process_result(message, result, ignore_reply=False)

    async def _get_method_result(self, message: IncomingMessage, method: Method):
        data = message.body

        try:
            if message.content_type is not None and len(message.content_type) != 0:
                data = deserialize(message.body, message.content_type)
        except ContentTypeNotSupportedException as e:
            pass

        return await method.handler(self, message, data=data, identifier=method.identifier)

    async def _process_result(self, message: IncomingMessage, result: AiopikaResult, ignore_reply: bool = False):
        if result.requeue:
            await asyncio.sleep(self.config.REQUEUE_DELAY)

        if result.action == AiopikaResultAction.ack:
            await message.ack(multiple=result.multiple)
        elif result.action == AiopikaResultAction.nack:
            await message.nack(multiple=result.multiple, requeue=result.requeue)
        elif result.action == AiopikaResultAction.reject:
            await message.reject(requeue=result.requeue)

        if ignore_reply:
            return

        if message.reply_to is not None and len(message.reply_to) != 0:
            try:
                result_message = result.get_response_message()

                await self._channel.default_exchange.publish(
                    result_message,
                    routing_key=message.reply_to
                )
            except Exception as e:
                raise ResultDeliveryFailedException

    async def _serve(self, loop) -> Connection:
        user            = self.config.RABBITMQ_USER
        password        = self.config.RABBITMQ_PASS
        host            = self.config.RABBITMQ_HOST
        port            = self.config.RABBITMQ_PORT
        virtual_host    = self.config.RABBITMQ_VHOST
        queue           = self.config.QUEUE_NAME

        self._connection = await connect_robust(
            host=host,
            port=port,
            login=user,
            password=password,
            virtualhost=virtual_host,

            loop=loop
        )

        self._channel = await self._connection.channel()
        self._queue = await self._channel.declare_queue(queue, durable=self.config.QUEUE_DURABLE, auto_delete=self.config.QUEUE_AUTO_DELETE)

        await self._queue.consume(self.process_message)

        return self._connection

    async def _prepare(self):
        log.debug(f'Router <{self.router_cls.__name__}> initialize')
        self._router = self.router_cls(self._methods)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

        uvloop.install()

        self.loop.run_until_complete(self._prepare())
        self.loop.run_until_complete(self._call_hooks(AiopikaHookNames.before_server_start))

        connection: Connection = None

        try:
            connection = self.loop.run_until_complete(self._serve(self.loop))
            self.loop.run_forever()
        except Exception as e:
            if connection is not None:
                self.loop.run_until_complete(connection.close())
        finally:
            self.loop.run_until_complete(self._call_hooks(AiopikaHookNames.after_server_stop))
            self.loop.close()
