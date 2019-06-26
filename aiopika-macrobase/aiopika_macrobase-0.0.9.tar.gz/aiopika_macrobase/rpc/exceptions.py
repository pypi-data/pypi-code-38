from ..exceptions import AiopikaException

from aio_pika.message import DeliveredMessage


class AiopikaRPCException(AiopikaException):
    requeue = None


class PublishMessageException(AiopikaRPCException):

    def __init__(self, queue: str, task: str, correlation_id: str):
        super(PublishMessageException, self).__init__(f'<Queue: {queue} task: {task} correlation_id: {correlation_id}> Publish task error')


class DeliveryException(AiopikaRPCException):

    def __init__(self, message: DeliveredMessage):
        super(DeliveryException, self).__init__(f'<Exchange: {message.delivery.exchange} routing_key: {message.delivery.routing_key} code: {message.delivery.reply_code}> {message.delivery.reply_text}')


class MessageTimeoutException(AiopikaRPCException):

    def __init__(self, queue: str, task: str, correlation_id: str):
        super(MessageTimeoutException, self).__init__(f'<Queue: {queue} task: {task} correlation_id: {correlation_id}> Service is unavailable')


class ExternalException(AiopikaRPCException):
    """
    Exception against rpc-fragile
    """

    def __init__(self, exception: Exception):
        super(ExternalException, self).__init__(str(exception))
