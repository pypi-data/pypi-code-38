from msrest.serialization import Model


class InnerErrorResponse(Model):
    """InnerErrorResponse.

    :param code:
    :type code: str
    :param inner_error:
    :type inner_error: ~swagger.models.InnerErrorResponse
    """

    _attribute_map = {
        'code': {'key': 'Code', 'type': 'str'},
        'inner_error': {'key': 'InnerError', 'type': 'InnerErrorResponse'},
    }

    def __init__(self, code=None, inner_error=None):
        super(InnerErrorResponse, self).__init__()
        self.code = code
        self.inner_error = inner_error
