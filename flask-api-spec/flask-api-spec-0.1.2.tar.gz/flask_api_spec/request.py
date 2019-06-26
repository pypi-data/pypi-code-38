from datetime import datetime

import dateutil.parser as dp
import yaml
from marshmallow import Schema as MSchema
from marshmallow import fields

from .value import NestedValue


def transform_compatible_types(value):
    """
    value: Value
    """
    new_types = []
    for ty in value.types:
        if ty == datetime:
            new_types.append(str)
            new_types.append(lambda x: dp.parse(x))
        else:
            new_types.append(ty)
    value.original_types = value.types
    value.types = new_types
    value.refresh()
    return value


class Request:
    @classmethod
    def __toSchema(cls, klass):
        schema = {}
        for k, v in klass.__dict__.items():
            if k.startswith('__') or callable(v):
                continue
            if isinstance(v, NestedValue):
                schema[k] = v.nested_class.toSchemaCls()
            else:
                schema[k] = transform_compatible_types(v)
        return schema

    @classmethod
    def toSchemaCls(cls):
        return Request.__toSchema(cls)

    def toSchema(self):
        return Request.__toSchema(self.__class__)
