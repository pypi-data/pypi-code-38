from msrest.serialization import Model


class DebugInfoResponse(Model):
    """DebugInfoResponse.

    :param type:
    :type type: str
    :param message:
    :type message: str
    :param stack_trace:
    :type stack_trace: str
    :param inner_exception:
    :type inner_exception: ~swagger.models.DebugInfoResponse
    :param data:
    :type data: dict[str, object]
    :param error_response:
    :type error_response: ~swagger.models.ErrorResponse
    """

    _attribute_map = {
        'type': {'key': 'Type', 'type': 'str'},
        'message': {'key': 'Message', 'type': 'str'},
        'stack_trace': {'key': 'StackTrace', 'type': 'str'},
        'inner_exception': {'key': 'InnerException', 'type': 'DebugInfoResponse'},
        'data': {'key': 'Data', 'type': '{object}'},
        'error_response': {'key': 'ErrorResponse', 'type': 'ErrorResponse'},
    }

    def __init__(self, type=None, message=None, stack_trace=None, inner_exception=None,
                 data=None, error_response=None):
        super(DebugInfoResponse, self).__init__()
        self.type = type
        self.message = message
        self.stack_trace = stack_trace
        self.inner_exception = inner_exception
        self.data = data
        self.error_response = error_response
