import itertools
import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import gitlab
import jsonschema
import requests
import tableschema
import toml
from cachetools.func import ttl_cache

from . import github_api, gitlab_api

log = logging.getLogger(__name__)

DEFAULT_GIT_REF = "master"
DEFAULT_SCHEMA_FILENAME = "schema.json"
GITHUB = "github"
GITHUB_DOMAIN = "github.com"
GITLAB = "gitlab"
SCHEMA_CATALOG_JSON_SCHEMA_URL = "https://framagit.org/opendataschema/spec/raw/master/schema.json"


def without_none_values(data_dict):
    """Keep only keys whose value is not None"""
    return {k: v
            for k, v in data_dict.items()
            if v is not None}


def is_http_url(url):
    return re.match("https?://", url)


def load_json_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def load_text_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def load_text_from_file(path):
    if isinstance(path, str):
        path = Path(path)
    return path.read_text()


class TableSchemaCatalog:

    def __init__(self, path_or_url):
        if isinstance(path_or_url, Path):
            path_or_url = str(path_or_url)

        toml_content = load_text_from_url(path_or_url) \
            if is_http_url(path_or_url) \
            else load_text_from_file(path_or_url)

        descriptor = toml.loads(toml_content)
        self.descriptor = descriptor

        schema = load_json_from_url(SCHEMA_CATALOG_JSON_SCHEMA_URL)
        jsonschema.validate(instance=descriptor, schema=schema)

        self.references = {
            name: TableSchemaReference.from_config(config)
            for name, config in self.descriptor.items()
        }


class TableSchemaReference(ABC):

    @classmethod
    def from_config(cls, config: dict):
        options = {**without_none_values(config)}
        repo_url = options.pop("repo_url", None)
        schema_url = options.pop("schema_url", None)
        if repo_url:
            return GitTableSchemaReference(repo_url, **options)
        elif schema_url:
            return URLTableSchemaReference(schema_url, **options)
        assert False, config  # config has been validated by JSON Schema

    @abstractmethod
    def get_schema_url(self, **kwargs):
        pass

    def get_table_schema(self, **kwargs):
        schema_url = self.get_schema_url(**kwargs)
        return tableschema.Schema(schema_url)

    @abstractmethod
    def to_json(self, **kwargs):
        pass


class GitTableSchemaReference(TableSchemaReference):

    def __init__(self, repo_url: str, schema_filename=DEFAULT_SCHEMA_FILENAME, doc_url=None):
        self.repo_url = repo_url
        self.repo_url_info = urlparse(repo_url)
        self.project_path = self.repo_url_info.path.strip('/')
        self.schema_filename = schema_filename
        self.doc_url = doc_url
        self.git_type = GITHUB if self.repo_url_info.netloc == GITHUB_DOMAIN else GITLAB
        if self.git_type == GITLAB:
            self.gitlab_instance_url = '{}://{}'.format(self.repo_url_info.scheme, self.repo_url_info.netloc)
            self.gl = gitlab.Gitlab(self.gitlab_instance_url)

    def get_refs(self):
        return sorted(itertools.chain.from_iterable(self.get_refs_by_type().values()))

    @ttl_cache(maxsize=128, ttl=5*60)
    def get_refs_by_type(self):
        if self.git_type == GITHUB:
            refs_iterator = github_api.iter_refs(self.project_path)
        elif self.git_type == GITLAB:
            refs_iterator = gitlab_api.iter_refs(self.gl, self.project_path)
        else:
            assert False, self.git_type
        result = defaultdict(list)
        for ref_type, ref in refs_iterator:
            result[ref_type].append(ref)
        return {k: sorted(v) for k, v in result.items()}

    def get_schema_url(self, ref=DEFAULT_GIT_REF, check_exists=True, **kwargs):
        if check_exists:
            refs = self.get_refs()
            if ref not in refs:
                raise ValueError("Git ref \"{}\" does not exist in repo \"{}\"".format(ref, self.repo_url))

        if self.git_type == GITHUB:
            return github_api.build_schema_url(self.project_path, ref, self.schema_filename)
        elif self.git_type == GITLAB:
            return gitlab_api.build_schema_url(self.repo_url, ref, self.schema_filename)
        else:
            assert False, self.git_type

    def to_json(self, versions=False, **kwargs):
        refs = self.get_refs()
        result = {
            "doc_url": self.doc_url,
            "git_type": self.git_type,
            "repo_url": self.repo_url,
            "schema_filename": self.schema_filename,
            "schema_url": self.get_schema_url()
        }
        if versions:
            result["versions"] = {ref: self.get_schema_url(ref=ref, check_exists=False) for ref in refs}
        return without_none_values(result)


class URLTableSchemaReference(TableSchemaReference):

    def __init__(self, schema_url: str, doc_url=None):
        self.schema_url = schema_url
        self.doc_url = doc_url

    def get_schema_url(self, **kwargs):
        return self.schema_url

    def to_json(self, **kwargs):
        return without_none_values({
            "doc_url": self.doc_url,
            "schema_url": self.schema_url,
        })
