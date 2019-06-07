from django.http import JsonResponse, HttpResponseNotAllowed

class ServerException(Exception):

    def buildResponse(self):
        raise NotImplementedError()

class JSONServerException(ServerException):

    def __init__(self, status, message=None, data=None):
        self._status = status
        self._message = message
        self._data = data

    def getData(self):
        return self._data

    def getStatus(self):
        return self._status

    def getMessage(self):
        return self._message

    def buildResponse(self):
        content = {}
        if self._message is not None:
            content["message"] = self._message
        if self._data is not None:
            content["data"] = self._data
        return JsonResponse(content, status=self._status)


class AuthenticationException(JSONServerException):

    def __init__(self, message=None, data=None):
        super().__init__(401, message, data)


class BadRequestException(JSONServerException):

    def __init__(self, message=None, data=None):
        super().__init__(400, message, data)


class NotFoundException(JSONServerException):

    def __init__(self, message=None, data=None):
        super().__init__(404, message, data)


class ServerErrorException(JSONServerException):

    def __init__(self, message=None, data=None):
        super().__init__(500, message, data)


class MethodNotAllowedException(ServerException):

    def __init__(self, allowedMethods):
        self._allowedMethods = allowedMethods

    def buildResponse(self):
        return HttpResponseNotAllowed(self._allowedMethods)
