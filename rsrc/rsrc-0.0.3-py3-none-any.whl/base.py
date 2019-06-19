from typing import (Callable,
                    Dict,
                    Union)

from pkg_resources import iter_entry_points

from . import plugins
from .models import (Resource,
                     URL)

_stop = object()

_DeserializersKey = Union[str, type(_stop)]
_Deserializer = Callable[[str], Resource]
_Deserializers = Dict[_DeserializersKey, _Deserializer]
_Deserializers = Dict[_DeserializersKey, _Deserializers]


def _load_deserializers() -> _Deserializers:
    registry = {entry_point.name: entry_point.load()
                for entry_point in iter_entry_points(plugins.__name__)}
    result = {}
    for name, deserializer in registry.items():
        id_ = plugins.deserialize_id(name)
        location = result
        for key in id_:
            location = location.setdefault(key, {})
        location[_stop] = deserializer
    return result


_deserializers = _load_deserializers()


def deserialize(string: str) -> Resource:
    result = URL.from_string(string)
    location = _deserializers
    for field in result._tuple:
        try:
            location = location[field]
        except KeyError:
            break
    try:
        deserializer = location[_stop]
    except KeyError as error:
        raise ValueError('Resource "{resource}" is not supported.'
                         .format(resource=string)) from error
    else:
        return deserializer(string)
