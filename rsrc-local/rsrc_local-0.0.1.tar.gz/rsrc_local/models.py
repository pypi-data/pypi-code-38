import os
import shutil
from errno import (EINVAL,
                   EISDIR,
                   ENOTDIR)
from pathlib import Path
from stat import (S_ISDIR,
                  S_ISREG)
from typing import (Any,
                    IO,
                    Iterator,
                    Type)

from memoir import cached
from reprit import seekers
from reprit.base import generate_repr
from rsrc.models import (Base,
                         Container,
                         Stream,
                         URL)

from .hints import Domain


def path_to_resource(path: Path) -> Base:
    if path.is_dir():
        return Directory(path)
    return File(path)


class Directory(Container):
    __slots__ = ('_path',)

    def __init__(self, path: Path) -> None:
        self._path = path

    def __iter__(self) -> Iterator[Base]:
        yield from map(path_to_resource, self._path.iterdir())

    def __hash__(self) -> int:
        return hash(self._path)

    def __eq__(self, other: Base) -> bool:
        if not isinstance(other, Base):
            return NotImplemented
        if not isinstance(other, Directory):
            return False
        return self._path == other._path

    @cached.property_
    def url(self) -> URL:
        return URL.from_string(self._path.as_uri())

    def exists(self) -> bool:
        try:
            stat = self._path.stat()
        except FileNotFoundError:
            return False
        else:
            if S_ISDIR(stat.st_mode):
                return True
            raise _to_os_error(error_code=ENOTDIR,
                               location_string=str(self))

    def join(self, part: str, *parts: str) -> Base:
        return path_to_resource(self._path.joinpath(part, *parts))

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)

    def __str__(self) -> str:
        return str(self._path)

    @classmethod
    def from_string(cls: Type[Domain], string: str) -> Domain:
        path = Path(string)
        if path.is_file():
            raise ValueError('Invalid argument: "{argument}" '
                             'supposed to be a path to directory, '
                             'but found file.'
                             .format(argument=string))
        return cls(path)


class File(Stream[str]):
    __slots__ = ('_path',)

    def __init__(self, path: Path) -> None:
        self._path = path

    def __hash__(self) -> int:
        return hash(self._path)

    def __eq__(self, other: Base) -> bool:
        if not isinstance(other, Base):
            return NotImplemented
        if not isinstance(other, File):
            return False
        return self._path == other._path

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)

    def __str__(self) -> str:
        return str(self._path)

    def exists(self) -> bool:
        try:
            stat = self._path.stat()
        except FileNotFoundError:
            return False
        else:
            mode = stat.st_mode
            if S_ISREG(mode):
                return True
            raise _to_os_error(error_code=EISDIR if S_ISDIR(mode) else EINVAL,
                               location_string=str(self))

    def open(self,
             *,
             binary_mode: bool = False,
             encoding: str = None) -> IO:
        return self._path.open(mode='rb' if binary_mode else 'r',
                               encoding=encoding)

    def send(self, destination: Base, **kwargs: Any) -> None:
        if not isinstance(destination, Stream):
            raise TypeError('Unsupported destination type: {type}.'
                            .format(type=type(destination)))
        if isinstance(destination, File):
            shutil.copy(str(self), str(destination))
        else:
            destination.receive(self, **kwargs)

    def receive(self, source: Base, **kwargs: Any) -> None:
        if not isinstance(source, Stream):
            raise TypeError('Unsupported destination type: {type}.'
                            .format(type=type(source)))
        if isinstance(source, File):
            shutil.copy(str(source), str(self))
        else:
            source.send(self, **kwargs)

    @cached.property_
    def url(self) -> URL:
        return URL.from_string(self._path.as_uri())

    @classmethod
    def from_string(cls: Type[Domain], string: str) -> Domain:
        path = Path(string)
        if path.is_dir():
            raise ValueError('Invalid argument: "{argument}" '
                             'supposed to be a path to file, '
                             'but found directory.'
                             .format(argument=string))
        return cls(path)


def _to_os_error(*,
                 error_code: int,
                 location_string: str) -> OSError:
    return OSError(error_code, os.strerror(error_code), location_string)
