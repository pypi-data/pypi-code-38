from ..errors import ClientError


class ParseError(ClientError):
    def __init__(self, message="Error when parsing request", statusCode=422):
        self.statusCode = statusCode or 422
        self.message = message

    def __repr__(self):
        return self.message
