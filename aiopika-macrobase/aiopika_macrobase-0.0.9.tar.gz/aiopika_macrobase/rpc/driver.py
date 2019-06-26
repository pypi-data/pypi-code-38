from ..driver import AiopikaDriver, IncomingMessage
from ..router import HeaderMethodRouter, IncomingRoutingFailedException, EndpointNotImplementedException
from .request import RPCResponse, RPCMessageType

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
