from dataclasses import dataclass, field
from typing import Any, List, Dict

from ..errors import ParseError

import jwt
import bson
import traceback
import inspect
import string
import enum


class FieldTypes(str, enum.Enum):
    STRING = "string"
    BOOL = "boolean"
    OBJECT = "object"
    INTEGER = "int"


@dataclass
class Field():
    optional: bool = False
    missingStatusCode: int = None
    default: Any = None
    allowedTypes: List[str] = field(default_factory=list)
    description: str = ""
    parseFrom: str = None
    serializeTo: str = None

    def parser(self, value):
        return value

    def normalizer(self, value):
        return value

    def parse(self, value):
        value = self.parser(value)
        return self.normalize(value)

    def normalize(self, value):
        return self.normalizer(value)

    def serialize(self, value):
        return value

    def describe(self):
        return {
            "allowedTypes": self.allowedTypes,
            "optional": self.optional,
            "default": self.default,
            "description": self.description,
        }

    def __repr__(self):
        return "FIELD"


@dataclass
class JwtField(Field):
    secretKey: str = ""

    def parser(self, value):
        value = super().parser(value)
        if not value:
            return None
        parsed = jwt.decode(
            value,
            self.secretKey,
            algorithms=['HS256'],
        )
        return parsed
