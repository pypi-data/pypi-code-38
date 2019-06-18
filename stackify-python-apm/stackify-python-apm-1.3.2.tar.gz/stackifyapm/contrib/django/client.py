from __future__ import absolute_import

import logging

import django
from django.conf import settings as django_settings
from django.core.exceptions import DisallowedHost

from stackifyapm.base import Client
from stackifyapm.conf import constants
from stackifyapm.utils import compat, get_url_data
from stackifyapm.utils.module_import import import_string
from stackifyapm.utils.wsgi import get_environ, get_headers

__all__ = ("DjangoClient",)


default_client_class = "stackifyapm.contrib.django.DjangoClient"
_client = (None, None)


def get_client(client=None):
    global _client

    tmp_client = client is not None
    if not tmp_client:
        client = default_client_class

    if _client[0] != client:
        client_class = import_string(client)
        instance = client_class()
        if not tmp_client:
            _client = (client, instance)
        return instance

    return _client[1]


class DjangoClient(Client):
    logger = logging.getLogger("stackifyapm.errors.client.django")

    def __init__(self, config=None, **inline):
        config = config or {}
        config["ENVIRONMENT"] = (
            config.get("ENV") or
            config.get("ENVIRONMENT") or
            (hasattr(django_settings, 'ENV') and django_settings.ENV) or
            (hasattr(django_settings, 'ENVIRONMENT') and django_settings.ENVIRONMENT) or
            'Production'
        )
        config["APPLICATION_NAME"] = (
            config.get('APPLICATION_NAME') or
            (hasattr(django_settings, 'APP_NAME') and django_settings.APP_NAME) or
            (hasattr(django_settings, 'APPLICATION_NAME') and django_settings.APPLICATION_NAME) or
            'Python Application'
        )
        config["BASE_DIR"] = config.get('BASE_DIR') or django_settings.BASE_DIR
        config["CONFIG_FILE"] = (
            config.get('CONFIG_FILE') or
            (hasattr(django_settings, 'CONFIG_FILE') and django_settings.CONFIG_FILE) or
            'stackify.json'
        )

        if "framework_name" not in inline:
            inline["framework_name"] = "django"
            inline["framework_version"] = django.get_version()

        super(DjangoClient, self).__init__(config, **inline)

    def get_data_from_request(self, request, capture_body=False):
        result = {
            "env": dict(get_environ(request.META)),
            "headers": dict(get_headers(request.META)),
            "method": request.method,
            "socket": {"remote_address": request.META.get("REMOTE_ADDR"), "encrypted": request.is_secure()},
            "cookies": dict(request.COOKIES),
        }

        if request.method in constants.HTTP_WITH_BODY:
            content_type = request.META.get("CONTENT_TYPE")
            if content_type == "application/x-www-form-urlencoded":
                data = compat.multidict_to_dict(request.POST)
            elif content_type and content_type.startswith("multipart/form-data"):
                data = compat.multidict_to_dict(request.POST)
                if request.FILES:
                    data["_files"] = {field: file.name for field, file in compat.iteritems(request.FILES)}
            else:
                try:
                    data = request.body
                except Exception:
                    data = "<unavailable>"

            result["body"] = data if (capture_body or not data) else "[REDACTED]"

        if hasattr(request, "get_raw_uri"):
            url = request.get_raw_uri()
        else:
            try:
                url = request.build_absolute_uri()
            except DisallowedHost:
                result["url"] = {"full": "DisallowedHost"}
                url = None
        if url:
            result["url"] = get_url_data(url)
        return result

    def get_data_from_response(self, response):
        result = {"status_code": response.status_code}

        if hasattr(response, "items"):
            result["headers"] = dict(response.items())
        return result


class ProxyClient(object):
    __members__ = property(lambda x: x.__dir__())
    __class__ = property(lambda x: get_client().__class__)
    __dict__ = property(lambda o: get_client().__dict__)
    __repr__ = lambda: repr(get_client())  # noqa
    __getattr__ = lambda x, o: getattr(get_client(), o)  # noqa
    __setattr__ = lambda x, o, v: setattr(get_client(), o, v)  # noqa
    __delattr__ = lambda x, o: delattr(get_client(), o)  # noqa
    __lt__ = lambda x, o: get_client() < o  # noqa
    __le__ = lambda x, o: get_client() <= o  # noqa
    __eq__ = lambda x, o: get_client() == o  # noqa
    __ne__ = lambda x, o: get_client() != o  # noqa
    __gt__ = lambda x, o: get_client() > o  # noqa
    __ge__ = lambda x, o: get_client() >= o  # noqa

    if compat.PY2:
        __cmp__ = lambda x, o: cmp(get_client(), o)  # noqa F821

    __hash__ = lambda x: hash(get_client())  # noqa
    __nonzero__ = lambda x: bool(get_client())  # noqa
    __len__ = lambda x: len(get_client())  # noqa
    __getitem__ = lambda x, i: get_client()[i]  # noqa
    __iter__ = lambda x: iter(get_client())  # noqa
    __contains__ = lambda x, i: i in get_client()  # noqa
    __getslice__ = lambda x, i, j: get_client()[i:j]  # noqa
    __add__ = lambda x, o: get_client() + o  # noqa
    __sub__ = lambda x, o: get_client() - o  # noqa
    __mul__ = lambda x, o: get_client() * o  # noqa
    __floordiv__ = lambda x, o: get_client() // o  # noqa
    __mod__ = lambda x, o: get_client() % o  # noqa
    __divmod__ = lambda x, o: get_client().__divmod__(o)  # noqa
    __pow__ = lambda x, o: get_client() ** o  # noqa
    __lshift__ = lambda x, o: get_client() << o  # noqa
    __rshift__ = lambda x, o: get_client() >> o  # noqa
    __and__ = lambda x, o: get_client() & o  # noqa
    __xor__ = lambda x, o: get_client() ^ o  # noqa
    __or__ = lambda x, o: get_client() | o  # noqa
    __div__ = lambda x, o: get_client().__div__(o)  # noqa
    __truediv__ = lambda x, o: get_client().__truediv__(o)  # noqa
    __neg__ = lambda x: -(get_client())  # noqa
    __pos__ = lambda x: +(get_client())  # noqa
    __abs__ = lambda x: abs(get_client())  # noqa
    __invert__ = lambda x: ~(get_client())  # noqa
    __complex__ = lambda x: complex(get_client())  # noqa
    __int__ = lambda x: int(get_client())  # noqa

    if compat.PY2:
        __long__ = lambda x: long(get_client())  # noqa F821

    __float__ = lambda x: float(get_client())  # noqa
    __str__ = lambda x: str(get_client())  # noqa
    __unicode__ = lambda x: compat.text_type(get_client())  # noqa
    __oct__ = lambda x: oct(get_client())  # noqa
    __hex__ = lambda x: hex(get_client())  # noqa
    __index__ = lambda x: get_client().__index__()  # noqa
    __coerce__ = lambda x, o: x.__coerce__(x, o)  # noqa
    __enter__ = lambda x: x.__enter__()  # noqa
    __exit__ = lambda x, *a, **kw: x.__exit__(*a, **kw)  # noqa


client = ProxyClient()
