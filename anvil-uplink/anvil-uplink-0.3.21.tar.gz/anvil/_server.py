# Helpers for implementing anvil.server.
# Used in uplink, downlink and pypy-sandbox.
import importlib

import anvil
import traceback
import numbers
import sys
import re
import json
import math

_do_call = None

string_type = str if sys.version_info >= (3,) else basestring
long_type = int if sys.version_info >= (3,) else long

POS_INFINITY = float("inf")
NEG_INFINITY = float("-inf")

_value_types = {}

class LiveObjectProxy(anvil.LiveObject):

    def __init__(self,spec,known_methods=None):
        for k in ["itemCache", "iterItems"]:
            if spec.get(k, {}) is None:
                del spec[k]

        if known_methods is not None:
            if spec.get("methods") is None:
                spec["methods"] = known_methods[spec["backend"]]
            else:
                known_methods[spec["backend"]] = spec["methods"]
        anvil.LiveObject.__init__(self, spec)

    def __getattr__(self, item):
        if item in self._spec["methods"]:
            def item_fn(*args, **kwargs):
                return _do_call(args, kwargs, fn_name=item, live_object=self)

            return item_fn
        else:
            raise AttributeError(item)

    def __getitem__(self, item):

        if "__anvil_iter_page__" in self._spec["methods"]:
            if isinstance(item, (int,long_type)):
                if item < 0:
                    raise IndexError("list index cannot be negative")

                iter = LiveObjectProxy.Iter(self, item)
                try:
                    return iter.next()
                except StopIteration:
                    raise IndexError("list index out of range")
            elif isinstance(item, slice):
                if (item.start and item.start < 0) or (item.stop and item.stop < 0) or (item.step and item.step < 0):
                    raise Exception("list slice indices and step cannot be negative")
                return LiveObjectProxy.Iter(self, item.start, item.stop, item.step)


        if item in self._spec.get("itemCache", {}):
            return self._spec["itemCache"][item]

        getitem = self.__getattr__("__getitem__")

        try:
            return getitem(item)
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

    def __setitem__(self, key, value):
        if key in self._spec.get("itemCache", {}):
            del self._spec["itemCache"][key]

        setitem = self.__getattr__("__setitem__")
        try:
            r = setitem(key, value)
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

        if "itemCache" in self._spec and (isinstance(value, string_type) or isinstance(value, numbers.Number) or isinstance(value, bool) or value is None):
            self._spec["itemCache"][key] = value

        return r

    class Iter:
        def __init__(self, live_object, start=None, stop=None, step=None):
            self._live_object = live_object

            i = live_object._spec.get("iterItems", {})
            self._idx = start if start is not None else 0
            self._items = i.get("items", None)
            self._next_page = i.get("nextPage", None)
            self._stop = stop
            self._step = step if step is not None else 1

        def _fetch_state(self):
            r = _do_call([self._next_page], {}, fn_name="__anvil_iter_page__", live_object=self._live_object)
            self._items = r["items"]
            self._next_page = r.get("nextPage", None)

        def __iter__(self):
            return self

        def next(self):
            if self._items is None:
                try:
                    self._fetch_state()
                except AnvilWrappedError as e:
                    raise _deserialise_exception(e.error_obj)

            if self._idx < len(self._items) and (self._stop is None or self._idx < self._stop):
                r = self._items[self._idx]
                self._idx += self._step
                return r

            if self._next_page is None or (self._stop is not None and self._idx >= self._stop):
                raise StopIteration

            self._idx -= len(self._items) if self._items is not None else self._idx
            if self._stop is not None:
                self._stop -= len(self._items) if self._items is not None else 0
            self._items = None
            return self.next()

        def __next__(self):
            return self.next()

    def __iter__(self):
        if "__anvil_iter_page__" in self._spec["methods"]:
            return LiveObjectProxy.Iter(self)
        else:
            raise Exception("Not iterable: <LiveObject: %s>" % self._spec.get("backend", "INVALID"))

    def __bool__(self):
        if "__nonzero__" in self._spec["methods"]:
            return self.__getattr__("__nonzero__")()
        else:
            return True

    __nonzero__ = __bool__

    def __len__(self):
        if "__len__" in self._spec["methods"]:
            return int(self.__getattr__("__len__")())
        else:
            l = 0
            for _ in self.__iter__():
                l += 1
            return l


