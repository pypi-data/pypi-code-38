import os
import re
import time
import hashlib
import time
import logging

from functools import wraps
from django.core.cache import cache
from django.utils.encoding import force_bytes, iri_to_uri
from django.utils import six
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def _to_bytestring(value):
    """
    Encode a string as a UTF8 bytestring.  This function could be passed a
    bytestring or unicode string so must distinguish between the two.
    """
    if isinstance(value, six.text_type):
        return value.encode('utf8')
    if isinstance(value, six.binary_type):
        return value
    if six.PY2:
        return str(value)
    return bytes(str(value), 'utf8')


def _hash(value):
    """
    Generate a hash of the given tuple.
    This is for use in a cache key.
    """
    if isinstance(value, tuple):
        value = tuple(_to_bytestring(v) for v in value)
    return hashlib.md5(six.b(':').join(value)).hexdigest()


def _generate_cache_key(prefix, fn, *args, **kwargs):
    """
    Cache key pattern:
        '@cache_fn.<prefix>.<fn_name>.[<hash(url)> | <hash(args&kwargs)>]'

    1. If the arguments contains WSGIRequest,
        we generate unique key by request arguments with GET  **not** POST!
    2. Otherwise we generate the unique key by all arguments.
    """
    cache_key = '@cache_fn.'
    if prefix:
        cache_key = cache_key + prefix
    cache_key = cache_key + "." + fn.__name__
    if args:
        is_request = False
        for k in args:
            if isinstance(k, (WSGIRequest)):
                url = hashlib.md5(
                    force_bytes(
                        iri_to_uri(
                            k.build_absolute_uri()))).hexdigest()
                cache_key = cache_key + "." + url
                is_request = True
                break
        if not is_request:
            # FIXME:Generate key exclude "SimpleLazyObject"
            cache_key = cache_key + "." + _hash(args)
    if kwargs:
        cache_key = cache_key + "." + \
            _hash(tuple([k for k in sorted(kwargs)])) + _hash(tuple([kwargs[k] for k in sorted(kwargs)]))

    return cache_key


MEMCACHE_MAX_EXPIRATION = 86400  # 1days


def cache_fn(timeout=1, prefix=None, cache_ttl=MEMCACHE_MAX_EXPIRATION):
    """
    Retrieve data from cache if cacheable and no-stale,
    otherise refresh synchronously and cache it.
    * timeout: The stale timeout which would be handled in the decorator.
    * prefix: The prefix of cache key.
    * cache_ttl: The TTL(time to live) of key in memcache.
    NOTE: For HttpResponse, we just cache the response whose status code is 200.
    """
    def cache_set(key, data):
        cache.set(key, (time.time() + timeout, data), cache_ttl)

    def _method(fn):
        def __w(*args, **kw):
            key = _generate_cache_key(prefix, fn, *args, **kw)
            item = cache.get(key)
            if item is None:
                logger.debug("Not Found data in cache, refresh synchronously")
                res = fn(*args, **kw)
                if isinstance(res, HttpResponse):
                    # XXX:Skip to cache the res whose code is not 200
                    if res.status_code == 200:
                        cache_set(key, res)
                else:
                    cache_set(key, res)
                return res
            else:
                expire, data = item
                delta = time.time() - expire
                if delta < 0:
                    logger.debug("Cache HIT")
                    return data
                else:
                    logger.debug("Stale Cache HIT, refresh synchronously")
                    # Return the stale data for another request cocurrently.
                    cache_set(key, data)
                    res = fn(*args, **kw)
                    # Updating the new data blockly
                    cache_set(key, res)
                    return res
        return __w
    return _method
