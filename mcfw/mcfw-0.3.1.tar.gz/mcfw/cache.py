# -*- coding: utf-8 -*-
# Copyright 2018 Mobicage NV
# NOTICE: THIS FILE HAS BEEN MODIFIED BY MOBICAGE NV IN ACCORDANCE WITH THE APACHE LICENSE VERSION 2.0
# Copyright 2018 GIG Technology NV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @@license_version:1.5@@

import base64
import hashlib
import logging
import threading
import time
from collections import defaultdict
from functools import wraps
try:
    from google.appengine.api import memcache as mod_memcache
    from google.appengine.ext import ndb
    __GAE__ = True
except ImportError:  # Allow running outside google app engine
    __GAE__ = False

from mcfw.consts import MISSING
from mcfw.serialization import serializer, s_bool, get_serializer, s_any, deserializer, get_deserializer, ds_bool, \
    ds_any, SerializedObjectOutOfDateException, get_list_serializer, List

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

CACHE_ATTR = u'cache_key'


class CachedModelMixIn(object):
    on_trans_committed = None

    def _trigger_invalidate_cache(self):
        def invalidate_cache():
            self.invalidateCache()
            logging.info('%s: Cache invalidated', self.__class__.__name__)

        if ndb.in_transaction() and self.on_trans_committed:
            self.on_trans_committed(invalidate_cache)
        else:
            invalidate_cache()

    def put(self):
        super(CachedModelMixIn, self).put()
        self._trigger_invalidate_cache()

    def delete(self):
        super(CachedModelMixIn, self).delete()
        self._trigger_invalidate_cache()


class _TLocal(threading.local):
    def __init__(self):
        self.request_cache = dict()


_tlocal = _TLocal()
del _TLocal


def get_from_request_cache(key):
    return _tlocal.request_cache.get(key, MISSING)


def add_to_request_cache(key, success, value):
    _tlocal.request_cache[key] = (success, value)


def flush_request_cache():
    _tlocal.request_cache.clear()


def set_cache_key(wrapped, f):
    def key():
        if hasattr(f, 'meta') and CACHE_ATTR in f.meta:
            return f.meta[CACHE_ATTR]
        else:
            return '%s.%s' % (f.__name__, f.__module__)

    if not hasattr(wrapped, 'meta'):
        wrapped.meta = {CACHE_ATTR: key()}
        return
    if CACHE_ATTR not in wrapped.meta:
        wrapped.meta[CACHE_ATTR] = key()


def ds_key(version, cache_key):
    return '%s-%s' % (version, hashlib.sha256(cache_key).hexdigest())


if __GAE__:
    class DSCache(ndb.Model):
        creation_timestamp = ndb.IntegerProperty()
        description = ndb.StringProperty(indexed=False)
        value = ndb.BlobProperty()

        @property
        def ds_key(self):
            return self.key.id()

        @classmethod
        def create_key(cls, ds_key):
            return ndb.Key(cls, ds_key)


def invalidate_cache(f, *args, **kwargs):
    f.invalidate_cache(*args, **kwargs)


cache_key_locks = defaultdict(lambda: threading.RLock())


