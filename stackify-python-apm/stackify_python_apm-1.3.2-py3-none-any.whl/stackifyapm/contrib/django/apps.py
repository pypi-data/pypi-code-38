import logging
from functools import partial

from django.apps import AppConfig
from django.conf import settings as django_settings

from stackifyapm.conf import constants
from stackifyapm.conf import setup_logging
from stackifyapm.contrib.django.client import get_client
from stackifyapm.utils.disttracing import TraceParent

logger = logging.getLogger("stackifyapm.traces")

ERROR_DISPATCH_UID = "stackifyapm-exceptions"
REQUEST_START_DISPATCH_UID = "stackifyapm-request-start"
REQUEST_FINISH_DISPATCH_UID = "stackifyapm-request-stop"

TRACEPARENT_HEADER_NAME_WSGI = "HTTP_" + constants.TRACEPARENT_HEADER_NAME.upper().replace("-", "_")


class StackifyAPMConfig(AppConfig):
    """
    Django application config for StackifyAPM.
    """
    name = "stackifyapm.contrib.django"
    label = "stackifyapm.contrib.django"
    verbose_name = "StackifyAPM"

    def __init__(self, *args, **kwargs):
        super(StackifyAPMConfig, self).__init__(*args, **kwargs)
        self.client = None

    def ready(self):
        self.client = get_client()
        setup_logging(self.client)
        register_handlers(self.client)
        if self.client.config.instrument:
            instrument(self.client)
        else:
            self.client.logger.debug("Skipping instrumentation. INSTRUMENT is set to False.")


def register_handlers(client):
    from django.core.signals import got_request_exception, request_started, request_finished
    from stackifyapm.contrib.django.handlers import exception_handler

    got_request_exception.disconnect(dispatch_uid=ERROR_DISPATCH_UID)
    got_request_exception.connect(partial(exception_handler, client), dispatch_uid=ERROR_DISPATCH_UID, weak=False)

    request_started.disconnect(dispatch_uid=REQUEST_START_DISPATCH_UID)
    request_started.connect(partial(_request_started_handler, client), dispatch_uid=REQUEST_START_DISPATCH_UID, weak=False)

    request_finished.disconnect(dispatch_uid=REQUEST_FINISH_DISPATCH_UID)
    request_finished.connect(partial(_request_ended_handler, client), dispatch_uid=REQUEST_FINISH_DISPATCH_UID, weak=False)

    try:
        import celery  # noqa
        from stackifyapm.contrib.celery import register_exception_tracking

        try:
            register_exception_tracking(client)
        except Exception:
            client.logger.exception("Failed installing django-celery.")
    except ImportError:
        client.logger.debug("Not instrumenting Celery, couldn't import")


def _request_ended_handler(client, sender, *args, **kwargs):
    if not _is_middleware_enabled(client):
        return

    client.end_transaction()


def _request_started_handler(client, sender, *args, **kwargs):
    if not _is_middleware_enabled(client):
        return

    traceparent_header = None
    if "environ" in kwargs:
        traceparent_header = kwargs["environ"].get(TRACEPARENT_HEADER_NAME_WSGI)
    elif "scope" in kwargs:
        traceparent_header = None

    if traceparent_header:
        trace_parent = TraceParent.from_string(traceparent_header)
        logger.debug("Read traceparent header {}".format(traceparent_header))
    else:
        trace_parent = None

    client.begin_transaction("request", trace_parent=trace_parent, client=client)


def instrument(client):
    from stackifyapm.instrumentation.control import instrument

    instrument(client=client)
    try:
        import celery  # noqa F401
        from stackifyapm.contrib.celery import register_instrumentation

        register_instrumentation(client)
    except ImportError:
        client.logger.debug("Not instrumenting Celery, couldn't import")


def _is_middleware_enabled(client):
    middleware_attr = "MIDDLEWARE" if getattr(django_settings, "MIDDLEWARE", None) is not None else "MIDDLEWARE_CLASSES"
    middleware = getattr(django_settings, middleware_attr)
    return middleware and "stackifyapm.contrib.django.middleware.TracingMiddleware" in middleware