class Capability(object):
    def __init__(self, scope, mac=None, narrow=None):
        self._scope = scope
        self._mac = mac
        if mac is None and (len(scope) == 0 or scope[0] == "_"):
            raise Exception("To construct a Capability from scratch, its scope cannot start with ['_']")
        self._narrow = narrow or []

    @property
    def scope(self):
        return self._scope + self._narrow

    def narrow(self, narrowing_suffix):
        return Capability(self._scope, self._mac, self._narrow + narrowing_suffix)

    @staticmethod
    def require(cap, scope):
        cap_scope = cap.scope
        if not isinstance(cap, Capability) or len(cap_scope) > len(scope):
            raise Exception("Not a capability: %s" % cap)
        for i in range(len(cap_scope)):
            if scope[i] != cap_scope[i]:
                raise Exception("Invalid capability for this action")

    def __repr__(self):
        try:
            return "<anvil.server.Capability:[%s]>" % (",".join((str(x) for x in self.scope)))
        except:
            return "<anvil.server.Capability:INVALID:%s>" % repr(self.scope)


class Serializable(object):
    SERIALIZATION_NAME = None

    def __serialize__(self, global_data):
        return self.__dict__

    @classmethod
    def __deserialize__(cls, from_data, global_data):
        obj = cls.__new__(cls)
        obj.__dict__.update(from_data)
        return obj


def serializable_type(cls, name=None):
    if not issubclass(cls, Serializable):
        raise Exception("%s is not a subclass of anvil.server.Serializable" % str(cls))
    if name is None:
        name = cls.__module__ + "." + cls.__name__
    _value_types[name] = cls
    cls.SERIALIZATION_NAME = name
    return cls


class LazyMedia(anvil.Media):
    def __init__(self, spec):
        if isinstance(spec,LazyMedia):
            spec = spec._spec
        self._spec = spec
        self._details = None
        self._fetched = None

    def _fetch(self):
        if self._details is None:
            import anvil.server
            self._fetched = anvil.server.call("anvil.private.fetch_lazy_media", self._spec)
        return self._fetched

    def _get(self, key, attr=None):
        if attr is None:
            attr = key
        return self._spec[key] if key in self._spec else getattr(self._fetch(), attr)

    def get_name(self):
        try:
            return self._get("name")
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

    def get_url(self, is_download=True):
        return anvil.server.call("anvil.private.get_lazy_media_url", self, is_download)

    def get_content_type(self):
        try:
            return self._get("mime-type", "content_type")
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

    def get_length(self):
        try:
            return self._get("length")
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

    def get_bytes(self):
        try:
            return self._fetch().get_bytes()
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)


class AnvilWrappedError(Exception):
    registered_type_name = None

    def __init__(self, error_obj):
        if isinstance(error_obj, dict):
            self.manually_created = False
            self.error_obj = error_obj
        else:
            self.manually_created = True
            self.error_obj = {'message': str(error_obj), 'trace': []}
            t =  type(self).registered_type_name
            if t is not None:
                self.error_obj['type'] = t
        self.message = self.error_obj.get("message", "")
        Exception.__init__(self, self.message)

    def __str__(self):
        eo_type = self.error_obj.get("type")
        if type(self) is AnvilWrappedError and eo_type is not None:
            return str(eo_type) + ": " + repr(self.message)
        return repr(self.message)


_named_exceptions = {
    "KeyError": lambda error_obj: KeyError(error_obj['message'])
}


def _register_exception_type(name, cls):
    _named_exceptions[name] = cls
    cls.registered_type_name = name


def _deserialise_exception(error_obj):
    return _named_exceptions.get(error_obj.get("type"), AnvilWrappedError)(error_obj)


def get_liveobject_cache_filter_spec(input_data):
    """Returns a specification of a filter for LiveObject cache updates, which passes only LiveObjects present in input_data"""
    spec = {}

    def f(data):
        if isinstance(data, list):
            for i in data: f(i)
        elif isinstance(data, dict):
            for k,v in data.items(): f(v)
        elif isinstance(data, LiveObjectProxy):
            b = spec.get(data._spec["backend"])
            if b is None:
                b = spec[data._spec["backend"]] = set()
            b.add(data._spec["id"])

    f(input_data)
    return spec


