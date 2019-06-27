class AiopikaException(Exception):
    requeue = None


class RoutingException(AiopikaException):
    pass


class PayloadTypeNotSupportedException(AiopikaException):
    requeue = False


class ContentTypeNotSupportedException(AiopikaException):
    requeue = False


class EndpointNotImplementedException(AiopikaException):
    pass


class ResponseFailedSendException(AiopikaException):
    pass


class SerializeFailedException(AiopikaException):
    requeue = False


class DeserializeFailedException(AiopikaException):
    requeue = False


class IncomingRoutingFailedException(AiopikaException):
    pass


class ResultDeliveryFailedException(AiopikaException):
    requeue = False
