from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict

from .strings import StringField
from .dicts import DictField


@dataclass
class ErrorField(DictField):
    message = StringField()
