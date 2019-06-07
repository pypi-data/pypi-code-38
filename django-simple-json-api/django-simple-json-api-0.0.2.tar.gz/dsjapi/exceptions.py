from django.http import JsonResponse, HttpResponseNotAllowed


class PrintableException(Exception):

    def toDict(self):
        return {"type": self.__class__.__name__}

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return repr(self.toDict())


class ServerException(PrintableException):

    def buildResponse(self):
        raise NotImplementedError()


class JSONServerException(ServerException):

    def __init__(self, status):
        self._status = status

    def getStatus(self):
        return self._status

    def buildResponse(self):
        return JsonResponse(self.toDict(), status=self._status)


class CommonException(PrintableException):

    def __init__(self, message=None, cause=None):
        self._message = message
        self._cause = cause

    def getCause(self):
        return self._cause

    def getMessage(self):
        return self._message

    def toDict(self):
        content = super().toDict()
        if self._message is not None:
            content["message"] = self._message
        if self._cause is not None:
            content["cause"] = self._cause.toDict()
        return content

    def __str__(self):
        txt = self.__class__.__name__
        if self._message is not None:
            txt += ": {}".format(self._message)
        if self._cause is not None:
            txt += "\nCaused by:\n{}".format(str(self._cause))
        return txt


class CommonJSONServerException(JSONServerException, CommonException):

    def __init__(self, status, message=None, cause=None):
        JSONServerException.__init__(self, status)
        CommonException.__init__(self, message, cause)


class AuthenticationException(CommonJSONServerException):

    def __init__(self, message=None, cause=None):
        super().__init__(401, message, cause)


class BadRequestException(CommonJSONServerException):

    def __init__(self, message=None, cause=None):
        super().__init__(400, message, cause)


class NotFoundException(CommonJSONServerException):

    def __init__(self, message=None, cause=None):
        super().__init__(404, message, cause)


class ServerErrorException(CommonJSONServerException):

    def __init__(self, message=None, cause=None):
        super().__init__(500, message, cause)


class MethodNotAllowedException(ServerException):

    def __init__(self, allowedMethods):
        self._allowedMethods = allowedMethods

    def toDict(self):
        content = super().toDict()
        content["allowedMethods"] = self._allowedMethods
        return content

    def __str__(self):
        return "{}\nAllowed methods:\n{}".format(self.__class__.__name__, self._allowedMethods)

    def buildResponse(self):
        return HttpResponseNotAllowed(self._allowedMethods)
