import json
from django.http import JsonResponse, HttpResponse, HttpRequest

from . import exceptions
from . import fields


def processRequest(request, field=None, allowedMethods=["GET", "POST"]):
    if not isinstance(request, HttpRequest):
        raise TypeError("Expected HttpRequest")

    if request.method not in allowedMethods:
        raise exceptions.MethodNotAllowedException(allowedMethods)

    if not (request.META.get('CONTENT_TYPE') and 'application/json' in request.META.get('CONTENT_TYPE')):
        raise exceptions.BadRequestException("Expected JSON content type")

    if request.body.strip():
        try:
            requestData = json.loads(request.body)
        except ValueError as e:
            raise exceptions.BadRequestException("Error while parsing JSON content: {}".format(str(e)))
    else:
        requestData = None

    if field is not None:
        if not isinstance(field, fields.Field):
            raise TypeError("Expected Field or None")
        cleanedData = None
        try:
            def add(v):
                nonlocal cleanedData
                cleanedData = v
            field.cleanAndAdd(requestData is not None, requestData, add)
        except fields.FieldException as e:
            raise exceptions.BadRequestException("Field exception", e)
    else:
        cleanedData = requestData

    return (cleanedData)


def processResponse(response, safeEncoding=True):
    if isinstance(response, HttpResponse):
        return response
    elif isinstance(response, (dict)) or not safeEncoding:
        return JsonResponse(response, safe=safeEncoding)
    else:
        raise TypeError("Unexpected response type")


def processException(exception):
    if isinstance(exception, exceptions.ServerException):
        return exception.buildResponse()
    else:
        raise exception
