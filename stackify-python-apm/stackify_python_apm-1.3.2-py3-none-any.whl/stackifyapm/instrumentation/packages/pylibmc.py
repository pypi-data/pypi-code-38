from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import compat, get_method_name
from stackifyapm.utils.helper import is_async_span


class PyLibMcInstrumentation(AbstractInstrumentedModule):
    name = "pylibmc"

    instrument_list = [
        ("pylibmc", "Client.get"),
        ("pylibmc", "Client.get_multi"),
        ("pylibmc", "Client.set"),
        ("pylibmc", "Client.set_multi"),
        ("pylibmc", "Client.add"),
        ("pylibmc", "Client.replace"),
        ("pylibmc", "Client.append"),
        ("pylibmc", "Client.prepend"),
        ("pylibmc", "Client.incr"),
        ("pylibmc", "Client.decr"),
        ("pylibmc", "Client.gets"),
        ("pylibmc", "Client.cas"),
        ("pylibmc", "Client.delete"),
        ("pylibmc", "Client.delete_multi"),
        ("pylibmc", "Client.touch"),
        ("pylibmc", "Client.get_stats"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        wrapped_name = self.get_wrapped_name(wrapped, instance, method)

        extra_data = {
            "wrapped_method": 'execute',
            "provider": self.name,
            "type": "Cache",
            "sub_type": "cache",
            "operation": get_method_name(method),
        }
        cache_name = args and args[0] or None
        if cache_name:
            if isinstance(cache_name, compat.string_types):
                extra_data['cache_name'] = cache_name
                extra_data['cache_key'] = cache_name.split(':')[-1]
            elif isinstance(cache_name, compat.list_type):
                extra_data['cache_name'] = cache_name
                extra_data['cache_key'] = [name.split(':')[-1] for name in cache_name]
            elif isinstance(cache_name, compat.dict_type):
                extra_data['cache_name'] = list(cache_name.keys())
                extra_data['cache_key'] = [name.split(':')[-1] for name in cache_name.keys()]
            else:
                extra_data['cache_key'] = cache_name

        with CaptureSpan(wrapped_name, "cache.memcached", extra_data, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
