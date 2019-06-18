from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import get_method_name
from stackifyapm.utils.helper import is_async_span


class PythonMemcachedInstrumentation(AbstractInstrumentedModule):
    name = "python_memcached"

    memcached_method_list = [
        "add",
        "append",
        "cas",
        "decr",
        "delete",
        "delete_multi",
        "disconnect_all",
        "flush_all",
        "get",
        "get_multi",
        "get_slabs",
        "get_stats",
        "gets",
        "incr",
        "prepend",
        "replace",
        "set",
        "set_multi",
        "touch",
    ]

    def get_instrument_list(self):
        method_list = [("memcache", "Client.{}".format(method)) for method in self.memcached_method_list]
        method_list += [("pymemcache.client.base", "Client.{}".format(method)) for method in self.memcached_method_list]
        return method_list

    def call(self, module, method, wrapped, instance, args, kwargs):
        name = self.get_wrapped_name(wrapped, instance, method)
        method_name = get_method_name(method)
        extra_data = {
            "wrapped_method": "execute",
            "provider": self.name,
            "type": "Cache",
            "sub_type": "cache",
            "operation": method_name,
        }
        cache_name = args and args[0] or None
        if cache_name:
            extra_data['cache_key'] = cache_name

        with CaptureSpan(name, "cache.memcached", extra_data, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
