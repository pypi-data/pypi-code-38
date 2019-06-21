from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class BoolField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.BOOL])

    def parser(self, value):
        try:
            return value == True
        except:
            raise ParseError(
                message="\"{}\" is not a valid boolean".format(value)
            )
        return value