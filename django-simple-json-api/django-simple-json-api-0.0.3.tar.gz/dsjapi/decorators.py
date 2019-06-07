from functools import wraps
from . import process
from . import exceptions


class Request:

    def __init__(self, request, data):
        super().__setattr__("data", data)
        super().__setattr__("request", request)

    def __getattr__(self, name):
        if name not in ["data", "request"]:
            raise AttributeError("Request object only supports 'request' and 'data' attributes")
        return super().__getattr__(name)

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __setattr__(self, name, value):
        raise NotImplementedError()


def api_rq(field=None, allowedMethods=["GET", "POST"], safeEncoding=True):

    def decorator(func):

        @wraps(func)
        def wrappedFunc(request):

            try:
                data = process.processRequest(request, field, allowedMethods)
                response = func(Request(request, data))
                return process.processResponse(response, safeEncoding)
            except exceptions.ServerException as e:
                return e.buildResponse()

        return wrappedFunc

    return decorator


def api(field=None, allowedMethods=["GET", "POST"], safeEncoding=True):

    def decorator(func):

        @wraps(func)
        def wrappedFunc(request):

            @api_rq(field, allowedMethods)
            def rqFunc(request):
                return func(request.data)

            return rqFunc(request)

        return wrappedFunc

    return decorator
