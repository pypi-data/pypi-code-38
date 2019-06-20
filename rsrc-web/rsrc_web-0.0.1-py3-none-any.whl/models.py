import io
from typing import (Any,
                    IO,
                    Optional,
                    Type)

import requests
from reprit import seekers
from reprit.base import generate_repr
from rsrc.hints import Domain
from rsrc.models import (Base,
                         FileLikeStream,
                         Stream,
                         URL)


class WebStream(FileLikeStream):
    __slots__ = ('_url',)

    def __init__(self, url: URL) -> None:
        self._url = url

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)

    def __str__(self) -> str:
        return str(self._url)

    def __hash__(self) -> int:
        return hash(self._url)

    def __eq__(self, other: Base) -> bool:
        if not isinstance(other, Base):
            return NotImplemented
        if not isinstance(other, WebStream):
            return False
        return self._url == other._url

    @property
    def url(self) -> URL:
        return self._url

    def exists(self) -> bool:
        try:
            return requests.head(str(self)).ok
        except OSError:
            return False

    def open(self,
             *,
             binary_mode: bool = False,
             encoding: Optional[str] = None,
             **kwargs: Any) -> IO:
        if binary_mode and encoding is not None:
            raise ValueError('binary mode doesn\'t take an encoding argument')
        response = requests.get(str(self), **kwargs)
        response.raise_for_status()
        binary_stream = io.BytesIO(response.content)
        if binary_mode:
            return binary_stream
        return io.TextIOWrapper(binary_stream,
                                encoding=encoding)

    def send(self, destination: Base, **kwargs: Any) -> None:
        if not isinstance(destination, Stream):
            raise TypeError('Unsupported destination type: {type}.'
                            .format(type=type(destination)))
        destination.receive(self, **kwargs)

    def receive(self, source: Base, **kwargs: Any) -> None:
        if not isinstance(source, FileLikeStream):
            raise TypeError('Unsupported source type: {type}.'
                            .format(type=type(source)))
        with source.open(binary_mode=True) as file:
            response = requests.post(str(self), **kwargs,
                                     files={'file': file})
            response.raise_for_status()

    @classmethod
    def from_string(cls: Type[Domain], string: str) -> Domain:
        return cls(URL.from_string(string))
