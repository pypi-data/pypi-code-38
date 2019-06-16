"""Hold file objects."""

import enum
import operator
from typing import Any, Callable, Iterable, NamedTuple, Optional, Tuple

__all__ = [
    'Segment',
    'Type',
    'InternalSegment',
    'ObjectWalk',
    'System',
    'FileInfo',
]

Segment = Tuple[str, Callable[[Any, str], Any]]


class Type(enum.Enum):
    """Type tokens."""

    GET_ATTR = getattr
    GET_ITEM = operator.getitem
    GET_ITEM_INTERNAL = 3


InternalSegment = Optional[Tuple[str, Type]]


class ObjectWalk:
    """Callable with properties."""

    segments: Tuple[Segment, ...]

    def __init__(self, path: str, segments: Iterable[Segment]):
        """Construct ObjectWalk."""
        self.path = path
        self.segments = tuple(segments)

    def __call__(self, obj: Any) -> Any:
        """Walk the object."""
        for key, function in self.segments:
            try:
                obj = function(obj, key)
            except (AttributeError, TypeError, KeyError):
                raise ValueError(
                    "{obj}.{path} doesn't exist"
                    .format(obj=obj, path=self.path),
                )
        return obj

    @property
    def names(self) -> Tuple[str, ...]:
        """Get the names of the segments."""
        return tuple(key for key, _ in self.segments)


System = NamedTuple(
    'System',
    [
        ('module', Optional[Any]),
        ('path', Optional[str]),
    ],
)


class FileInfo(NamedTuple(
    'FileInfo',
    [
        ('module', Optional[Any]),
        ('path', Optional[str]),
        ('search', ObjectWalk),
    ],
)):
    """File named tuple."""

    @property
    def obj(self) -> Any:
        """Get the object in the module."""
        return self.search(self.module)