def combine_cache_updates(updates, new_updates, filter_spec):
    if updates is None:
        updates = {}

    for k in new_updates:
        permitted_ids = filter_spec.get(k)
        if permitted_ids is None:
            continue
        caches = updates.get(k)
        if caches is None:
            caches = updates[k] = dict()
        for id in new_updates[k]:
            if id not in permitted_ids:
                continue
            caches[id] = new_updates[k][id]


def apply_cache_updates(cache_updates, objects_to_walk):
    """Recursively walk an object tree, applying cache updates wherever necessary"""

    def f(data):
        if isinstance(data, list):
            for i in data: f(i)
        elif isinstance(data, dict):
            for k,v in data.items(): f(v)
        elif isinstance(data, LiveObjectProxy):
            update = cache_updates.get(data._spec["backend"], {})
            if data._spec["id"] in update:
                data._spec["itemCache"] = update[data._spec["id"]]

    f(objects_to_walk)


class MaybeWrappedError(Exception):
    def __init__(self, error_obj):
        if isinstance(error_obj, dict):
            Exception.__init__(self, error_obj["message"])
        else:
            Exception.__init__(self, error_obj)


class SerializationError(MaybeWrappedError):
    pass


class InternalError(MaybeWrappedError):
    pass


class InvalidResponseError(MaybeWrappedError):
    pass


class RuntimeUnavailableError(MaybeWrappedError):
    pass


class UplinkDisconnectedError(MaybeWrappedError):
    pass


class ExecutionTerminatedError(MaybeWrappedError):
    pass


class TimeoutError(MaybeWrappedError):
    pass


class QuotaExceededError(MaybeWrappedError):
    pass


class NoServerFunctionError(AnvilWrappedError):
    pass


class CookieError(AnvilWrappedError):
    pass


class _FailError(MaybeWrappedError):
    pass


class BackgroundTaskError(MaybeWrappedError):
    pass


class BackgroundTaskNotFound(MaybeWrappedError):
    pass


class BackgroundTaskKilled(MaybeWrappedError):
    pass




_register_exception_type("anvil.server.SerializationError", SerializationError)
_register_exception_type("anvil.server.InternalError", InternalError)
_register_exception_type("anvil.server.InvalidResponseError", InvalidResponseError)
_register_exception_type("anvil.server.RuntimeUnavailableError", RuntimeUnavailableError)
_register_exception_type("anvil.server.UplinkDisconnectedError", UplinkDisconnectedError)
_register_exception_type("anvil.server.ExecutionTerminatedError", ExecutionTerminatedError)
_register_exception_type("anvil.server.TimeoutError", TimeoutError)
_register_exception_type("anvil.server.QuotaExceededError", QuotaExceededError)
_register_exception_type("anvil.server.NoServerFunctionError", NoServerFunctionError)
_register_exception_type("anvil.server.CookieError", CookieError)
_register_exception_type("anvil.server._FailError", _FailError)
_register_exception_type("anvil.server.BackgroundTaskError", BackgroundTaskError)
_register_exception_type("anvil.server.BackgroundTaskNotFound", BackgroundTaskNotFound)
_register_exception_type("anvil.server.BackgroundTaskKilled", BackgroundTaskKilled)



def _report_exception(request_id=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)

    trace = [(filename.replace("\\","/"), lineno) for (filename, lineno, _, _) in tb]
    trace.reverse()

    # Last element of trace is where we called into user code. Remove it.
    trace.pop()

    if isinstance(exc_value, AnvilWrappedError):
        if not exc_value.manually_created:
            # First element of trace is where we re-raised the exception. Remove it.
            trace = trace[1:]
        exc_value.error_obj["trace"] = exc_value.error_obj.get("trace", []) + trace
        r = {
            "error": exc_value.error_obj,
            "id": request_id
        }
        return r
    elif isinstance(exc_value, SyntaxError):
        # Remove whole internal trace and replace it with line where error occurred.
        trace=[(exc_value.filename, exc_value.lineno)]
        return {
            "error": {
                "type": "SyntaxError",
                "trace": trace,
                "message": str(exc_value)
            },
            "id": request_id
        }
    elif isinstance(exc_value, MaybeWrappedError):
        return {
            "error": {
                "type": "anvil.server.%s" % exc_type.__name__,
                "trace": trace,
                "message": str(exc_value),
            },
            "id": request_id
        }
    else:
        return {
            "error": {
                "type": str(exc_type.__name__),
                "trace": trace,
                "message": str(exc_value),
            },
            "id": request_id
        }

