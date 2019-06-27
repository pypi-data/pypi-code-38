import json
import logging
import os
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterator, List, Mapping, Optional
from urllib.parse import ParseResult, urlparse

import github
import gitlab
import jsonschema
import requests

log = logging.getLogger(__name__)


CATALOG_SCHEMA_URL = "https://opendataschema.frama.io/catalog/schema-catalog.json"
DEFAULT_SCHEMA_FILENAME = "schema.json"
DEFAULT_SESSION = requests.Session()
GITHUB_DOMAIN = "github.com"


class GitRef:
    """A Git reference (branch or tag) in a platform (i.e. GitLab/GitHub) agnostic way."""

    def __init__(self, name=None, commit=None, _source=None):
        self.name = name
        self.commit = commit
        self._source = None

    def __repr__(self):
        return "<GitRef name={!r} commit={!r}>".format(self.name, self.commit)


class GitCommit:
    """A Git commit in a platform (i.e. GitLab/GitHub) agnostic way."""

    def __init__(self, sha, committed_date=None, _source=None):
        self.sha = sha
        self.committed_date = committed_date
        self._source = None

    def __repr__(self):
        return "<GitCommit sha={!r} committed_date={!r}>".format(self.sha, self.committed_date)


def by_commit_date(tag: GitRef):
    return tag.commit.committed_date if tag.commit else date.min


def without_none_values(data: dict) -> dict:
    """Keep only keys whose value is not None"""
    return {k: v
            for k, v in data.items()
            if v is not None}


def is_http_url(url: str) -> bool:
    return re.match("https?://", url)


def load_json_from_url(url: str, session: requests.Session = DEFAULT_SESSION):
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def load_text_from_url(url: str, session: requests.Session = DEFAULT_SESSION) -> str:
    response = session.get(url)
    response.raise_for_status()
    return response.text


def load_text_from_file(path) -> str:
    if isinstance(path, str):
        path = Path(path)
    return path.read_text()


class SchemaCatalog:
    def __init__(self, source, catalog_schema_url: str = CATALOG_SCHEMA_URL, session: requests.Session = DEFAULT_SESSION):
        """
        :param source: can be a `str`, a `pathlib.Path` or a `dict` representing the catalog
        """
        self.session = session

        if isinstance(source, Path):
            source = str(source)

        if isinstance(source, str):
            catalog_content = load_text_from_url(source, session=session) \
                if is_http_url(source) \
                else load_text_from_file(source)
            descriptor = json.loads(catalog_content)
        else:
            descriptor = source

        schema = load_json_from_url(catalog_schema_url, session=self.session)
        jsonschema.validate(instance=descriptor, schema=schema)  # raise an exception if invalid
        if descriptor["version"] != 1:
            raise NotImplementedError("Only version 1 is supported")
        self.descriptor = descriptor

        references = [
            SchemaReference.from_config(config, session=session)
            for config in self.descriptor['schemas']
        ]
        self.references = references
        self.reference_by_name = {reference.name: reference for reference in references}


class SchemaReference(ABC):
    @staticmethod
    def from_config(config: dict, session: requests.Session = DEFAULT_SESSION):
        options = without_none_values(config)
        if config.get("repo_url"):
            return GitSchemaReference.from_repo_url(**options, session=session)
        elif config.get("schema_url"):
            return URLSchemaReference(**options)
        assert False, config  # Should not happen because config has already been validated by JSON Schema.

    @abstractmethod
    def __init__(self, name: str, doc_url: Optional[str] = None):
        self.name = name
        self.doc_url = doc_url

    def get_doc_url(self, **kwargs) -> Optional[str]:
        return self.doc_url

    @abstractmethod
    def get_schema_url(self, **kwargs) -> str:
        pass

    def to_json(self, **kwargs) -> dict:
        return without_none_values({
            "doc_url": self.doc_url,
            "name": self.name,
            "schema_url": self.get_schema_url(),
        })


