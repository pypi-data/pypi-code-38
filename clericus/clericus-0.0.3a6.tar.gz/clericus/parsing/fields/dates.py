from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict

from dateutil.parser import parse as parseDate


@dataclass
class DatetimeField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.STRING])

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