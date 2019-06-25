from msrest.serialization import Model
from msrest.exceptions import HttpOperationError


class ErrorResponse(Model):
    """ErrorResponse.

    :param error:
    :type error: ~swagger.models.RootError
    :param correlation:
    :type correlation: dict[str, str]
    """

    _attribute_map = {
        'error': {'key': 'Error', 'type': 'RootError'},
        'correlation': {'key': 'Correlation', 'type': '{str}'},
    }

    def __init__(self, error=None, correlation=None):
        super(ErrorResponse, self).__init__()
        self.error = error
        self.correlation = correlation


class ErrorResponseException(HttpOperationError):
    """Server responsed with exception of type: 'ErrorResponse'.

    :param deserialize: A deserializer
    :param response: Server response to be deserialized.
    """

    def __init__(self, deserialize, response, *args):

        super(ErrorResponseException, self).__init__(deserialize, response, 'ErrorResponse', *args)
