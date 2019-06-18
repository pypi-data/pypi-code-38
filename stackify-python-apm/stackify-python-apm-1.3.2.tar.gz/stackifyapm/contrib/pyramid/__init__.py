import os
import pkg_resources
import sys

from stackifyapm.base import Client
from stackifyapm.conf import setup_logging
from stackifyapm.handlers.exceptions import get_exception_context
from stackifyapm.utils.helper import get_stackify_header
from stackifyapm.instrumentation.control import instrument
from stackifyapm.traces import get_transaction, set_transaction_context
from stackifyapm.utils import get_url_data


def includeme(config):
    config.add_tween('stackifyapm.contrib.pyramid.stackifyapm_tween_factory')
    config.scan('stackifyapm.contrib.pyramid')


def get_data_from_request(request):
    return {
        "headers": dict(**request.headers),
        "method": request.method,
        "url": get_url_data(request.url),
    }


def get_data_from_response(response=None):
    return {
        "status_code": response and response.status_int or 500,
    }


def make_client(registry, **defaults):
    config = {
        "FRAMEWORK_NAME": "pyramid",
        "FRAMEWORK_VERSION": pkg_resources.get_distribution("pyramid").version,
        "ENVIRONMENT": (
            registry.settings.get('ENVIRONMENT') or
            registry.settings.get('environment') or
            'Production'
        ),
        "APPLICATION_NAME": (
            registry.settings.get('APPLICATION_NAME') or
            registry.settings.get('application_name') or
            'Python Application'
        ),
        "BASE_DIR": os.getcwd(),
        "CONFIG_FILE": (
            registry.settings.get('CONFIG_FILE') or
            registry.settings.get('config_file') or
            'stackify.json'
        ),
    }

    return Client(config, **defaults)


class stackifyapm_tween_factory(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry
        self.client = make_client(registry)
        setup_logging(self.client)
        instrument(client=self.client)

    def __call__(self, request):
        response = None
        self.client.begin_transaction('request', client=self.client)
        try:
            response = self.handler(request)
            response.headers["X-StackifyID"] = get_stackify_header(get_transaction())
            return response
        except Exception:
            exc_info = sys.exc_info()
            if exc_info:
                exception = exc_info[1]
                traceback = exc_info[2]
                self.client.capture_exception(
                    exception=get_exception_context(exception, traceback)
                )
            raise
        finally:
            transaction_name = request.matched_route.pattern if request.matched_route else request.view_name
            transaction_name = " ".join((request.method, transaction_name)) if transaction_name else ""
            set_transaction_context(lambda: get_data_from_request(request), "request")
            set_transaction_context(lambda: get_data_from_response(response), "response")
            self.client.end_transaction(transaction_name)
