from abc import (ABC,
                 abstractmethod)
from pathlib import PurePosixPath
from typing import (Any,
                    Generic,
                    Iterable,
                    Iterator,
                    Type,
                    TypeVar,
                    Union)
from urllib.parse import (quote,
                          quote_plus,
                          unquote,
                          unquote_plus,
                          urlparse,
                          urlunparse)

from memoir import cached
from reprit.base import generate_repr

from .hints import Domain


# not using `namedtuple` to be weak referencable
class URL:
    _fields = ('scheme', 'authority', 'path_string',
               'params', 'query', 'fragment')
    __slots__ = ('_tuple', '__weakref__')

    # added for auto-completion support,
    # each of them will be overwritten afterwards in cycle
    # and made a `property`
    scheme = ''
    authority = ''
    path_string = ''
    params = ''
    query = ''
    fragment = ''

    for index, field in enumerate(_fields):
        locals()[field] = property(
                lambda self, index=index: self._tuple[index])
    del index, field

    def __init__(self,
                 scheme: str,
                 authority: str,
                 path_string: str,
                 params: str,
                 query: str,
                 fragment: str) -> None:
        self._tuple = (scheme, authority, path_string, params, query, fragment)

    def __hash__(self) -> int:
        return hash(self._tuple)

    def __eq__(self, other: 'URL') -> bool:
        if not isinstance(other, URL):
            return NotImplemented
        return self._tuple == other._tuple

    def __str__(self) -> str:
        return urlunparse(self._replace(path_string=quote(self.path_string,
                                                          '/%'),
                                        query=quote_plus(self.query, ':&='))
                          ._tuple)

    __repr__ = generate_repr(__init__)

    def _replace(self, **kwargs: str) -> 'URL':
        return type(self)(*map(kwargs.pop, self._fields, self._tuple))

    def join(self, part: str, *parts: str) -> 'URL':
        return self._replace(path_string=str(self.path.joinpath(part, *parts)),
                             params='',
                             query='',
                             fragment='')

    @cached.property_
    def path(self) -> PurePosixPath:
        return PurePosixPath(self.path_string)

    @classmethod
    def from_string(cls: Type[Domain], string: str) -> Domain:
        raw = urlparse(string)
        return cls(scheme=raw.scheme,
                   authority=raw.netloc,
                   path_string=unquote(raw.path),
                   params=raw.params,
                   query=unquote_plus(raw.query),
                   fragment=raw.fragment)


class Base(ABC):
    @property
    @abstractmethod
    def url(self) -> URL:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __eq__(self, other: 'Base') -> bool:
        pass

    @classmethod
    @abstractmethod
    def from_string(cls: Type[Domain], string: str) -> Domain:
        pass


class Container(Base):
    @abstractmethod
    def join(self, part: str, *parts: str) -> Base:
        pass

    def __truediv__(self, other: str) -> Base:
        if not isinstance(other, str):
            return NotImplemented
        return self.join(other)

    @abstractmethod
    def __iter__(self) -> Iterator[Base]:
        pass


Element = TypeVar('Element')


class Stream(Base, Generic[Element]):
    @abstractmethod
    def open(self, **kwargs) -> Iterable[Element]:
        pass

    @abstractmethod
    def send(self, destination: Base, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def receive(self, source: Base, **kwargs: Any) -> None:
        pass


Resource = Union[Stream, Container]
