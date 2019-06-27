from enum import Enum, IntEnum

from .serializers import serialize, SerializeFailedException, PayloadTypeNotSupportedException

from aio_pika.message import Message, DateType, DeliveryMode

from structlog import get_logger
log = get_logger('AiopikaResult')


class AiopikaResultAction(IntEnum):
    nothing = 0
    ack = 10
    nack = 20
    reject = 30


class AiopikaResult(object):
    """
    Result class with data for action on IncomingMessage
    """

    def __init__(self, action: AiopikaResultAction = AiopikaResultAction.ack,
                 multiple: bool = False, requeue: bool = False,
                 payload=None, headers: dict = None,
                 content_type: str = None, content_encoding: str = None,
                 delivery_mode: DeliveryMode = None,
                 priority: int = None, correlation_id=None,
                 reply_to: str = None, expiration: DateType = None,
                 message_id: str = None,
                 timestamp: DateType = None,
                 type: str = None, user_id: str = None,
                 app_id: str = None):
        """
        Initialize AiopikaResult

        Args:
            action (AiopikaResultAction): Action for IncomingMessage
            multiple (bool): Multiple actio, only for ack/nack actions
            requeue (bool): Requeue flag, only for nack/reject actions

            payload: Payload data object or dict or any supported serialization types (show on serializers.py)
            headers (dict): Headers dictionary for additional information in result message
            content_type (str): Type of body (content) result message
            content_encoding (str): Encoding of body (content) result message
            delivery_mode (DeliveryMode): Delivery mode
            priority (int): Priority of delivery result message
            correlation_id: If of correlation for find result among all others
            reply_to (str): Name of queue for reply
            expiration (DateType): Time for expire result message
            message_id  (str): Id of message
            timestamp (DateType): Timestamp of result message
            type (str): Type of result message
            user_id (str): Id of user for result message
            app_id (str): Id of application for result message
        """
        self.action = action
        self.multiple = multiple
        self.requeue = requeue

        self.payload = payload
        self.headers: dict = headers
        self.content_type: str = content_type
        self.content_encoding: str = content_encoding
        self.delivery_mode: DeliveryMode = delivery_mode
        self.priority: int = priority
        self.correlation_id = correlation_id
        self.reply_to: str = reply_to
        self.expiration: DateType = expiration
        self.message_id: str = message_id
        self.timestamp: DateType = timestamp
        self.type: str = type
        self.user_id: str = user_id
        self.app_id: str = app_id

    def get_response_message(self, payload=None, headers: dict = None,
                             content_type: str = None, content_encoding: str = None,
                             delivery_mode: DeliveryMode = None,
                             priority: int = None, correlation_id=None,
                             reply_to: str = None, expiration: DateType = None,
                             message_id: str = None,
                             timestamp: DateType = None,
                             type: str = None, user_id: str = None,
                             app_id: str = None) -> Message:
        # body = ''.encode()
        # _content_type = 'text/plain'

        # try:
        body, _content_type = serialize(payload or self.payload)
        # except (PayloadTypeNotSupportedException, SerializeFailedException) as e:
        #     pass

        _headers = self.headers

        if headers is not None:
            if _headers is None:
                _headers = headers
            else:
                _headers.update(headers)

        return Message(
            body,
            content_type=content_type or _content_type or self.content_type,
            content_encoding=content_encoding or self.content_encoding,

            headers=_headers,
            delivery_mode=delivery_mode or self.delivery_mode,
            priority=priority or self.priority,
            correlation_id=correlation_id or self.correlation_id,
            reply_to=reply_to or self.reply_to,
            expiration=expiration or self.expiration,
            message_id=message_id or self.message_id,
            timestamp=timestamp or self.timestamp,
            type=type or self.type,
            user_id=user_id or self.user_id,
            app_id=app_id or self.app_id
        )
