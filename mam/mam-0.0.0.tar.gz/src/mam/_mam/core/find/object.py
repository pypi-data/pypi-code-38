"""Find objects."""

from typing import Iterator, List, Optional

from .objects import InternalSegment, ObjectWalk, Segment, Type

__all__ = [
    'find_object',
]


def normalize_path(path: str) -> str:
    """
    Normalize path.

    Converts
        # -> root
        ^ -> parent
        ^^ -> parent.parent
    """
    if not path.startswith('$'):
        return path

    path = path[1:]
    if path.startswith('#'):
        return 'root.' + path[1:]

    for i, value in enumerate(path):
        if value != '^':
            return 'parent.' * i + path[i:]
    return ('parent.' * len(path))[:-1]


def _split(path: str) -> Iterator[InternalSegment]:
    """Split into internal segments."""
    path_ = iter(enumerate(path, 1))
    name: List[str] = []
    current_type = Type.GET_ATTR

    def handle_prev() -> InternalSegment:
        """Create internal segment."""
        nonlocal name
        if not name:
            return None
        output = ''.join(name)
        name = []
        return output, current_type

    for index, char in path_:
        if char == '\\':
            char_: Optional[str] = next(path_, (None, None))[1]
            if char_ is None:
                break
            name.append(char_)
            continue

        if char == '.':
            if current_type is Type.GET_ITEM_INTERNAL:
                raise ValueError('Invalid char . at {0}'.format(index))
            yield handle_prev()
            current_type = Type.GET_ATTR
        elif char == ']':
            if current_type is not Type.GET_ITEM_INTERNAL:
                raise ValueError('Invalid char ] at {0}'.format(index))
            current_type = Type.GET_ITEM
        elif char == '[':
            yield handle_prev()
            current_type = Type.GET_ITEM_INTERNAL
        else:
            name.append(char)
    if current_type is Type.GET_ITEM_INTERNAL:
        raise ValueError('Missing closing bracket')
    yield handle_prev()


def split(path: str, orig_path: str,
          ) -> List[Segment]:
    """Split path into segments."""
    output = []
    for segment in _split(path):
        if segment is None:
            continue
        key, type_ = segment
        if type_ is Type.GET_ITEM_INTERNAL:
            raise ValueError('Invalid path {0}'.format(orig_path))
        output.append((key, type_.value))
    return output


def find_object(path: str) -> ObjectWalk:
    """Build function that walks path."""
    path_ = normalize_path(path)
    segments = split(path_, path)
    return ObjectWalk(path, segments)
