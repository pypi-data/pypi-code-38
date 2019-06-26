from abc import ABC, abstractmethod
from typing import Dict

from .method import Method
from .exceptions import IncomingRoutingFailedException, EndpointNotImplementedException

from aio_pika import IncomingMessage


class Router(ABC):
    """
    Abstract class for routing incoming message by any basis.
    """

    def __init__(self, methods: Dict[str, Method]):
        self._methods: Dict[str, Method] = methods

    def route(self, message: IncomingMessage) -> Method:
        """
        Route by message

        Args:
            message (IncomingMessage): Incoming message from driver processing

        Returns:
            Method: Routed method
        """
        method = self.get_method_identifier(message)

        if method is None:
            raise IncomingRoutingFailedException

        if method not in self._methods:
            raise EndpointNotImplementedException

        return self._methods[method]

    @staticmethod
    @abstractmethod
    def get_method_identifier(message: IncomingMessage) -> str:
        """
        Function for getting method identifier from incoming message

        Args:
            message (IncomingMessage): Incoming message from driver processing

        Returns:
            str: Found method identifier or None
        """
        pass


class HeaderMethodRouter(Router):
    """
    The router by method identifier in `method` header of message.
    """

    @staticmethod
    def get_method_identifier(message: IncomingMessage) -> str:
        return message.headers.get('method', None)
