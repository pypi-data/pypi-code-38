from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import get_transaction
from stackifyapm.utils.helper import is_async_span


class Urllib2Instrumentation(AbstractInstrumentedModule):
    name = "urllib2"

    instrument_list = [
        ("urllib2", "urlopen"),
        ("urllib2.request", "urlopen"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        url = args[0]
        signature = method.upper() + " " + url
        extra_data = {
            "wrapped_method": "Execute",
            "provider": self.name,
            "type": "Web External",
            "sub_type": "send",
            "url": url,
        }

        with CaptureSpan(signature, "ext.http.urllib2", extra_data, leaf=True, is_async=is_async_span()) as span:
            request = wrapped(*args, **kwargs)

            if not isinstance(span, DroppedSpan):
                span.context['status_code'] = request.code
                if hasattr(request, '_method'):
                    span.context['request_method'] = request._method

                transaction = get_transaction()
                transaction.update_span_context(span.id, span.context)

            return request
