from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import get_transaction
from stackifyapm.utils import default_ports
from stackifyapm.utils.helper import is_async_span


class Urllib3Instrumentation(AbstractInstrumentedModule):
    name = "urllib3"

    instrument_list = [
        ("urllib3.connectionpool", "HTTPConnectionPool.urlopen"),
        ("requests.packages.urllib3.connectionpool", "HTTPConnectionPool.urlopen"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        if "method" in kwargs:
            method = kwargs["method"]
        else:
            method = args[0]

        host = instance.host

        if instance.port != default_ports.get(instance.scheme):
            host += ":" + str(instance.port)

        if "url" in kwargs:
            url = kwargs["url"]
        else:
            url = args[1]

        signature = method.upper() + " " + host

        url = instance.scheme + "://" + host + url
        extra_data = {
            "wrapped_method": "Execute",
            "provider": self.name,
            "type": "Web External",
            "sub_type": "send",
            "url": url,
            "request_method": method.upper(),
        }

        with CaptureSpan(signature, "ext.http.urllib3", extra_data, leaf=True, is_async=is_async_span()) as span:
            leaf_span = span
            while isinstance(leaf_span, DroppedSpan):
                leaf_span = leaf_span.parent

            request = wrapped(*args, **kwargs)
            if not isinstance(span, DroppedSpan):
                span.context['status_code'] = request.status

                transaction = get_transaction()
                transaction.update_span_context(span.id, span.context)

            return request
