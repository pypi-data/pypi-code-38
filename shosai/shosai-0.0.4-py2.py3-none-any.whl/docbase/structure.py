import typing as t
import mypy_extensions as mx
from shosai.base import structure as base


class MappingDict(mx.TypedDict):
    id: int
    title: str
    draft: bool
    url: str
    created_at: str
    scope: str
    groups: t.Sequence[str]
    file: str


class ProfileDict(mx.TypedDict):
    token: str
    teamname: str
    username: str


class MetadataDict(mx.TypedDict):
    id: int
    name: str  # todo
    title: str
    draft: bool
    url: str
    created_at: str
    scope: str
    groups: t.Sequence[str]
    file: str


class TagDict(mx.TypedDict):
    name: str


class UserDict(mx.TypedDict):
    id: int
    name: str
    profile_image_url: str


AttachmentDict = base.AttachmentDict


class AttachmentResultDict(base.AttachmentResultDict):
    size: int
    markdown: str
    created_at: str


class PostDict(mx.TypedDict):
    body: str
    comments: t.Sequence[t.Dict]  # untyped
    created_at: str
    draft: bool
    groups: t.Sequence[int]  # xxx
    id: int
    scope: str  # everyone,...
    tags: t.Sequence[TagDict]
    title: str
    url: str
    user: UserDict