def cached(version, lifetime=600, request=True, memcache=True, key=None, datastore=None):
    """
    Caches the result of the decorated function and returns the cached version if it exists.

    Args:
        version (long):  Cache version, needs to bumped every time the arguments of the cached function change
        lifetime (long): Number of seconds the cached entry remains in memcache after it was created.
        request(bool): Whether it needs to be cached in memory for the current request processing.
        memcache (bool): Whether it needs to be cached in memcache.
        key (str): Function to create cache_key
        datastore (str): Content description of cache object in datastore. Leave none to ommit the datastore cache.

    Raises:
        ValueError: if neither request nor memcache are True
        ValueError: If datastore caching is used but lifetime is not set to 0
    """

    if not request and not memcache and not datastore:
        raise ValueError('Either request or memcache or datastore needs to be True')

    if datastore and lifetime != 0:
        raise ValueError('If datastore caching is used, values other than 0 for lifetime are not permitted.')

    def wrap(f):
        base_cache_key = f.meta[CACHE_ATTR]
        if base_cache_key == 'inner_wrapper.google.appengine.api.datastore':
            raise ValueError('Move @db.non_transactional inside the @cached method')
        f_args = f.meta['fargs']
        f_ret = f.meta['return_type']
        f_pure_default_args_dict = f.meta['pure_default_args_dict']

        if isinstance(f_ret, list):
            f_ret = List(f_ret[0])
        if memcache or datastore:
            result_serializer = get_serializer(f_ret)
            result_deserializer = get_deserializer(f_ret)
        key_function = key
        if not key_function:
            def key_(kwargs):
                stream = StringIO()
                stream.write(base_cache_key)
                kwargt = f.meta['kwarg_types']
                for a in sorted(kwargt.keys()):
                    if a in kwargs:
                        effective_value = kwargs[a]
                    else:
                        effective_value = f_pure_default_args_dict[a]
                    if isinstance(kwargt[a], list):
                        get_list_serializer(get_serializer(kwargt[a][0]))(stream, effective_value)
                    else:
                        get_serializer(kwargt[a])(stream, effective_value)
                return stream.getvalue()

            key_function = key_

        @serializer
        def serialize_result(stream, obj):
            s_bool(stream, obj[0])
            if obj[0]:
                result_serializer(stream, obj[1])
            else:
                s_any(stream, obj[1])

        f.serializer = serialize_result

        @deserializer
        def deserialize_result(stream):
            success = ds_bool(stream)
            if success:
                result = result_deserializer(stream)
            else:
                result = ds_any(stream)
            return success, result

        f.deserializer = deserialize_result

        def cache_key(*args, **kwargs):
            kwargs_ = dict(kwargs)
            kwargs_.update(dict(((f_args[0][i], args[i]) for i in xrange(len(args)))))
            return 'v%s.%s' % (version, base64.b64encode(key_function(kwargs_)))

        f.cache_key = cache_key

        def invalidate_cache(*args, **kwargs):
            ck = cache_key(*args, **kwargs)
            with cache_key_locks[ck]:
                if datastore:
                    @ndb.non_transactional
                    def clear_dscache():
                        DSCache.create_key(ds_key(version, ck)).delete()

                    clear_dscache()
                if memcache:
                    attempt = 1
                    while not mod_memcache.delete(ck):  # @UndefinedVariable
                        if attempt >= 3:
                            logging.critical('MEMCACHE FAILURE !!! COULD NOT INVALIDATE CACHE !!!')
                            raise RuntimeError('Could not invalidate memcache!')
                        logging.debug('Memcache failure. Retrying to invalidate cache.')
                        time.sleep(0.25 * attempt)
                        attempt += 1

                if request and ck in _tlocal.request_cache:
                    del _tlocal.request_cache[ck]

        f.invalidate_cache = invalidate_cache

        @wraps(f)
        def wrapped(*args, **kwargs):
            if ndb.in_transaction():
                return f(*args, **kwargs)
            ck = cache_key(*args, **kwargs)
            with cache_key_locks[ck]:
                if request and ck in _tlocal.request_cache:
                    success, result = _tlocal.request_cache[ck]
                    if success:
                        return result
                if memcache:
                    memcache_result = mod_memcache.get(ck)  # @UndefinedVariable
                    if memcache_result:
                        buf = StringIO(memcache_result)
                        try:
                            success, result = deserialize_result(buf)
                            if request:
                                _tlocal.request_cache[ck] = (success, result)
                            if success:
                                return result
                        except SerializedObjectOutOfDateException:
                            pass
                if datastore:
                    @ndb.non_transactional
                    def get_from_dscache():
                        ds_cache = DSCache.create_key(ds_key(version, ck)).get()
                        if ds_cache:
                            buf = StringIO(str(ds_cache.value))
                            try:
                                success, result = deserialize_result(buf)
                                if request:
                                    _tlocal.request_cache[ck] = (success, result)
                                if memcache:
                                    mod_memcache.set(ck, ds_cache.value, time=lifetime)  # @UndefinedVariable
                                if success:
                                    return True, result
                            except SerializedObjectOutOfDateException:
                                pass
                        return False, None

                    cached, result = get_from_dscache()
                    if cached:
                        return result

                cache_value = None
                try:
                    result = f(*args, **kwargs)
                    cache_value = (True, result)
                    return result
                except Exception as e:
                    cache_value = (False, e)
                    raise
                finally:
                    if cache_value and cache_value[0]:
                        if datastore or memcache:
                            buf = StringIO()
                            serialize_result(buf, cache_value)
                            serialized_cache_value = buf.getvalue()
                        if datastore:
                            @ndb.non_transactional
                            def update_dscache():
                                dsm = DSCache(key=DSCache.create_key(ds_key(version, ck)))
                                dsm.description = datastore
                                dsm.creation_timestamp = int(time.time())
                                dsm.value = serialized_cache_value
                                dsm.put()

                            update_dscache()
                        if memcache:
                            mod_memcache.set(ck, serialized_cache_value, time=lifetime)  # @UndefinedVariable
                        if request:
                            _tlocal.request_cache[ck] = cache_value

        return wrapped

    return wrap
