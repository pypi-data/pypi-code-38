import typing as t
import mypy_extensions as mx
import logging
import os.path
import base64
from requests import sessions
from ..langhelpers import reify
from ..base.resources import LoggedRequestMixin
from . import structure
logger = logging.getLogger(__name__)


class Session(LoggedRequestMixin, sessions.Session):
    logger = logger


class Resource:
    def __init__(self, profile):
        self.profile = profile

    @reify
    def url(self):
        return f"https://api.docbase.io/teams/{self.profile.teamname}".rstrip("/")

    @reify
    def session(self) -> Session:
        s = Session()
        s.headers["X-DocBaseToken"] = self.profile.token
        return s

    def __enter__(self):
        self.session.__enter__()
        return self

    def __exit__(self, *args):
        return self.session.__exit__(*args)

    @reify
    def search(self) -> "Search":
        return Search(self)

    @reify
    def attachment(self) -> "Attachment":
        return Attachment(self)

    @reify
    def fetch(self) -> "Fetch":
        return Fetch(self)

    @reify
    def post(self) -> "Post":
        return Post(self)

    def is_author(self, userdata: t.Union[t.Dict, str]):
        return self.profile.username == userdata


class SearchResponseMetaDict(mx.TypedDict):
    next_page: t.Optional[str]
    previous_page: t.Optional[str]
    total: int


class SearchResponseDict(mx.TypedDict):
    meta: SearchResponseMetaDict
    posts: t.Sequence[structure.PostDict]


class SearchParamsDict(mx.TypedDict, total=False):
    q: str  # default "*"
    page: int  # default 1
    per_page: int  # default 20, max 100


class Search:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def __call__(
        self,
        *,
        q: t.Optional[str] = None,
        page: t.Optional[int] = None,
        per_page: t.Optional[int] = None,
    ) -> t.Sequence[SearchResponseDict]:
        app = self.app
        url = f"{app.url}/posts"

        params: SearchParamsDict = {}
        params["q"] = q or f"author:{app.profile.username}"
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        response = app.session.get(url, params=params)
        return response.json()


class Attachment:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def build_content_from_file(
        self,
        path: str,
        *,
        name=None,
    ) -> structure.AttachmentDict:
        with open(path, "rb") as rf:
            data = rf.read()
        return self.build_content(path, data, name=name)

    def build_content(
        self,
        path: str,
        data: bytes,
        *,
        name: t.Optional[str] = None,
    ) -> structure.AttachmentDict:
        return {
            "name": name or os.path.basename(path),
            "content": base64.b64encode(data).decode("ascii"),
        }

    def __call__(self, contents) -> t.Sequence[structure.AttachmentResultDict]:
        # [{"name": <str>, "content": <base64>}]
        app = self.app
        url = f"{app.url}/attachments"

        response = app.session.post(url, json=contents)
        return response.json()


class Fetch:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def __call__(self, id: int) -> structure.PostDict:
        app = self.app
        url = f"{app.url}/posts/{id}"
        response = app.session.get(url)
        return response.json()

    def from_url(self, url: str) -> structure.PostDict:
        import re
        app = self.app
        rx = re.compile(r"https://([^.]+).docbase.io/posts/(\d+)")

        m = rx.search(url)
        assert m is not None
        team = m.group(1)
        assert team == app.profile.teamname
        id = m.group(2)
        return self.__call__(id)


class _PostParamsDictOptional(mx.TypedDict, total=False):
    draft: bool  # default false
    notice: bool  # default true
    tags: t.Sequence[str]
    scope: str  # default "everyone"
    groups: t.Sequence[str]


class PostParamsDict(_PostParamsDictOptional, mx.TypedDict, total=True):
    title: str
    body: str


class Post:
    def __init__(self, app: Resource) -> None:
        self.app = app

    # todo: group/scope
    def __call__(
        self,
        title: str,
        body: str,
        *,
        draft: t.Optional[bool] = None,
        notice: bool = False,
        tags: t.Optional[t.Sequence[str]] = None,
        id: t.Optional[str] = None,
        meta: t.Optional[structure.MetadataDict] = None,
    ) -> structure.PostDict:
        params: PostParamsDict = {
            "title": title,
            "body": body,
            "draft": (draft is None) or bool(draft),  # default is draft=True
            "notice": notice,
        }
        if tags is not None:
            params["tags"] = tags

        if meta is not None:
            if draft is None:
                params["draft"] = meta["draft"]

            # xxx: passing scope is only owner or team-admin(same settings are also invalid)
            if self.app.is_author(meta["user"]["name"]):
                params["scope"] = meta["scope"]
                params["groups"] = [g["id"] for g in meta["groups"]]
            else:
                params.pop("draft", None)

        if id is None:
            return self._create_post(params)
        else:
            return self._update_post(params, id=id)

    def _update_post(self, params: t.Dict, *, id: str) -> structure.PostDict:
        app = self.app
        url = f"{app.url}/posts/{id}"
        response = app.session.patch(url, json=params)
        return response.json()

    def _create_post(self, params: t.Dict) -> structure.PostDict:
        app = self.app
        url = f"{app.url}/posts"

        response = app.session.post(url, json=params)
        return response.json()
