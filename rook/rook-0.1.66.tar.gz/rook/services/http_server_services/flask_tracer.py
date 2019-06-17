"""This module initializes the flask hook """

import six
import time

from rook.logger import logger

from rook.processor.namespaces.container_namespace import ContainerNamespace
from rook.processor.namespaces.python_object_namespace import PythonObjectNamespace

from functools import update_wrapper


class FlaskTracer(object):
    NAME = "flask"

    def __init__(self, execute_augs_callback):
        logger.info("installing flask hook")

        try:
            import flask
            from flask import request
            self._request = request
        except ImportError as e:
            six.print_("Rook failed to import dependencies: " + str(e))
            return

        if getattr(flask, '_flask_patch', False):
            return

        self._execute_augs_callback = execute_augs_callback

        # Install hooks
        flask.app.Flask.__init__ = self._wrap_function(self, flask.app.Flask.__init__)

        setattr(flask, '_flask_patch', True)

    @staticmethod
    def _wrap_function(flask_tracer, function_to_wrap):
        # self is the app instance
        def new_f(self, import_name, *args, **kwargs):

            ret_val = function_to_wrap(self, import_name, *args, **kwargs)

            self.before_request(flask_tracer.before_request)
            self.after_request(flask_tracer.after_request)
            self.teardown_request(flask_tracer.teardown_request)

            return ret_val

        return update_wrapper(new_f, function_to_wrap)

    def before_request(self):
        try:
            setattr(self._request, "start_time", time.time())
        except:
            return

    def after_request(self, response):
        try:
            code = response.status_code if response else ''
            setattr(self._request, "status_code", code)
        finally:
            return response

    def teardown_request(self, exception):
        try:
            start_time = getattr(self._request, 'start_time', None)
            if not start_time:
                return

            code = getattr(self._request, 'status_code', None)
            if not code:
                code = "Unknown"

            duration = time.time() - start_time
            extracted = ContainerNamespace(
                {'duration': PythonObjectNamespace(duration),
                 'remote_host': PythonObjectNamespace(self._request.remote_addr),
                 'url': PythonObjectNamespace(self._request.url),
                 'method': PythonObjectNamespace(self._request.method),
                 'status_code': PythonObjectNamespace(code)})

            self._execute_augs_callback(extracted)
        except:
            return
