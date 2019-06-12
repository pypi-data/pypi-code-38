class CeleryException(Exception):
    pass


class RoutingException(CeleryException):
    pass


class ContentTypeNotSupportedException(CeleryException):
    pass


class PayloadFormattingException(CeleryException):
    pass


class EndpointNotImplementedException(CeleryException):
    pass
