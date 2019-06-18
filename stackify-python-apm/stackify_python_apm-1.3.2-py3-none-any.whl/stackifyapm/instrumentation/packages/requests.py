from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import get_transaction
from stackifyapm.utils import default_ports
from stackifyapm.utils.compat import urlparse
from stackifyapm.utils.helper import is_async_span


def get_host_from_url(url):
    parsed_url = urlparse.urlparse(url)
    host = parsed_url.hostname or " "

    if parsed_url.port and default_ports.get(parsed_url.scheme) != parsed_url.port:
        host += ":" + str(parsed_url.port)

    return host


class RequestsInstrumentation(AbstractInstrumentedModule):
    name = "requests"

    instrument_list = [("requests.sessions", "Session.send")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        if "request" in kwargs:
            request = kwargs["request"]
        else:
            request = args[0]

        signature = request.method.upper()
        signature += " " + get_host_from_url(request.url)

        extra_data = {
            "wrapped_method": "Execute",
            "provider": self.name,
            "type": "Web External",
            "sub_type": "send",
            "request_method": request.method,
            "url": request.url,
        }

        with CaptureSpan(signature, "ext.http.requests", extra_data, leaf=True, is_async=is_async_span()) as span:
            request = wrapped(*args, **kwargs)

            if not isinstance(span, DroppedSpan):
                span.context['status_code'] = request.status_code

                transaction = get_transaction()
                transaction.update_span_context(span.id, span.context)

            return request
