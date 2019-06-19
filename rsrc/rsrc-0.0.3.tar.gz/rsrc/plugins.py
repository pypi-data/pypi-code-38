import codecs
import json
from typing import List

from .models import URL

Id = List[str]

MAX_ID_PARTS_COUNT = len(URL._fields)


def to_id(*parts: str,
          max_parts_count: int = MAX_ID_PARTS_COUNT) -> Id:
    if len(parts) > max_parts_count:
        raise ValueError('Parts count should not be '
                         'greater than {max_expected_count}, '
                         'but found {actual_count}.'
                         .format(max_expected_count=max_parts_count,
                                 actual_count=len(parts)))
    return list(parts)


_ENCODING = 'hex'


def serialize_id(id_: Id) -> str:
    return codecs.encode(json.dumps(id_).encode(), _ENCODING).decode()


def deserialize_id(string: str) -> Id:
    return json.loads(codecs.decode(string, _ENCODING).decode())


def to_entry_point(*, id_: Id, module_name: str, function_name: str) -> str:
    return ('{id_} = {module_name}:{function_name}'
            .format(id_=serialize_id(id_),
                    module_name=module_name,
                    function_name=function_name))
