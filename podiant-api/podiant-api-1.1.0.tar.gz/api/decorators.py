from api.exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    MethodNotAllowedError,
    NotAcceptableError,
    NotAuthenticatedError,
    UnprocessableEntityError,
    UnsupportedMediaTypeError
)

from api import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse, Http404

import json
import logging


DEFAULT_MEDIA_TYPE = 'application/vnd.api+json'


def jsonapi(accepted_media_types=(DEFAULT_MEDIA_TYPE,)):
    """
    Wraps around the `get()`, `post()`, `put()`, `patch()` and `delete()`
    methods of a View class, interpreting all responses and exceptions, and
    outputting JSON.

    This decorator will catch any user-originated error and report it to the
    API client with the correct HTTP status code. Other errors are returned
    as 500 errors, and are logged to the `podiant.api` logger.

    Example::

        class ListView(View):
            @jsonapi()
            def get(self, request):
                ...
    """

    def wrapper(f):
        def a(view, request, *args, **kwargs):
            if request.method in ('OPTIONS', 'HEAD'):
                response = HttpResponse(
                    content_type=DEFAULT_MEDIA_TYPE
                )

                allowed = ['OPTIONS', 'HEAD']

                if hasattr(view, 'get'):
                    allowed.append('GET')

                if hasattr(view, 'post'):
                    allowed.append('POST')

                if hasattr(view, 'put'):
                    allowed.append('PUT')

                if hasattr(view, 'patch'):
                    allowed.append('PATCH')

                if hasattr(view, 'delete'):
                    allowed.append('DELETE')

                response['Allow'] = ', '.join(allowed)
                return response

            try:
                if accepted_media_types is not None:
                    if request.method in ('PATCH', 'POST', 'PUT'):
                        content_type = request.META.get('CONTENT_TYPE')
                        if content_type not in accepted_media_types:
                            raise UnsupportedMediaTypeError(
                                (
                                    'Content-Type header must be set to '
                                    '"application/vnd.api+json".'
                                )
                            )

                accepts = [
                    a.strip()
                    for a in request.META.get('ACCEPT', '').split(',')
                    if a and a.strip()
                ]

                if any(accepts) and DEFAULT_MEDIA_TYPE not in accepts:
                    raise NotAcceptableError(
                        (
                            'If specified, the Accept header must contain '
                            '"application/vnd.api+json".'
                        )
                    )

                return f(view, request, *args, **kwargs)
            except NotAuthenticatedError as ex:
                e = {
                    'status': 401,
                    'title': 'Unauthorized'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=401,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except UnprocessableEntityError as ex:
                e = {
                    'status': 422,
                    'title': 'Unprocessable Entity'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                    if len(ex.args) > 1:
                        e['meta'] = ex.args[1]

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=422,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except BadRequestError as ex:
                e = {
                    'status': 400,
                    'title': 'Bad Request'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=400,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except ForbiddenError as ex:
                e = {
                    'status': 403,
                    'title': 'Forbidden'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                    if len(ex.args) > 1:
                        e['meta'] = ex.args[1]

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=403,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except (ObjectDoesNotExist, Http404) as ex:
                e = {
                    'status': 404,
                    'title': 'Not Found'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=404,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except MethodNotAllowedError as ex:
                e = {
                    'status': 405,
                    'title': 'Method Not Allowed'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=405,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except NotAcceptableError as ex:
                e = {
                    'status': 406,
                    'title': 'Not Acceptable'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=406,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except ConflictError as ex:
                e = {
                    'status': 409,
                    'title': 'Conflict'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=409,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except UnsupportedMediaTypeError as ex:
                e = {
                    'status': 415,
                    'title': 'Unsupported Media Type'
                }

                if any(ex.args):
                    e['detail'] = str(ex.args[0])

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=415,
                    content_type=DEFAULT_MEDIA_TYPE
                )
            except Exception as ex:  # pragma: no cover
                e = {
                    'status': 500,
                    'title': 'Internal Server Error'
                }

                if settings.DEBUG:
                    if any(ex.args):
                        e['detail'] = str(ex.args[0])

                    if len(ex.args) > 1:
                        e['meta'] = ex.args[1]

                logger = logging.getLogger('podiant.api')
                logger.error('Error processing API request', exc_info=True)

                return HttpResponse(
                    json.dumps(
                        {
                            'error': e
                        },
                        indent=2
                    ),
                    status=500,
                    content_type=DEFAULT_MEDIA_TYPE
                )

        return a

    return wrapper
