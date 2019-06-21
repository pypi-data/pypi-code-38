class HTTPError(Exception):
    def __init__(
        self,
        message="Server Error",
        statusCode=500,
        errorType=None,
        errorCode=None,
        key=None,
    ):
        self.statusCode = statusCode
        self.message = message
        self.errorType = errorType
        self.errorCode = errorCode
        self.key = key

    def __repr__(self):
        return self.message

    def toJSON(self):
        d = {
            "message": self.message,
        }

        for k in ["errorType", "errorCode", "key"]:
            if getattr(self, k, None) != None:
                d[k] = getattr(self, k)

        return d


class ClientError(HTTPError):
    def __init__(
        self,
        message="Invalid Request",
        statusCode=400,
        errorType=None,
        errorCode=None,
        key=None,
    ):
        super().__init__(
            message,
            statusCode,
            errorType,
            errorCode,
            key,
        )


class ServerError(HTTPError):
    def __init__(
        self,
        message="Server Error",
        statusCode=500,
        errorType=None,
        errorCode=None,
        key=None,
    ):
        super().__init__(
            message,
            statusCode,
            errorType,
            errorCode,
            key,
        )


class ErrorList(Exception):
    def __init__(self, errors):
        self.errors = errors