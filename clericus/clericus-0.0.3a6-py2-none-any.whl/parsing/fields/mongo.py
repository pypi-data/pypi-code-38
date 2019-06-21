import bson

from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class ObjectIdField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.STRING])

    def parser(self, value):
        try:
            return bson.ObjectId(value)
        except:
            raise ParseError(message="\"{}\" is not a valid id".format(value))
        return value

    def serialize(self, value):
        return str(value)
