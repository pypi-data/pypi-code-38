from __future__ import absolute_import

import threading

from django.apps import apps
from django.conf import settings as django_settings

import stackifyapm
from stackifyapm.contrib.django.client import client, get_client
from stackifyapm.utils.helper import get_stackify_header
from stackifyapm.traces import get_transaction
from stackifyapm.utils import build_name_with_http_method_prefix, get_name_from_func, get_name_from_path, wrapt

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


class StackifyAPMClientMiddlewareMixin(object):
    @property
    def client(self):
        try:
            app = apps.get_app_config("stackifyapm.contrib.django")
            return app.client
        except LookupError:
            return get_client()


def get_name_from_middleware(wrapped, instance):
    name = [type(instance).__name__, wrapped.__name__]
    if type(instance).__module__:
        name = [type(instance).__module__] + name
    return ".".join(name)


def process_request_wrapper(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)
    try:
        if response is not None:
            request = args[0]
            stackifyapm.set_transaction_name(
                build_name_with_http_method_prefix(get_name_from_middleware(wrapped, instance), request),
                override=False,
            )
    finally:
        return response


def process_response_wrapper(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)
    try:
        request, original_response = args
        if not hasattr(request, "_stackifyapm_view_func") and response is not original_response:
            stackifyapm.set_transaction_name(
                build_name_with_http_method_prefix(get_name_from_middleware(wrapped, instance), request),
                override=False,
            )
    finally:
        return response


class TracingMiddleware(MiddlewareMixin, StackifyAPMClientMiddlewareMixin):
    _stackifyapm_instrumented = False
    _instrumenting_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        super(TracingMiddleware, self).__init__(*args, **kwargs)
        if not self._stackifyapm_instrumented:
            with self._instrumenting_lock:
                if not self._stackifyapm_instrumented:
                    if self.client.config.instrument_django_middleware:
                        self.instrument_middlewares()

                    TracingMiddleware._stackifyapm_instrumented = True

    def instrument_middlewares(self):
        middlewares = getattr(django_settings, "MIDDLEWARE", None) or getattr(
            django_settings, "MIDDLEWARE_CLASSES", None
        )
        if middlewares:
            for middleware_path in middlewares:
                module_path, class_name = middleware_path.rsplit(".", 1)
                try:
                    module = import_module(module_path)
                    middleware_class = getattr(module, class_name)
                    if middleware_class == type(self):
                        continue
                    if hasattr(middleware_class, "process_request"):
                        wrapt.wrap_function_wrapper(middleware_class, "process_request", process_request_wrapper)
                    if hasattr(middleware_class, "process_response"):
                        wrapt.wrap_function_wrapper(middleware_class, "process_response", process_response_wrapper)
                except ImportError:
                    client.logger.info("Can't instrument middleware {}".format(middleware_path))

    def process_view(self, request, view_func, view_args, view_kwargs):
        request._stackifyapm_view_func = view_func

    def process_response(self, request, response):
        try:
            if hasattr(response, "status_code"):
                transaction = get_transaction()
                transaction_name = ''
                if getattr(request, "_stackifyapm_view_func", False):
                    transaction_name = get_name_from_func(request._stackifyapm_view_func)
                    transaction_name = build_name_with_http_method_prefix(transaction_name, request)
                else:
                    transaction_name = get_name_from_path(request.path)

                stackifyapm.set_transaction_name(transaction_name, override=False)
                stackifyapm.set_transaction_context(
                    lambda: self.client.get_data_from_request(
                        request, capture_body=self.client.config.capture_body in ("all", "transactions")
                    ),
                    "request",
                )
                stackifyapm.set_transaction_context(lambda: self.client.get_data_from_response(response), "response")

            response._headers['x-stackifyid'] = ('X-StackifyID', get_stackify_header(transaction))
        except Exception:
            self.client.error_logger.error("Exception during timing of request", exc_info=True)

        return response