def reconstruct_val(v, known_liveobject_methods, reconstruct_data_media=None):

    for t in v["type"]:
        if t == "DataMedia":
            if reconstruct_data_media is None:
                raise Exception("No data media deserialiser provided. Cannot reconstruct.")
            return reconstruct_data_media(v)
        elif t == "LazyMedia":
            return LazyMedia(v)
        elif t == "LiveObject":
            return reconstruct_live_object(v, known_liveobject_methods)
        elif t == "Capability":
            return Capability(v["scope"], v["mac"])
        elif t == "Date":
            return parsedate(v["value"]) if v["value"] else None
        elif t == "DateTime":
            return parsedatetime(v["value"]) if v["value"] else None
        elif t == "Long":
            return long_type(v["value"])
        elif t == "Float":
            return float(v["value"])
        elif t == "Primitive":
            return v["value"]
        elif t == "ValueType":
            return v["typeName"]

    raise Exception("Server module cannot accept an object of type '%s'" % v["type"][0])



def reconstruct_live_object(d, known_methods):

    # Need to fill out known_methods before we can reconstruct members:
    if d.get('methods') is not None:
        known_methods[d["backend"]] = d["methods"]

    reconstructed_item_cache = {}
    for k,v in d.get("itemCache", {}).items():
        reconstructed_item_cache[k] = reconstruct_val(v, known_methods)
    d["itemCache"] = reconstructed_item_cache

    if d.get("iterItems"):
        reconstructed_iteritems = []
        for i in d["iterItems"]["items"]:
            reconstructed_iteritems.append(reconstruct_val(i, known_methods))
        d["iterItems"]["items"] = reconstructed_iteritems

    return LiveObjectProxy(d, known_methods)


def serialise_val(v, known_liveobject_methods):
    import datetime
    if isinstance(v, long_type) and not isinstance(v, bool):
        return {
            "type": ["Long"],
            "value": str(v)
        }
    elif isinstance(v, float) and (v == POS_INFINITY or v == NEG_INFINITY or math.isnan(v)):
        return {
            "type": ["Float"],
            "value": "Infinity" if v == POS_INFINITY else \
                        "-Infinity" if v == NEG_INFINITY else \
                        "NaN"
        }
    elif isinstance(v, (numbers.Number, bool, string_type)) or v is None:
        return {
            "type": ["Primitive"],
            "value": v
        }
    elif isinstance(v, anvil.LiveObject):
        return serialise_live_object(v, known_liveobject_methods)
    elif isinstance(v, datetime.datetime):
        s = "%04d-%02d-%02d %02d:%02d:%02d.%06d" % (v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond)

        if v.tzinfo is not None:
            offset = v.tzinfo.utcoffset(v).total_seconds()
        else:
            offset = 0

        sign = "+" if offset >= 0 else "-"
        z = "%s%02d%02d" % (sign, abs(int(offset/3600)), int((offset % 3600)/60))

        return {
            "type": ["DateTime"],
            "value": s + z
        }
    elif isinstance(v, datetime.date):
        s = "%04d-%02d-%02d" % (v.year, v.month, v.day)
        return {
            "type": ["Date"],
            "value": s
        }
    elif isinstance(v, LazyMedia):
        return dict(v._spec)
    else:
        for [n, cls] in _value_types.items():
            if isinstance(v, cls):
                type_name = n
                break
        else:
            raise Exception("Cannot serialise object of type %s" % type(v).__name__)

        return {
            "type": ["ValueType"],
            "typeName": type_name
        }


def serialise_live_object(obj, known_methods):
    obj = obj._spec.copy()
    obj["type"] = ["LiveObject"]

    km = known_methods.get(obj["backend"])
    if obj["methods"] == km:
        del obj["methods"]
    else:
        known_methods[obj["backend"]] = obj["methods"]

    serialised_item_cache = {}
    for k,v in sorted(obj.get("itemCache", {}).items(), key=lambda x: x[0]):
        # Dictionaries aren't ordered, so we can't allow this element
        # to write into known_methods. We give it a copy instead.
        serialised_item_cache[k] = serialise_val(v, known_methods.copy())
    obj["itemCache"] = serialised_item_cache

    if obj.get("iterItems"):
        serialised_iteritems = []
        for i in obj["iterItems"]["items"]:
            serialised_iteritems.append(serialise_val(i, known_methods))
        obj["iterItems"]["items"] = serialised_iteritems

    return obj


