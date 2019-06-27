from .endpoint import AiopikaEndpoint
from .exceptions import RoutingException


class Method(object):
    """
    Class for storage handler endpoint and his identifier. This is analog of HTTP Route class.
    """

    def __init__(self, handler: AiopikaEndpoint, identifier: str):
        """
        Initialize of Method

        Args:
            handler (AiopikaEndpoint): Instance of AiopikaEndpoint
            identifier (str): Identifier of method
        """
        super(Method, self).__init__()

        if not isinstance(handler, AiopikaEndpoint):
            raise RoutingException('Handler must be instance of AiopikaEndpoint class')

        self._handler = handler
        self._identifier = identifier

    @property
    def handler(self) -> AiopikaEndpoint:
        return self._handler

    @property
    def identifier(self) -> str:
        return self._identifier
