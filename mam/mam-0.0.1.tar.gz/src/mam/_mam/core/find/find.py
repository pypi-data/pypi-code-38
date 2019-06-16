"""Find both system and object."""

from .object import find_object
from .objects import FileInfo
from .system import find_system

__all__ = [
    'find',
]


def find(path: str) -> FileInfo:
    """Get file info from path."""
    segments = path.rsplit(':', 1)
    if len(segments) == 1:
        if segments[0].startswith('$'):
            segments = ['', segments[0]]
        else:
            segments = [segments[0], '']
    system_, object_ = segments
    module, path_ = find_system(system_)
    return FileInfo(module, path_, find_object(object_))
