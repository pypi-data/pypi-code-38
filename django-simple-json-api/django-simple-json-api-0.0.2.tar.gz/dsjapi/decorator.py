import json
from functools import wraps
from django.http import JsonResponse, HttpResponse

from . import exceptions
from . import fields


def api(field=None):

    def decorator(func):

        @wraps(func)
        def wrappedFunc(request):
            try:
                if request.method not in ['GET', 'POST']:
                    raise exceptions.MethodNotAllowedException(['GET', 'POST'])

                if not (request.META.get('CONTENT_TYPE') and 'application/json' in request.META.get('CONTENT_TYPE')):
                    raise exceptions.BadRequestException("Expected JSON content type")

                if request.body.isspace():
                    requestData = None
                else:
                    try:
                        requestData = json.loads(request.body)
                    except ValueError as e:
                        raise exceptions.BadRequestException("Error while parsing JSON content: {}".format(str(e)))

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

                response = func(cleanedData)

                if isinstance(response, HttpResponse):
                    return response
                elif isinstance(response, (dict)):
                    return JsonResponse(response)
                else:
                    raise TypeError("Unexpected response type")

            except exceptions.ServerException as e:
                return e.buildResponse()

        return wrappedFunc

    return decorator
