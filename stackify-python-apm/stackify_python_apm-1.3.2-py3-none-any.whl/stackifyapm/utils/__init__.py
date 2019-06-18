from functools import partial

from stackifyapm.utils import compat, encoding

try:
    from functools import partialmethod
    partial_types = (partial, partialmethod)
except ImportError:
    partial_types = (partial,)


default_ports = {"https": 433, "http": 80, "postgresql": 5432}


def get_name_from_path(path):
    if path.startswith('/'):
        return path[1:]
    return path


def get_name_from_func(func):
    if isinstance(func, partial_types):
        return "partial({})".format(get_name_from_func(func.func))
    elif hasattr(func, "_partialmethod") and hasattr(func._partialmethod, "func"):
        return "partial({})".format(get_name_from_func(func._partialmethod.func))

    module = func.__module__

    if hasattr(func, "__name__"):
        view_name = func.__name__
    else:
        view_name = func.__class__.__name__

    return "{0}.{1}".format(module, view_name)


def build_name_with_http_method_prefix(name, request):
    return " ".join((request.method, name)) if name else name


def get_url_data(url):
    scheme, netloc, path, params, query, fragment = compat.urlparse.urlparse(url)

    if ":" in netloc:
        hostname, port = netloc.split(":")
    else:
        hostname, port = (netloc, None)

    url_data = {
        "full": encoding.keyword_field(url),
        "protocol": scheme + ":",
        "hostname": encoding.keyword_field(hostname),
        "pathname": encoding.keyword_field(path),
    }
    if port:
        url_data["port"] = port

    if query:
        url_data["search"] = encoding.keyword_field("?" + query)

    return url_data


def get_method_name(method):
    method_name = str(method) if isinstance(method, compat.string_types) else method.__name__
    return method_name.split('.')[-1]


def get_class_name_or_None(method):
    if hasattr(method, '__qualname__') and '.' in method.__qualname__:
        return method.__qualname__.split('.')[0]
    elif hasattr(method, 'im_class'):
        return method.im_class.__name__

    return None