def _repr_path(p):
    return "".join(("[%s]" % repr(k) for k in p))


def fill_out_media(json, handle_media_fn):
    obj_descr = []
    path = []
    known_liveobject_methods = {}
    vt_global_data = {}
    import datetime

    def do_fom(_json):
        if isinstance(_json, dict):
            _json = dict(_json)
            for k,v in sorted(_json.items(),key=lambda x: x[0]):
                if not isinstance(k, string_type):
                    raise SerializationError("Cannot serialize dictionaries with keys that aren't strings at msg%s" % _repr_path(path + [k]))
                path.append(k)
                _json[k] = do_fom(v)
                path.pop()
        elif isinstance(_json, list) or isinstance(_json, tuple):
            _json = list(_json)
            for i in range(len(_json)):
                path.append(i)
                _json[i] = do_fom(_json[i])
                path.pop()
        elif isinstance(_json, LazyMedia):
            d = dict(_json._spec)
            d["path"] = list(path)
            obj_descr.append(d)
            _json = None
        elif isinstance(_json, anvil.Media):
            extra = handle_media_fn(_json)
            d = {"type": ["DataMedia"], "path": list(path), "mime-type": _json.content_type, "name": _json.name}
            if extra is not None:
                d.update(extra)
            obj_descr.append(d)
            _json = None
        elif isinstance(_json, Capability):
            d = {
                "type": ["Capability"],
                "path": list(path),
                "scope": _json._scope,
                "mac": _json._mac
            }
            if _json._narrow:
                d["narrow"] = _json._narrow
            obj_descr.append(d)
            _json = None
        elif isinstance(_json, anvil.LiveObject):
            #print "Serialising LiveObject: " + repr(_json._spec) + " at " + repr(path)
            serialised_liveobject = serialise_live_object(_json, known_liveobject_methods)
            serialised_liveobject["path"] = list(path)
            obj_descr.append(serialised_liveobject)
            _json = None
        elif isinstance(_json, (datetime.date, datetime.datetime)) or \
                (isinstance(_json, long_type) and (_json > 2147483647 or _json < -2147483647)) or \
                (isinstance(_json, float) and (_json == POS_INFINITY or _json == NEG_INFINITY or math.isnan(_json))):
            serialised_val = serialise_val(_json, known_liveobject_methods)
            serialised_val["path"] = list(path)
            obj_descr.append(serialised_val)
            _json = None
        elif isinstance(_json, Serializable):
            type_name = _json.SERIALIZATION_NAME
            if type_name not in _value_types:
                raise SerializationError("Cannot serialize %s (must be registered with @anvil.server.serializable_type) at msg%s" % (type(_json), _repr_path(path)))

            content = _json.__serialize__(vt_global_data)

            _json = do_fom(content)

            # Append this afterwards, so we deserialise our content first
            obj_descr.append({
                "type": ["ValueType"],
                "path": list(path),
                "typeName": type_name
            })

        elif 'numpy' in sys.modules and isinstance(_json, sys.modules['numpy'].generic):

            import numpy
            _json = numpy.asscalar(_json)

        elif not (isinstance(_json, string_type) or _json is None or _json is True or _json is False or isinstance(_json, (int, long_type)) or isinstance(_json, float)):

            # Rescue: Convert numpy types to nearest equivalent
            if 'numpy' in sys.modules:
                import numpy
                if isinstance(_json, numpy.ndarray):
                    _json = _json.tolist()
                else:
                    raise SerializationError("Cannot serialize %s object at msg%s" % (type(_json), _repr_path(path)))
            else:
                raise SerializationError("Cannot serialize %s object at msg%s" % (type(_json), _repr_path(path)))

        return _json

    json = do_fom(json)

    if vt_global_data != {}:
        path.append("vt_global")
        gd = vt_global_data
        vt_global_data = None
        json["vt_global"] = do_fom(gd)
        path.pop()

    json["objects"] = obj_descr

    return json


def simple_strpdate(s):
    import datetime
    return datetime.date(int(s[0:4]), int(s[5:7]), int(s[8:10]))


def simple_strpdatetime(s):
    import datetime
    return datetime.datetime(int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]), int(s[14:16]), int(s[17:19]), int(s[20:26])) # datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

def parsedate(s):
    return simple_strpdate(s)


