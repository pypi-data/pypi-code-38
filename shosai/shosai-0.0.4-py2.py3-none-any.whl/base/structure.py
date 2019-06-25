import typing as t
import mypy_extensions as mx


class PostDict(mx.TypedDict):
    content: str
    tags: t.Sequence[str]
    title: str


class MappingDict(mx.TypedDict):
    id: t.Any
    name: str
    title: str
    draft: bool
    url: str
    created_at: str
    file: str
    tags: t.Sequence[str]


class AttachmentDict(mx.TypedDict):
    name: str
    content: str


class AttachmentResultDict(mx.TypedDict):
    id: t.Any
    name: str
    url: str
