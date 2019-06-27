from datetime import datetime

from marshmallow import Schema as MSchema
from marshmallow import fields

from .value import NestedValue, Value


class Response(MSchema):
    @classmethod
    def redefine(cls, k, v):
        cls.__dict__['_declared_fields'][k] = v

    def __init__(self, *args, **kwargs):
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, Value):
                if v.types[0] == int:
                    self.__class__.redefine(k, fields.Int())
                elif v.types[0] == str:
                    self.__class__.redefine(k, fields.Str())
                elif v.types[0] == datetime:
                    self.__class__.redefine(k, fields.DateTime())
            if isinstance(v, NestedValue):
                self.__class__.redefine(k, fields.Nested(
                    v.nested_class, *v.args, **v.kwargs))
        MSchema.__init__(self, *args, **kwargs)