def parsedatetime(s):

    has_tz = len(s) > 5 and \
             (s[-5] == "-" or s[-5] == "+") and \
             48 <= ord(s[-4]) <= 57 and \
             48 <= ord(s[-3]) <= 57 and \
             48 <= ord(s[-2]) <= 57 and \
             48 <= ord(s[-1]) <= 57

    if not has_tz:
        # Parse a naive datetime
        return simple_strpdatetime(s)

    # Timezone present. First parse without it
    d = simple_strpdatetime(s[:-5])

    # Now construct a tzoffset
    hours = int(s[-5:-2])
    minutes = int(s[-5] + s[-2:])
    total_minutes = hours*60+minutes

    # Cannot import earlier - circular dependency!
    import anvil.tz

    return d.replace(tzinfo=anvil.tz.tzoffset(minutes=total_minutes))


def _reconstruct_objects(json, reconstruct_data_media, hold_back_value_types=False):
    known_liveobject_methods = {}

    if "objects" in json:
        held_back_objects = []
        for d in json["objects"]:
            if hold_back_value_types and "ValueType" in d["type"]:
                held_back_objects.append(d)
                continue

            reconstructed = reconstruct_val(d, known_liveobject_methods, reconstruct_data_media)

            obj = json
            last_obj = None
            key = None
            for k in d["path"]:
                last_obj = obj
                key = k
                obj = obj[k]

            if last_obj is not None:

                if "ValueType" in d["type"]:
                    # Hack: The "reconstructed value" here is actually just the type name
                    type_name = reconstructed
                    value_type = _value_types.get(type_name)
                    if value_type is None:
                        # Try importing the relevant module
                        i = type_name.rfind('.')
                        if i != -1:
                            # TODO do we filter what we can specify as import? I don't *think* this is dangerous...
                            importlib.import_module(type_name[:i])
                            value_type = _value_types.get(type_name)

                        if value_type is None:
                            raise SerializationError("No such serializable type: %s at msg%s" % (type_name, _repr_path(d["path"])))

                    last_obj[key] = value_type.__deserialize__(last_obj[key], json.get('vt_global'))
                else:
                    last_obj[key] = reconstructed

        if hold_back_value_types:
            json["objects"] = held_back_objects
        else:
            del json["objects"]

    return json

on_register = None # optional
registrations = {}


class HttpRequest(object):

    def __init__(self):
        self._prevent_access = True

    def __getattribute__(self, name):
        if object.__getattribute__(self, "_prevent_access"):
            raise Exception("anvil.server.request is only available in http_endpoint calls.")

        return object.__getattribute__(self, name)


api_request = HttpRequest()

class HttpHeaders():

    def __init__(self):
        self._headers = []

    def __setitem__(self, name, val):
        self._headers = [(h,v) for (h,v) in self._headers if h != name]

        self.add(name, val)

    def __delitem__(self, name):
        self._headers = [(h,v) for (h,v) in self._headers if h != name]

    def add(self, name, val):
        self._headers.append((name, val))

    def clear(self):
        self._headers = []

    def __repr__(self):
        return repr(self._headers)



class HttpResponse():

    def __init__(self, status=200, body=""):
        self.status = status
        self.body = body
        self.headers = HttpHeaders()


# can be used as a decorator too
def register(fn, name=None, name_prefix=None):

    if isinstance(fn, string_type):
        # Someone's using the old syntax. Our bad.
        (fn, name) = (name, fn)

    if name is None:
        name = fn.__name__

    if name_prefix is not None:
        name = "%s:%s" % (name_prefix, name)

    registrations[name] = fn

    if on_register is not None:
        on_register(name, False)

    def reregister(new_f):
        registrations[name] = new_f
        new_f._anvil_reregister = reregister

    fn._anvil_reregister = reregister

    return fn


def callable(fn_or_name=None):
    if fn_or_name is None or isinstance(fn_or_name, string_type):
        return lambda f: register(f, fn_or_name)
    else:
        return register(fn_or_name)


def background_task(fn_or_name=None):
    if fn_or_name is None or isinstance(fn_or_name, string_type):
        return lambda f: register(f, fn_or_name, name_prefix="task")
    else:
        return register(fn_or_name, name_prefix="task")


# A parameterised decorator
def callable_as(name):
    print("@callable_as is deprecated. Please use @callable directly.")
    return lambda f: register(f, name)

