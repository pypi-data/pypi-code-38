from msrest.serialization import Model


class RootError(Model):
    """RootError.

    :param code:
    :type code: str
    :param message:
    :type message: str
    :param target:
    :type target: str
    :param details:
    :type details: list[~swagger.models.ErrorDetails]
    :param inner_error:
    :type inner_error: ~swagger.models.InnerErrorResponse
    :param debug_info:
    :type debug_info: ~swagger.models.DebugInfoResponse
    """

    _attribute_map = {
        'code': {'key': 'Code', 'type': 'str'},
        'message': {'key': 'Message', 'type': 'str'},
        'target': {'key': 'Target', 'type': 'str'},
        'details': {'key': 'Details', 'type': '[ErrorDetails]'},
        'inner_error': {'key': 'InnerError', 'type': 'InnerErrorResponse'},
        'debug_info': {'key': 'DebugInfo', 'type': 'DebugInfoResponse'},
    }

    def __init__(self, code=None, message=None, target=None, details=None, inner_error=None, debug_info=None):
        super(RootError, self).__init__()
        self.code = code
        self.message = message
        self.target = target
        self.details = details
        self.inner_error = inner_error
        self.debug_info = debug_info
