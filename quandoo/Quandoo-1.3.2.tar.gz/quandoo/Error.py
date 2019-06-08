class QuandooException(Exception):

    def __init__(self, error_type, error_message):
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self):
        return "{}: {}".format(self.error_type, self.error_message)


class APIException(QuandooException):

    def __init__(self, status_code, response, request):
        super().__init__("{} {}".format(status_code, response["errorType"]), response["errorMessage"])
        self.request = request


class PoorResponse(APIException):

    def __init__(self, status_code, response, request):
        super().__init__(status_code, response, request)


class PoorRequest(APIException):

    def __init__(self, status_code, response, request):
        super().__init__(status_code, response, request)


class PoorType(QuandooException):

    def __init__(self, status_code, data):
        super().__init__(status_code, data)
