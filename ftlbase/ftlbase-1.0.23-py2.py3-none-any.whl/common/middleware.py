# -*- coding: utf-8 -*-

from django.contrib import messages
from django.db import models
from django.db.models import signals
from django.shortcuts import redirect
from django.utils.functional import curry
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

"""Add user created_by and modified_by foreign key refs to any model automatically.
   Almost entirely taken from https://github.com/Atomidata/django-audit-log/blob/master/audit_log/middleware.py"""


def get_current_request():
    """ returns the request object for this thread """
    return getattr(_thread_locals, "request", None)


def set_current_request(request):
    _thread_locals.request = request


def get_current_user():
    """ returns the request user for this thread """
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    _thread_locals.user = user


def set_current_request_and_user(request):
    """ Set current request and user if is authenticated """
    set_current_request(request)

    if hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
    else:
        user = None

    set_current_user(user)

    return user


""" Tratamento dos campos de created_by e modified_by e 
    tratamento de erro de deleção de registro pai associado a FK em algum filho """


class FTLMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        self.process_request(request)
        response = self.get_response(request)
        self.process_response(request, response)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_request(self, request):
        user = set_current_request_and_user(request)

        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(mark_whodid, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def mark_whodid(self, user, sender, instance, **kwargs):
        # print('response mark =-=-=-=-=-=-=-=-=-=-=-= class=',self.__class__, 'request=',request, 'user=', user)
        if not getattr(instance, 'created_by_id', None):
            instance.created_by = user
        if hasattr(instance, 'modified_by_id'):
            instance.modified_by = user

    def process_exception(self, request, exception):
        """ Called when a view raises an exception.
        Keyword arguments:
        request -- the HttpRequest object.
        exception -- an Exception object raised by the view function.
        Response value:
        None -- An empty value; the default exception handling kicks in.
        HttpResponse -- An HttpResponse object; If it returns an HttpResponse object, the template response
                        and response middleware will be applied, and the resulting response returned to the browser.
                        If an exception middleware returns a response, the middleware classes above that middleware
        will not be called at all.
        NOTE: Response-phase method applied in reverse order, from the bottom up. This means classes defined at
              the end of MIDDLEWARE_CLASSES will be run first.
        """
        if request.method == 'POST':
            if exception.__class__ == models.ProtectedError:
                messages.error(request, mark_safe(
                    u'<strong>%s</strong>: Registro não pode ser excluído pois está sendo usado em outro local. '
                    u'<br>Mensagem original: %s.' % (request.user.first_name, _(exception.args[0]))))
                return redirect(request.get_full_path())
        return None
