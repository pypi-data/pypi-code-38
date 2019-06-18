from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils.helper import is_async_span


class ZLibInstrumentation(AbstractInstrumentedModule):
    name = 'zlib'

    instrument_list = [("zlib", "compress"), ("zlib", "decompress")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        wrapped_name = module + "." + method
        extra_data = {
            "provider": self.name,
            "type": "Compression",
            "sub_type": "compression",
            "operation": method,
        }

        with CaptureSpan(wrapped_name, "compression.zlib", extra_data, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
