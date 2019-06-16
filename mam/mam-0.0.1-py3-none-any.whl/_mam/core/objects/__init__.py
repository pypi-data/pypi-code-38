"""Core objects."""
# nosa: E501,pylint[:Line too long]
from __future__ import annotations

import dataclasses
import string
from typing import (
    Any, Dict, List, Mapping, Optional, Sequence, Tuple, TypeVar, Union,
)

from ..find import find_object

__all__ = [
    '_Null',
    'NULL',
    'PathFormatter',
    'Format',
    'ALL',
    'Message',
    'MessageKeys',
]

T = TypeVar('T')  # nosa: pylint[C0103]


class Less:
    """Object that is always less than anything."""

    def __str__(self):
        return 'None'  # For when output doesn't convert from Less.

    # nosa: pylint[C0123]
    def __lt__(self, other: Any) -> bool:
        """Less than anything."""
        return True

    def __le__(self, other: Any) -> bool:
        """Less than or equal to anything."""
        return True

    def __eq__(self, other: Any) -> bool:
        """Equal to itself."""
        return type(other) is Less

    def __ne__(self, other: Any) -> bool:
        """Not equal to anything but Less."""
        return type(other) is not Less

    def __gt__(self, other: Any) -> bool:
        """Greater than nothing."""
        return False

    def __ge__(self, other: Any) -> bool:
        """Greater than nothing, equal to self."""
        return type(other) is Less

    def __hash__(self) -> int:
        """Hashable."""
        return 1355

    @classmethod
    def default(cls, obj: Union[Less, T], default: T) -> T:
        """Change Less item to default."""
        if isinstance(obj, Less):
            return default
        return obj


LESS = Less()


class MessageKeys:
    """Message names."""

    APP = 'app'
    PATH = 'path'
    LINE = 'line'
    CHAR = 'char'
    CODE = 'code'
    CODE_READABLE = 'code_readable'
    MESSAGE = 'msg'
    EXTENDS = 'extends'
    EXTRAS = 'extras'


def _default(value, obj, default):
    return value if value is not obj else default


@dataclasses.dataclass
class Message:
    """Message object."""

    app: str
    path: Union[str, Less]
    line: Union[int, Less]
    char: Union[int, Less]
    code: Union[str, Less]
    code_readable: Union[str, Less]
    message: Union[str, Less]
    extends: List[str]
    extras: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, obj):
        """Build message from dictionary."""
        return cls(
            app=obj[MessageKeys.APP],
            path=_default(obj.get(MessageKeys.PATH), None, LESS),
            line=_default(obj.get(MessageKeys.LINE), None, LESS),
            char=_default(obj.get(MessageKeys.CHAR), None, LESS),
            code=_default(obj.get(MessageKeys.CODE), None, LESS),
            code_readable=_default(obj.get(MessageKeys.CODE_READABLE), None, LESS),
            message=_default(obj.get(MessageKeys.MESSAGE), None, LESS),
            extends=obj.get(MessageKeys.EXTENDS) or [],
            extras=obj.get(MessageKeys.EXTRAS) or [],
        )

    def to_dict(self):
        """Convert message to dictionary."""
        return {
            MessageKeys.APP: self.app,
            MessageKeys.PATH: _default(self.path, LESS, None),
            MessageKeys.LINE: _default(self.line, LESS, None),
            MessageKeys.CHAR: _default(self.char, LESS, None),
            MessageKeys.CODE: _default(self.code, LESS, None),
            MessageKeys.CODE_READABLE: _default(self.code_readable, LESS, None),
            MessageKeys.MESSAGE: _default(self.message, LESS, None),
            MessageKeys.EXTENDS: self.extends,
            MessageKeys.EXTRAS: self.extras,
        }


class _Null:
    """Create a null value that isn't the same as None."""

    def __str__(self) -> str:
        """Return string representation."""
        return 'NULL'

    def __len__(self) -> int:
        """Length of _Null."""
        return 0

    @classmethod
    def default(cls, obj: Union[_Null, T], default: T) -> T:
        """Change _Null item to default."""
        if isinstance(obj, _Null):
            return default
        return obj

    @classmethod
    def default_none(cls, obj: Union[_Null, None, T], default: T) -> T:
        """Change _Null item to default."""
        if isinstance(obj, _Null):
            return default
        if obj is None:
            return default
        return obj


NULL = _Null()


class PathFormatter(string.Formatter):
    """Custom formatter to `find_object` searching."""

    def get_field(self, field_name: str, args: Sequence[Any],
                  kwargs: Mapping[str, Any],
                  ) -> Tuple[Any, str]:
        """Get field, like normal but extended with $# and $^ syntax."""
        function = find_object(field_name)
        obj = function(kwargs['self'].parent)
        value = obj._value
        if any(i[1] is not None for i in self.parse(value)):
            new_kwargs = dict(kwargs)
            new_kwargs['self'] = obj
            # Recursively handle formats, not clean but works.
            value = self.vformat(value, args, new_kwargs)
        return value, 'self'


class Format:
    """Lazy formatting object."""

    def __init__(self, format_: str, *args: Any, **kwargs: Any) -> None:
        """Initialize object."""
        self.format = format_
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        """Build string."""
        return self.format.format(*self.args, **self.kwargs)


class All:
    """Allow all status types."""

    last: Optional[int] = None

    def __contains__(self, item: int) -> bool:
        """Allow all status types, store last."""
        self.last = item
        return True


ALL = All()
