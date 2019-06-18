from __future__ import absolute_import

import flask
import logging
import sys
from flask import request, signals

import stackifyapm
import stackifyapm.instrumentation.control
from stackifyapm.base import Client
from stackifyapm.conf import constants
from stackifyapm.conf import setup_logging
from stackifyapm.contrib.flask.utils import get_data_from_request, get_data_from_response, get_data_from_exception
from stackifyapm.utils.helper import get_stackify_header
from stackifyapm.utils import build_name_with_http_method_prefix
from stackifyapm.utils.disttracing import TraceParent
from stackifyapm.utils.helper import get_rum_script_or_None
from stackifyapm.handlers.exceptions import get_exception_context
from stackifyapm.traces import get_transaction

logger = logging.getLogger("stackifyapm.errors.client")


def make_client(app, **defaults):
    if "framework_name" not in defaults:
        defaults["framework_name"] = "flask"
        defaults["framework_version"] = getattr(flask, "__version__", "<0.7")

    config = {
        "ENVIRONMENT": app.config.get("ENVIRONMENT") or app.config.get("ENV") or 'Production',
        "APPLICATION_NAME": app.config.get("APPLICATION_NAME") or 'Python Application',
        "BASE_DIR": app.config.get("BASE_DIR") or app.config.root_path,
        "CONFIG_FILE": app.config.get("CONFIG_FILE") or 'stackify.json',
    }

    return Client(config, **defaults)


class StackifyAPM(object):
    """
    Flask application for StackifyAPM.
    """
    def __init__(self, app=None, **defaults):
        self.app = app
        self.logging = logging
        self.client = None

        if app:
            self.init_app(app, **defaults)

    def init_app(self, app, **defaults):
        self.app = app
        if not self.client:
            self.client = make_client(app, **defaults)

        setup_logging(self.client)

        signals.got_request_exception.connect(self.handle_exception, sender=app, weak=False)

        try:
            from stackifyapm.contrib.celery import register_exception_tracking

            register_exception_tracking(self.client)
        except ImportError:
            pass

        # Instrument to get spans
        if self.client.config.instrument:
            stackifyapm.instrumentation.control.instrument(client=self.client)

            signals.request_started.connect(self.request_started, sender=app)
            signals.request_finished.connect(self.request_finished, sender=app)

            try:
                from stackifyapm.contrib.celery import register_instrumentation

                register_instrumentation(self.client)
            except ImportError:
                pass
        else:
            logger.debug("Skipping instrumentation. INSTRUMENT is set to False.")

        @app.context_processor
        def rum_tracing():
            transaction = get_transaction()
            rum_script = get_rum_script_or_None(transaction)
            if rum_script:
                return {
                    "stackifyapm_inject_rum": rum_script
                }
            return {}

    def request_started(self, app, **kwargs):
        if constants.TRACEPARENT_HEADER_NAME in request.headers:
            trace_parent = TraceParent.from_string(request.headers[constants.TRACEPARENT_HEADER_NAME])
        else:
            trace_parent = None

        self.client.begin_transaction("request", trace_parent=trace_parent, client=self.client)

    def request_finished(self, app, response, **kwargs):
        transaction = get_transaction()

        rule = request.url_rule.rule if request.url_rule is not None else ""
        rule = build_name_with_http_method_prefix(rule, request)
        stackifyapm.set_transaction_context(
            lambda: get_data_from_request(
                request, capture_body=self.client.config.capture_body in ("transactions", "all")
            ),
            "request",
        )
        stackifyapm.set_transaction_context(lambda: get_data_from_response(response), "response")
        stackifyapm.set_transaction_name(rule, override=False)
        self.client.end_transaction()

        response.headers["X-StackifyID"] = get_stackify_header(transaction)

    def handle_exception(self, app, **kwargs):
        if not self.client:
            return

        exc_info = sys.exc_info()
        if exc_info:
            exception = exc_info[1]
            traceback = exc_info[2]
        else:
            return

        rule = request.url_rule.rule if request.url_rule is not None else ""
        rule = build_name_with_http_method_prefix(rule, request)
        stackifyapm.set_transaction_context(
            lambda: get_data_from_request(
                request, capture_body=self.client.config.capture_body in ("transactions", "all")
            ),
            "request",
        )
        stackifyapm.set_transaction_context(lambda: get_data_from_exception(), "response")
        stackifyapm.set_transaction_name(rule, override=False)

        self.client.capture_exception(
            exception=get_exception_context(exception, traceback)
        )
        self.client.end_transaction()

    def capture_exception(self, *args, **kwargs):
        assert self.client, "capture_exception called before application configured"
        return self.client.capture_exception(*args, **kwargs)
