"""
    Copyright 2019 sbienkow

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from typing import Dict, Union, Iterable, Set, Any, Optional
from types import MappingProxyType  # Readonly dict
from datetime import datetime

# BaseClient doesn't provide typing
# so we need to ignore it
from ._BaseClient import BaseClientV2 as BaseClient


class Base:
    def __init__(self, name: str) -> None:
        self.__name: str = name

    @property
    def name(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return '{}({})'.format(type(self).__name__, self.name)


class Manifest(Base):
    def __init__(self,
                 client: BaseClient,
                 repo: str,
                 digest: str,
                 content: Union[Dict, None] = None) -> None:
        super().__init__('{}:{}'.format(repo, digest))
        self._client: BaseClient = client
        self._repo: str = repo
        self._digest: str = digest
        self._content: Union[Dict, None] = content
        self._creation_date: Union[datetime, None] = None

    @property
    def repository(self) -> str:
        return self._repo

    @property
    def content(self) -> MappingProxyType:
        if self._content is None:
            self._content, _ = self._client.get_manifest_and_digest(
                self.repository, self.digest)
        return MappingProxyType(self._content)

    @property
    def digest(self) -> str:
        return self._digest

    @property
    def creation_date(self) -> datetime:
        if self._creation_date is None:
            conf = self.content['config']
            blob = self._client.get_blob(self.repository,
                                         digest=conf['digest'],
                                         schema=conf['mediaType'])

            date_str = blob['created'].split('.')[0]
            self._creation_date = datetime.strptime(date_str,
                                                    '%Y-%m-%dT%H:%M:%S')
        return self._creation_date

    def delete(self) -> None:
        self._client.delete_manifest(self.repository, self.digest)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.digest == other.digest
                and self.repository == other.repository
                and self.content == other.content)

    def __hash__(self):
        return hash(repr(self))


class Tag(Base):
    def __init__(self, client: BaseClient, repo: str, tag: str) -> None:
        super().__init__('{}:{}'.format(repo, tag))
        self._client: BaseClient = client
        self._repo: str = repo
        self._tag: str = tag
        self._manifest: Union[Manifest, None] = None

    @property
    def repository(self) -> str:
        return self._repo

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def manifest(self) -> Manifest:
        if self._manifest is None:
            manifest, digest = self._client.get_manifest_and_digest(
                self._repo, self._tag)
            self._manifest = Manifest(self._client,
                                      self.repository,
                                      digest,
                                      manifest)
        return self._manifest

    def delete(self) -> None:
        self.manifest.delete()

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.tag == other.tag
                and self.repository == other.repository)

    def __hash__(self):
        return hash(repr(self))


class Repository(Base):
    def __init__(self, client: BaseClient, repo: str) -> None:
        super().__init__(repo)
        self._client: BaseClient = client
        self._repo: str = repo
        self.__tags: Union[Dict[str, Tag], None] = None

    @property
    def _tags(self) -> Dict[str, Tag]:
        if self.__tags is None:
            self.__tags = {
                tag: Tag(self._client, self._repo, tag)
                for tag in self._client.get_repository_tags(self._repo)['tags']
            }
        return self.__tags

    def __getitem__(self, tag) -> Tag:
        return self._tags[tag]

    def get(self, tag: str, default: Any = None) -> Optional[Tag]:
        try:
            return self[tag]
        except KeyError:
            return default

    @property
    def tags(self) -> Iterable[Tag]:
        return self._tags.values()

    def __iter__(self) -> Iterable[Tag]:
        return iter(self.tags)

    @property
    def manifests(self) -> Set[Manifest]:
        return {tag.manifest for tag in self.tags}

    def delete(self) -> None:
        for manifest in self.manifests:
            manifest.delete()

    def __eq__(self, other) -> bool:
        return self._repo == other._repo and self.tags == other.tags


class Registry(Base):
    def __init__(self,
                 host: str,
                 verify_ssl: bool = False,
                 username: str = None,
                 password: str = None,
                 api_timeout: int = None) -> None:
        super().__init__(host)
        self._client: BaseClient = BaseClient(
            host=host,
            verify_ssl=verify_ssl,
            username=username,
            password=password,
            api_timeout=api_timeout,
        )

        self.__repositories: Union[Dict[str, Repository], None] = None

    @property
    def _repositories(self) -> Dict[str, Repository]:
        if self.__repositories is None:
            self.__repositories = {
                repo: Repository(self._client, repo)
                for repo in self._client.catalog()['repositories']
            }
        return self.__repositories

    def __getitem__(self, repository: str) -> Repository:
        return self._repositories[repository]

    def get(self, repository: str, default: Any = None) -> Optional[Repository]:
        try:
            return self[repository]
        except KeyError:
            return default

    @property
    def repositories(self) -> Iterable[Repository]:
        return self._repositories.values()

    def __iter__(self) -> Iterable[Repository]:
        return iter(self.repositories)
