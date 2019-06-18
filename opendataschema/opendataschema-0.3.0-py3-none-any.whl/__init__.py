import itertools
import json
import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, List
from urllib.parse import ParseResult, urlparse

import github
import gitlab
import jsonschema
import requests

log = logging.getLogger(__name__)


DEFAULT_SCHEMA_FILENAME = "schema.json"
GITHUB_DOMAIN = "github.com"
CATALOG_SCHEMA_URL = "https://opendataschema.frama.io/catalog/schema-catalog.json"


@dataclass
class GitRef:
    """Represent a Git reference (branch or tag) in a platform (i.e. GitLab/GitHub) agnostic way."""
    name: str
    _source: Any = None


@dataclass
class GitBranch(GitRef):
    default: bool = False  # Is the reference the default branch?


@dataclass
class GitTag(GitRef):
    pass


DEFAULT_GIT_REF = GitBranch(name="master", default=True)

DEFAULT_SESSION = requests.Session()


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

    def get_refs(self) -> List[GitRef]:
        return sorted(self.iter_refs(), key=lambda ref: ref.name)

    def get_schema_url(self, ref: GitRef = DEFAULT_GIT_REF, check_exists: bool = True, **kwargs) -> str:
        if isinstance(ref, str):
            ref = GitRef(name=ref)
        if check_exists:
            ref_names = [ref.name for ref in self.get_refs()]
            if ref.name not in ref_names:
                raise ValueError("Git ref \"{}\" does not exist in repo \"{}\"".format(ref.name, self.repo_url))
        return self.build_schema_url(ref=ref)

    @abstractmethod
    def iter_refs(self) -> Iterator[GitRef]:
        """Yield tags and branches defined in the given repository."""
        pass

    @abstractmethod
    def to_json(self, versions=False, **kwargs) -> dict:
        refs = self.get_refs()
        result = {
            "doc_url": self.doc_url,
            "name": self.name,
            "repo_url": self.repo_url,
            "schema_filename": self.schema_filename,
            "schema_url": self.get_schema_url()
        }
        if versions:
            result["versions"] = {ref: self.get_schema_url(ref=ref, check_exists=False) for ref in refs}
        return without_none_values(result)


class GitHubSchemaReference(GitSchemaReference):
    RAW_BASE_URL = "https://raw.githubusercontent.com"

    def __init__(self, repo_url_info: ParseResult, session: requests.Session = DEFAULT_SESSION, *args, **kwargs):
        super().__init__(*args, **kwargs, repo_url_info=repo_url_info, session=session)
        g = github.Github()
        # Monkey-patch Session
        g._Github__requester._Requester__createConnection()
        g._Github__requester._Requester__connection.session = session
        self.git_client = g

    def build_schema_url(self, ref: GitRef) -> str:
        return "{}/{}/{}/{}".format(self.RAW_BASE_URL, self.project_path, ref.name, self.schema_filename)

    def iter_refs(self) -> Iterator[GitRef]:
        repo = self.git_client.get_repo(self.project_path)
        default_branch_name = repo.default_branch
        for branch in repo.get_branches():
            default = branch.name == default_branch_name
            yield GitBranch(name=branch.name, default=default, _source=branch)
        for tag in repo.get_tags():
            yield GitTag(name=tag.name, _source=tag)

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

    def iter_refs(self) -> Iterator[GitRef]:
        project = self.git_client.projects.get(self.project_path)
        for branch in project.branches.list():
            yield GitBranch(name=branch.name, default=branch.default, _source=branch)
        for project_tag in project.tags.list():
            yield GitTag(name=project_tag.name, _source=project_tag)

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
