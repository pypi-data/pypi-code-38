import itertools
import json
import logging
import os
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterator, List, Optional
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


class GitCommit:
    """A Git commit in a platform (i.e. GitLab/GitHub) agnostic way."""

    def __init__(self, committed_date=None, _source=None):
        self.committed_date = committed_date
        self._source = None


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
        options = {**without_none_values(config)}
        name = options.pop("name")  # required
        repo_url = options.pop("repo_url", None)
        schema_url = options.pop("schema_url", None)
        if repo_url:
            return GitSchemaReference.from_repo_url(name, repo_url, **options, session=session)
        elif schema_url:
            return URLSchemaReference(name, schema_url, **options)
        assert False, config  # Should not happen because config has already been validated by JSON Schema.

    @abstractmethod
    def get_schema_url(self, **kwargs):
        pass

    @abstractmethod
    def to_json(self, **kwargs):
        pass


class GitSchemaReference(SchemaReference):
    @staticmethod
    def from_repo_url(name: str, repo_url: str, *args, **kwargs):
        repo_url_info = urlparse(repo_url)
        klass = GitHubSchemaReference \
            if repo_url_info.netloc == GITHUB_DOMAIN \
            else GitLabSchemaReference
        return klass(*args, **kwargs, name=name, repo_url=repo_url, repo_url_info=repo_url_info)

    @abstractmethod
    def __init__(self, name: str, repo_url: str, repo_url_info: ParseResult,
                 schema_filename: str = DEFAULT_SCHEMA_FILENAME, doc_url: str = None,
                 session: requests.Session = DEFAULT_SESSION):
        self.name = name
        self.repo_url = repo_url
        self.repo_url_info = repo_url_info
        self.schema_filename = schema_filename
        self.doc_url = doc_url
        self.session = session
        self.project_path = repo_url_info.path.strip('/')

    @abstractmethod
    def build_schema_url(self, ref: GitRef) -> str:
        pass

    @abstractmethod
    def get_default_branch(self) -> GitRef:
        pass

    def get_latest_tag(self) -> Optional[GitRef]:
        def by_commit_date(tag):
            return tag.commit.committed_date if tag.commit else date.min
        tags = sorted(self.iter_tags(), key=by_commit_date, reverse=True)
        return tags[0] if tags else None

    def get_schema_url(self, ref: GitRef = None) -> str:
        if ref is None:
            ref = self.get_default_branch()
        elif isinstance(ref, str):
            ref = GitRef(name=ref)
        return self.build_schema_url(ref=ref)

    @abstractmethod
    def iter_branches(self) -> Iterator[GitRef]:
        """Yield branches defined in the given repository."""
        pass

    def iter_refs(self) -> Iterator[GitRef]:
        return itertools.chain(self.iter_branches(), self.iter_tags())

    @abstractmethod
    def iter_tags(self) -> Iterator[GitRef]:
        """Yield tags defined in the given repository."""
        pass

    @abstractmethod
    def to_json(self, versions=False, **kwargs) -> dict:
        result = {
            "default_branch": self.get_default_branch().name,
            "doc_url": self.doc_url,
            "name": self.name,
            "repo_url": self.repo_url,
            "schema_filename": self.schema_filename,
            "schema_url": self.get_schema_url(),
        }
        if versions:
            result["versions"] = {ref.name: self.get_schema_url(ref=ref) for ref in self.iter_refs()}
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

    def build_schema_url(self, ref: GitRef) -> str:
        return "{}/{}/{}/{}".format(self.RAW_BASE_URL, self.project_path, ref.name, self.schema_filename)

    def get_default_branch(self) -> GitRef:
        return GitRef(name=self.repo.default_branch)

    def iter_branches(self) -> Iterator[GitRef]:
        for branch in self.repo.get_branches():
            yield GitRef(name=branch.name, _source=branch)

    def iter_tags(self) -> Iterator[GitRef]:
        for tag in self.repo.get_tags():
            committed_date = tag.commit.raw_data['commit']['committer']['date']
            commit = GitCommit(committed_date=committed_date)
            yield GitRef(name=tag.name, commit=commit, _source=tag)

    @property
    def repo(self):
        return self.git_client.get_repo(self.project_path)

    def to_json(self, versions: bool = False, **kwargs) -> dict:
        result = super().to_json(versions=versions, **kwargs)
        result["git_type"] = "github"
        return result


class GitLabSchemaReference(GitSchemaReference):
    def __init__(self, repo_url_info: ParseResult, session: requests.Session = DEFAULT_SESSION, *args, **kwargs):
        super().__init__(*args, **kwargs, repo_url_info=repo_url_info, session=session)
        gitlab_instance_url = '{}://{}'.format(repo_url_info.scheme, repo_url_info.netloc)
        self.git_client = gitlab.Gitlab(gitlab_instance_url, session=session)

    def build_schema_url(self, ref: GitRef) -> str:
        return '{}/raw/{}/{}'.format(self.repo_url.rstrip('/'), ref.name, self.schema_filename)

    def get_default_branch(self) -> GitRef:
        return GitRef(name=self.project.default_branch)

    def iter_branches(self) -> Iterator[GitRef]:
        for branch in self.project.branches.list():
            yield GitRef(name=branch.name, _source=branch)

    def iter_tags(self) -> Iterator[GitRef]:
        for project_tag in self.project.tags.list():
            committed_date = project_tag.attributes['commit']['committed_date']
            commit = GitCommit(committed_date=committed_date)
            yield GitRef(name=project_tag.name, commit=commit, _source=project_tag)

    @property
    def project(self):
        return self.git_client.projects.get(self.project_path)

    def to_json(self, versions: bool = False, **kwargs) -> dict:
        result = super().to_json(versions=versions, **kwargs)
        result["git_type"] = "gitlab"
        return result


class URLSchemaReference(SchemaReference):
    def __init__(self, name: str, schema_url: str, doc_url: str = None):
        self.name = name
        self.schema_url = schema_url
        self.doc_url = doc_url

    def get_schema_url(self, **kwargs) -> str:
        return self.schema_url

    def to_json(self, **kwargs) -> str:
        return without_none_values({
            "doc_url": self.doc_url,
            "name": self.name,
            "schema_url": self.schema_url,
        })
