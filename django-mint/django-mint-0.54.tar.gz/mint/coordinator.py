from mint import utils
from mint import exceptions
from django import http
from django.conf import settings
import traceback
import logging
import json


class HttpResponseUnauthorized(http.HttpResponse):
    status_code = 403


class Coordinator(object):
    controllers = []

    def __init__(self, request, ctx, idx=None, action=None):
        self.request = request
        self.ctx = utils.underscore_to_camel(ctx)
        self.id = idx
        self.action = action
        self.related = action
        self.controller = None
        self.related_controller = None

    def open(self):
        for ctx in self.controllers:
            if ctx.__name__ == self.ctx:
                self.controller = ctx(self.request)
                return
        raise exceptions.InvalidContext('This controller does not exist: %s' % self.ctx)

    def run(self):
        try:
            return self.run_inner()
        except exceptions.HttpError as exc:
            if isinstance(exc, exceptions.HttpBadRequest):
                return self.return_error(exc, response=http.HttpResponseBadRequest)
            elif isinstance(exc, exceptions.HttpForbidden):
                return self.return_error(exc, response=http.HttpResponseForbidden)
            elif isinstance(exc, exceptions.HttpNotAllowed):
                return self.return_error(exc, response=http.HttpResponseNotAllowed)
            elif isinstance(exc, exceptions.HttpNotFound):
                return self.return_error(exc, response=http.HttpResponseNotFound)
            elif isinstance(exc, exceptions.HttpUnauthorized):
                return self.return_error(exc, response=HttpResponseUnauthorized)
            elif isinstance(exc, exceptions.HttpError):
                self.report_exception()
                return self.return_error(exc, response=http.HttpResponseServerError)
        except Exception as exc:
            self.report_exception()
            return self.return_error(exc, response=http.HttpResponseServerError)

    def run_inner(self):
        self.open()
        if self.id and self.action:
            if self.find_action():
                return self.exec_action()
            else:
                raise exceptions.HttpBadRequest("No such action: %s" % self.action)
        elif self.id:
            if self.find_action(self.id):
                self.action = self.id
                self.id = None
                return self.exec_action()
            else:
                return self.exec_id()
        elif not self.id and self.action:
            if self.find_action():
                return self.exec_action()
            else:
                raise exceptions.HttpBadRequest("No such action: %s" % self.action)
        else:
            return self.exec_root()

    def find_action(self, action=None):
        if not action:
            action = self.action
        return self.controller.has_action(action)

    def exec_action(self):
        return self.return_success(self.controller.exec_action(self.action, self.id))

    def exec_id(self):
        return self.return_success(self.controller.exec_id(self.id))

    def exec_root(self):
        self.controller.open_model()
        return self.return_success(self.controller.exec_root())

    def return_success(self, out, response=http.HttpResponse):
        return self.format(out, response=response)

    def return_error(self, exc=None, error=None, message=None, response=http.HttpResponse):
        if exc:
            tb = traceback.format_exc().split("\n") if settings.DEBUG else []
            tb = [item.strip().replace('"', "'") for item in tb]
            return self.format({
                'message': str(exc),
                'error': exc.__class__.__name__,
                'traceback': tb,
            }, response=response)
        elif error and message:
            return self.format({
                'message': message,
                'error': error
            }, response=response)
        else:
            return self.format({
                'message': 'Error handler not correctly invoked',
                'error': 'Exception'
            }, response=response)

    def format(self, out, response=http.HttpResponse):
        if out is True:
            return self.format({}, response=response)
        else:
            return response(json.dumps(out), content_type='application/json')

    def report_exception(self):
        logger = logging.getLogger('django.request')
        logger.exception(
            "Internal Server Error during API call: %s" % self.request.path,
            extra={'status_code': 500, 'request': self.request}
        )