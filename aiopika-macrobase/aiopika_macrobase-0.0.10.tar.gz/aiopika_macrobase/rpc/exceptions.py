from ..exceptions import AiopikaException

from aio_pika.message import DeliveredMessage


class AiopikaRPCException(AiopikaException):
    requeue = None


class PublishMessageException(AiopikaRPCException):

    def __init__(self, queue: str, task: str, correlation_id: str):
        super(PublishMessageException, self).__init__(f'<Queue: {queue} task: {task} correlation_id: {correlation_id}> Publish task error')


class DeliveryException(AiopikaRPCException):

    def __init__(self, message: DeliveredMessage):
        self.exchange = message.delivery.exchange
        self.routing_key = message.delivery.routing_key
        self.reply_code = message.delivery.reply_code
        self.reply_text = message.delivery.reply_text

        super(DeliveryException, self).__init__(
            f'<Exchange: {self.exchange} routing_key: {self.routing_key} code: {self.reply_code}> {self.reply_text}'
        )


class ReceiveMessageException(AiopikaRPCException):

    def __init__(self, correlation_id: str, routing_key: str, type: str):
        super(ReceiveMessageException, self).__init__(f'<Message: {correlation_id} routing_key: {routing_key} type: {type}> Message fail receive')


class MessageTimeoutException(AiopikaRPCException):

    def __init__(self, queue: str, task: str, correlation_id: str):
        super(MessageTimeoutException, self).__init__(f'<Queue: {queue} task: {task} correlation_id: {correlation_id}> Service is unavailable')


class ExternalException(AiopikaRPCException):
    """
    Exception against rpc-fragile
    """

    def __init__(self, exception: Exception):
        super(ExternalException, self).__init__(str(exception))


class ResponseContentException(AiopikaRPCException):
    pass
    # def __init__(self, correlation_id: str, routing_key: str):
    #     super(ResponseContentException, self).__init__(f'<Message: {correlation_id} routing_key: {routing_key}> Message response not serialized')
