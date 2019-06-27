from .request import RPCResponse, RPCMessageType
from .exceptions import ResponseContentException

from ..driver import AiopikaDriver, IncomingMessage
from ..router import HeaderMethodRouter, IncomingRoutingFailedException, EndpointNotImplementedException
from ..result import AiopikaResult, AiopikaResultAction
from ..exceptions import PayloadTypeNotSupportedException, SerializeFailedException, ResultDeliveryFailedException

from structlog import get_logger
log = get_logger('AiopikaDriver')


class AiopikaRPCDriver(AiopikaDriver):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = 'Aiopika RPC Driver'
        self.router_cls = HeaderMethodRouter

    async def _process_message(self, message: IncomingMessage):
        method = None

        try:
            method = self._router.route(message)
            result = await self._get_method_result(message, method)
        except Exception as e:
            log.error(e)
            result = RPCResponse(payload=e, type=RPCMessageType.error).get_result(message.correlation_id, method.identifier if method is not None else '', message.expiration)

        await self._process_result(message, result, ignore_reply=False)

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
                try:
                    result_message = result.get_response_message()
                except (PayloadTypeNotSupportedException, SerializeFailedException) as e:
                    result_message = result.get_response_message(
                        payload=ResponseContentException(),
                        type=RPCMessageType.error.value
                    )

                await self._channel.default_exchange.publish(
                    result_message,
                    routing_key=message.reply_to
                )
            except Exception as e:
                raise ResultDeliveryFailedException
