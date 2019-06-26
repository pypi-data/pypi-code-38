from enum import Enum
import uuid

from ..result import AiopikaResult, AiopikaResultAction, DateType
from ..serializers import deserialize, DeserializeFailedException, ContentTypeNotSupportedException

from aio_pika import Message, IncomingMessage


class RPCMessageType(Enum):
    call = 'call'
    error = 'error'
    result = 'result'


class RPCRequest(object):

    def __init__(self, message: IncomingMessage, identifier: str, payload = None):
        self._message: IncomingMessage = message
        self._identifier: str = identifier
        self._payload = payload

    @property
    def message(self) -> IncomingMessage:
        return self._message

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def payload(self):
        return self._payload


class RPCResponse(object):

    def __init__(self, payload=None, type: RPCMessageType = RPCMessageType.result):
        self.payload = payload
        self.type = type

    def get_result(self, correlation_id: str, identifier: str, expire: DateType) -> AiopikaResult:
        return AiopikaResult(
            action=AiopikaResultAction.ack,
            payload=self.payload,
            correlation_id=correlation_id,
            headers={
                'method': identifier
            },
            expiration=expire,
            type=self.type.value,
        )


def response_from_raw(body: bytes, content_type: str, type_value: str) -> RPCResponse:
    payload = deserialize(body, content_type)

    return RPCResponse(payload=payload, type=RPCMessageType(type_value))