class GitSchemaReference(SchemaReference):
    @staticmethod
    def from_repo_url(repo_url: str, *args, **kwargs):
        repo_url_info = urlparse(repo_url)
        klass = GitHubSchemaReference \
            if repo_url_info.netloc == GITHUB_DOMAIN \
            else GitLabSchemaReference
        return klass(*args, **kwargs, repo_url=repo_url, repo_url_info=repo_url_info)

    @abstractmethod
    def __init__(self,
                 repo_url: str,
                 repo_url_info: ParseResult,
                 doc_url_by_ref: Mapping[str, str] = {},
                 schema_filename: str = DEFAULT_SCHEMA_FILENAME,
                 schema_filename_by_ref: Mapping[str, str] = {},
                 session: requests.Session = DEFAULT_SESSION,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_url_by_ref = doc_url_by_ref
        self.repo_url = repo_url
        self.repo_url_info = repo_url_info
        self.schema_filename = schema_filename
        self.schema_filename_by_ref = schema_filename_by_ref
        self.session = session
        self.project_path = repo_url_info.path.strip('/')

    @abstractmethod
    def build_schema_url(self, ref: GitRef) -> str:
        pass

    @abstractmethod
    def build_project_url(self, ref: GitRef) -> str:
        pass

    @abstractmethod
    def get_default_branch(self) -> GitRef:
        pass

    def get_doc_url(self, ref: Optional[GitRef] = None) -> Optional[str]:
        ref = self.sanitize_ref(ref)
        if self.doc_url_by_ref:
            latest_tag_doc_url = self.doc_url_by_ref.get("~latest_tag")
            if latest_tag_doc_url:
                tags = sorted(self.iter_tags(), key=by_commit_date, reverse=True)
                latest_tag = tags[0] if tags else None
                if latest_tag is not None and ref.name == latest_tag.name:
                    return latest_tag_doc_url
            ref_doc_url = self.doc_url_by_ref.get(ref.name)
            if ref_doc_url:
                return ref_doc_url
        return super().get_doc_url()

    def get_project_url(self, ref: Optional[GitRef] = None) -> str:
        ref = self.sanitize_ref(ref)
        return self.build_project_url(ref=ref)

    def get_schema_filename(self, ref: GitRef) -> str:
        ref_schema_filename = self.schema_filename_by_ref.get(ref.name)
        if ref_schema_filename:
            return ref_schema_filename
        return self.schema_filename

    def get_schema_url(self, ref: Optional[GitRef] = None) -> str:
        ref = self.sanitize_ref(ref)
        return self.build_schema_url(ref=ref)

    @abstractmethod
    def iter_branches(self) -> Iterator[GitRef]:
        """Yield branches defined in the given repository."""
        pass

    @abstractmethod
    def iter_tags(self) -> Iterator[GitRef]:
        """Yield tags defined in the given repository."""
        pass

    def sanitize_ref(self, ref: Optional[GitRef] = None) -> GitRef:
        if ref is None:
            ref = self.get_default_branch()
        elif isinstance(ref, str):
            ref = GitRef(name=ref)
        return ref

    @abstractmethod
    def to_json(self, versions=False) -> dict:
        result = {
            **super().to_json(),
            "default_branch": self.get_default_branch().name,
            "doc_url_by_ref": self.doc_url_by_ref,
            "repo_url": self.repo_url,
            "schema_filename": self.schema_filename,
            "schema_filename_by_ref": self.schema_filename_by_ref,
        }
        if versions:
            result["branches"] = {ref.name: self.get_schema_url(ref=ref) for ref in self.iter_branches()}
            result["tags"] = {ref.name: self.get_schema_url(ref=ref) for ref in self.iter_tags()}
        return without_none_values(result)


class GitHubSchemaReference(GitSchemaReference):
    RAW_BASE_URL = "https://raw.githubusercontent.com"

    def __init__(self, repo_url_info: ParseResult, session: requests.Session = DEFAULT_SESSION, *args, **kwargs):
        super().__init__(*args, **kwargs, repo_url_info=repo_url_info, session=session)
        g = github.Github(os.getenv("GITHUB_ACCESS_TOKEN"))
        # Monkey-patch Session
        g._Github__requester._Requester__createConnection()
        g._Github__requester._Requester__connection.session = session
        self.git_client = g

    def build_project_url(self, ref: GitRef) -> str:
        if ref.name == "master":
            return self.repo_url
        return '{}/tree/{}'.format(self.repo_url.rstrip('/'), ref.name)

    def build_schema_url(self, ref: GitRef) -> str:
        return "{}/{}/{}/{}".format(self.RAW_BASE_URL, self.project_path, ref.name, self.get_schema_filename(ref))

    def get_default_branch(self) -> GitRef:
        return GitRef(name=self.repo.default_branch)

    def iter_branches(self) -> Iterator[GitRef]:
        for branch in self.repo.get_branches():
            yield GitRef(name=branch.name, _source=branch)

    def iter_tags(self) -> Iterator[GitRef]:
        for tag in self.repo.get_tags():
            sha = tag.commit.sha
            committed_date = tag.commit.raw_data['commit']['committer']['date']
            commit = GitCommit(sha, committed_date=committed_date)
            yield GitRef(name=tag.name, commit=commit, _source=tag)

    @property
    def repo(self):
        return self.git_client.get_repo(self.project_path)

    def to_json(self, versions: bool = False) -> dict:
        return {
            **super().to_json(versions=versions),
            "git_type": "github",
        }


class GitLabSchemaReference(GitSchemaReference):
    def __init__(self, repo_url_info: ParseResult, session: requests.Session = DEFAULT_SESSION, *args, **kwargs):
        super().__init__(*args, **kwargs, repo_url_info=repo_url_info, session=session)
        gitlab_instance_url = '{}://{}'.format(repo_url_info.scheme, repo_url_info.netloc)
        self.git_client = gitlab.Gitlab(gitlab_instance_url, session=session)

    def build_project_url(self, ref: GitRef) -> str:
        if ref.name == "master":
            return self.repo_url
        return '{}/tree/{}'.format(self.repo_url.rstrip('/'), ref.name)

    def build_schema_url(self, ref: GitRef) -> str:
        return '{}/raw/{}/{}'.format(self.repo_url.rstrip('/'), ref.name, self.get_schema_filename(ref))

    def get_default_branch(self) -> GitRef:
        return GitRef(name=self.project.default_branch)

    def iter_branches(self) -> Iterator[GitRef]:
        for branch in self.project.branches.list():
            yield GitRef(name=branch.name, _source=branch)

    def iter_tags(self) -> Iterator[GitRef]:
        for project_tag in self.project.tags.list():
            sha = project_tag.commit['id']
            committed_date = project_tag.attributes['commit']['committed_date']
            commit = GitCommit(sha, committed_date=committed_date)
            yield GitRef(name=project_tag.name, commit=commit, _source=project_tag)

    @property
    def project(self):
        return self.git_client.projects.get(self.project_path)

    def to_json(self, versions: bool = False) -> dict:
        return {
            **super().to_json(versions=versions),
            "git_type": "gitlab",
        }


class URLSchemaReference(SchemaReference):
    def __init__(self, schema_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_url = schema_url

    def get_schema_url(self, **kwargs) -> str:
        return self.schema_url
