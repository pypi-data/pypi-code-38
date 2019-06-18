from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import get_transaction
from stackifyapm.utils.compat import urlparse
from stackifyapm.utils.helper import is_async_span


class BotocoreInstrumentation(AbstractInstrumentedModule):
    name = "botocore"

    instrument_list = [("botocore.client", "BaseClient._make_api_call")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        if "operation_name" in kwargs:
            operation_name = kwargs["operation_name"]
        else:
            operation_name = args[0]

        target_endpoint = instance._endpoint.host
        parsed_url = urlparse.urlparse(target_endpoint)
        if "." in parsed_url.hostname:
            service, region = parsed_url.hostname.split(".", 2)[:2]
        else:
            service, region = parsed_url.hostname, None

        signature = "{}:{}".format(service, operation_name)
        extra_data = {
            "wrapped_method": 'Execute',
            "provider": self.name,
            "type": "Http",
            "sub_type": "send",
            "service": service,
            "region": region,
            "operation": operation_name,
            "url": instance.meta.endpoint_url,
        }

        with CaptureSpan(signature, "ext.http.aws", extra_data, leaf=True, is_async=is_async_span()) as span:
            request = wrapped(*args, **kwargs)

            if not isinstance(span, DroppedSpan):
                span.context['status_code'] = request.get('ResponseMetadata', {}).get('HTTPStatusCode', 500)

                transaction = get_transaction()
                transaction.update_span_context(span.id, span.context)

            return request
