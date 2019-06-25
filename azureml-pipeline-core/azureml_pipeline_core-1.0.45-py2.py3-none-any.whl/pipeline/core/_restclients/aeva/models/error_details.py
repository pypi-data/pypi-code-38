from msrest.serialization import Model


class ErrorDetails(Model):
    """ErrorDetails.

    :param code:
    :type code: str
    :param message:
    :type message: str
    :param target:
    :type target: str
    """

    _attribute_map = {
        'code': {'key': 'Code', 'type': 'str'},
        'message': {'key': 'Message', 'type': 'str'},
        'target': {'key': 'Target', 'type': 'str'},
    }

    def __init__(self, code=None, message=None, target=None):
        super(ErrorDetails, self).__init__()
        self.code = code
        self.message = message
        self.target = target
