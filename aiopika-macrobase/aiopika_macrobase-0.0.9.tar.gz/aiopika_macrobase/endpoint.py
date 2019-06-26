from .result import AiopikaResult

from macrobase_driver.endpoint import Endpoint

from aio_pika import IncomingMessage

from structlog import get_logger
log = get_logger('AiopikaEndpoint')


class AiopikaEndpoint(Endpoint):
    """
    Endpoint class for process incoming messages and ack/nack/reject message
    """

    async def handle(self, driver, message: IncomingMessage, data, *args, **kwargs):
        """
        Handle method for process incoming message with identifier

        Args:
            driver: Aiopika Macrobase driver
            message (IncomingMessage): Incoming message from driver processing
            data: Deserialized payload from Incoming Message
            *args: Additional arguments
            **kwargs: Additional arguments with keys

        Returns:
            AiopikaResult: Aiopika result action or None  (if return None then driver ack message).
        """
        result = await self.method(driver, message, data, *args, **kwargs)

        return result if result is not None else AiopikaResult()

    async def method(self, driver, message: IncomingMessage, data, *args, **kwargs) -> AiopikaResult:
        return AiopikaResult()


class HealthEndpoint(AiopikaEndpoint):

    async def method(self, driver, message: IncomingMessage, data, *args, **kwargs):
        log.info('Health')
