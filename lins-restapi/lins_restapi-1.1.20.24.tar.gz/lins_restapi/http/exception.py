from django.http import Http404
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.views.debug import ExceptionReporter
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import set_rollback
from rest_framework.settings import api_settings
import logging
import sys


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    data = {}

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        data['code'] = exc.status_code
        data['error_code'] = getattr(exc, 'code', exc.default_code)
        if isinstance(exc.detail, (list, dict)):
            message = exc.default_detail
            # A String abaixo deveria estar no dicionário, mas não está, por isso foi traduzido aqui
            if 'Invalid input.' in str(message):
                message = u'Entrada inválida.'
            data['message'] = message
            if isinstance(exc.detail, list):
                # Errors raised as a list are non-field errors.
                data['data'] = {api_settings.NON_FIELD_ERRORS_KEY: exc.detail}
            else:
                data['data'] = exc.detail
        else:
            data['message'] = exc.detail

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        code = status.HTTP_404_NOT_FOUND
        data['code'] = code
        data['error_code'] = 'not_found'
        data['message'] = _('Not found.')

        set_rollback()
        return Response(data, status=code)

    elif isinstance(exc, PermissionDenied):
        code = status.HTTP_403_FORBIDDEN
        data['code'] = code
        data['error_code'] = 'permission_denied'
        data['message'] = _('Permission denied.')

        set_rollback()
        return Response(data, status=code)

    elif not settings.DEBUG:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        data['code'] = code
        data['error_code'] = 'error'
        data['message'] = _('A server error occurred.')

        text = get_traceback_text(context['request'])
        send_log(text)

        set_rollback()
        return Response(data, status=code)


def send_log(text):
    logger = logging.getLogger('apilog')
    logger.error(text)


def get_traceback_text(request):
    """
    Create a technical server error
    """
    exc_info = sys.exc_info()
    reporter = ExceptionReporter(request, *exc_info)
    text = reporter.get_traceback_text()
    return text
