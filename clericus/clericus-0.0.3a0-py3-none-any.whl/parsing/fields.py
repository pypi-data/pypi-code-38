from dataclasses import dataclass, field
from typing import Any, List, Dict

from .errors import ParseError

import jwt
import bson
import traceback
import inspect
import string

from dateutil.parser import parse as parseDate


@dataclass
class Field():
    optional: bool = False
    missingStatusCode: int = None
    default: Any = None
    allowedTypes: List[str] = None
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
class StringField(Field):
    allowedTypes = ["String"]

    def parser(self, value):
        value = super().parser(value)
        if not isinstance(value, str):
            raise ParseError(message="\"{}\" is not a string".format(value))
        return value


@dataclass
class NoWhitespaceStringField(StringField):
    """
        A string field where leading/trailing whitespace
        should be trimmed.
    """

    def normalizer(self, value):
        value = super().normalizer(value)
        return value.strip()


@dataclass
class NonBlankStringField(NoWhitespaceStringField):
    def parser(self, value):
        value = super().parser(value)
        if not value:
            raise ParseError(message="Cannot be blank")
        return value


@dataclass
class EmailField(NonBlankStringField):
    def parser(self, value):
        value = super().parser(value)
        if "@" not in value:
            raise ParseError(
                message=f"{value} is not a valid email address",
            )
        return value

@dataclass
class UsernameField(NonBlankStringField):
    def parser(self, value):
        value = super().parser(value)

        if any([c in value for c in string.whitespace]):
            raise ParseError("Usernames must not contain whitespace")
        
        return value


@dataclass
class ObjectIdField(Field):
    allowedTypes = ["String"]

    def parser(self, value):
        try:
            return bson.ObjectId(value)
        except:
            raise ParseError(message="\"{}\" is not a valid id".format(value))
        return value

    def serialize(self, value):
        return str(value)


@dataclass
class DatetimeField(Field):
    allowedTypes = ["String"]

    def parser(self, value):
        try:
            return parseDate(value)
        except:
            raise ParseError(
                message="\"{}\" is not a valid datetime".format(value)
            )
        return value

    def serialize(self, value):
        if value:
            return value.isoformat()
        return None


@dataclass
class BoolField(Field):
    allowedTypes = ["Boolean"]

    def parser(self, value):
        try:
            return value == True
        except:
            raise ParseError(
                message="\"{}\" is not a valid boolean".format(value)
            )
        return value


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


@dataclass
class DictField(Field):
    def __init__(self, fields: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = fields or {}
        for k, v in fields.items():
            setattr(self, k, v)

    def _getFields(self):
        return {
            f: theField
            for (f, theField) in filter(
                lambda k: isinstance(k[1], Field),
                inspect.getmembers(self),
            )
        }

    def parser(self, source: Dict):
        source = source or {}
        fields = self._getFields()
        if not fields:
            return source
        parameters = {}
        for name, parameter in fields.items():
            if (not parameter.optional) and (name not in source):
                raise ParseError(
                    message="Missing required field: {}".format(name),
                    statusCode=parameter.missingStatusCode,
                )
            parameters[name] = parameter.parse(
                source.get(name, parameter.default)
            )
        return parameters

    def serialize(self, dictValue):
        fields = self._getFields()
        if not fields:
            return dictValue
        result = {}

        for name, outField in fields.items():
            try:
                value = dictValue[name]

                name = getattr(outField, "serializeTo", name) or name

                try:
                    result[name] = outField.serialize(value)

                except:
                    result[name] = value
            except KeyError as k:
                if not outField.optional:
                    print("MISSING FIELD FOR SERIALIZATION", k)
                    result[name] = None

        return result

    def describe(self):
        return {
            key: field.describe()
            for (key, field) in self._getFields().items()
        }


@dataclass
class ErrorField(DictField):
    message = StringField()


@dataclass
class ListField(Field):
    def __init__(self, elementField):
        self.elementField = elementField
        self.default = []

    def parser(self, source):
        if not source:
            return []
        parsed = []
        for value in source:
            parsed.append(elementField.parser(value))
        return parsed

    def serialize(self, values):
        result = []
        if not values:
            return result
        for value in values:
            try:
                result.append(self.elementField.serialize(value))
            except Exception as e:
                print(e)
                result.append(value)

        return result