def http_endpoint(path, require_credentials=False, authenticate_users=False, authenticate_user=False,
                  methods=["GET","POST"], enable_cors=False, cross_site_session=False):
    def decorator(fn):
        path_parts = []
        def register_path_part(s):
            path_parts.append(s.group(1))
            return "([^/]*)"

        path_regex = re.sub(":([^/]*)", register_path_part, path)

        def wrapped_fn(method, path, query_params, form_params, origin, headers, remote_address, body, username, password, same_app_alternate_origin=None, **more_kwargs):

            api_request._prevent_access = False

            if cross_site_session:
                import anvil.server
                anvil.server._switch_session()

            api_request.user = None
            if authenticate_users or authenticate_user:
                import anvil.users
                try:
                    api_request.user = anvil.users.get_user() or \
                                        anvil.users.login_with_email(username, password)
                except (anvil.users.AuthenticationFailed, anvil.users.AccountIsNotEnabled) as e:
                    return {"status": 401,
                            "body": "Unauthorized",
                            "headers": {"WWW-Authenticate": "Basic realm=\"Anvil App API\""}}
            elif require_credentials:
                if username is None or password is None:
                    return {"status": 401,
                            "body": "Unauthorized",
                            "headers": {"WWW-Authenticate": "Basic realm=\"Anvil App API\""}}

            def add_cross_origin_to_header_dict(d):
                if enable_cors:
                    d["Access-Control-Allow-Origin"] = enable_cors if isinstance(enable_cors, str) else "*"
                elif same_app_alternate_origin:
                    d["Access-Control-Allow-Origin"] = same_app_alternate_origin
                return d

            if method not in methods:
                if method == "OPTIONS" and (enable_cors or same_app_alternate_origin):
                    return {"status": 200,
                            "body": "",
                            "headers": add_cross_origin_to_header_dict({})}
                else:
                    return {"status": 405,
                            "body": "Method not supported",
                            "headers": {"Allow": ", ".join(methods)}}

            api_request.path = path
            api_request.method = method
            api_request.query_params = query_params
            api_request.form_params = form_params
            api_request.origin = origin
            api_request.headers = headers
            api_request.remote_address = remote_address
            api_request.body = body
            api_request.username = username
            api_request.password = password

            if body is not None and headers.get("content-type", None) == "application/json":
                api_request.body_json = json.loads(api_request.body.get_bytes())
            else:
                api_request.body_json = None

            
            # Path takes precedence over query params. Query params take precedence over form params.
            kwargs = dict(form_params)
            kwargs.update(query_params)
            match = re.match(path_regex, path)
            for i,m in enumerate(match.groups()):
                kwargs[path_parts[i]] = m

            response = fn(**kwargs)

            api_request._prevent_access = True

            if isinstance(response, HttpResponse):
                return {"status":  response.status,
                        "body":    response.body,
                        "headers": add_cross_origin_to_header_dict(response.headers._headers)}
            else:
                return {"status":  200,
                        "body":    response,
                        "headers": add_cross_origin_to_header_dict({})}

        register(wrapped_fn, path_regex, "http")

        return fn
    return decorator


class AnvilCookie(object):

    def __init__(self, type):
        self._type = type

    def __getitem__(self, name):
        return _do_call([self._type, name], None, fn_name="anvil.private.get_cookie")

    def __setitem__(self, name, value):
        kw = {}
        kw[name] = value
        self.set(30, **kw)

    def __delitem__(self, name):
        _do_call([self._type, name], None, fn_name="anvil.private.del_cookie")

    def get(self, key, default=None):
        try:
            return _do_call([self._type, key], None, fn_name="anvil.private.get_cookie")
        except KeyError:
            return default

    def set(self, timeout_days=30, **values):
        _do_call([self._type, timeout_days], values, fn_name="anvil.private.set_cookie")

    def clear(self):
        _do_call([self._type], None, fn_name="anvil.private.clear_cookie")


class CookieContainer(object):

    def __init__(self):
        self.local = AnvilCookie("local")
        self.shared = AnvilCookie("shared")


cookies = CookieContainer()


class NotABackgroundTaskState():
    def __setitem__(self, key, value):
        raise Exception("Cannot access anvil.server.task_status outside a background task")

    def __getitem__(self, item):
        raise Exception("Cannot access anvil.server.task_status outside a background task")





