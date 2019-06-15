from typing import Optional
from typing import List
from injector import inject

from gumo.core import GumoConfiguration
from gumo.core.injector import injector

from gumo.core.application.entity_key import KeyIDAllocator
from gumo.core.domain.entity_key import NoneKey
from gumo.core.domain.entity_key import EntityKey
from gumo.core.domain.entity_key import EntityKeyFactory
from gumo.core.domain.entity_key import IncompleteKey

from gumo.datastore.infrastructure.repository import DatastoreClientFactory

from google.cloud import datastore


class _KeyMapper:
    @inject
    def __init__(
            self,
            gumo_config: GumoConfiguration,
            entity_key_factory: EntityKeyFactory,
    ):
        self._gumo_config = gumo_config
        self._entity_key_factory = entity_key_factory

    def to_datastore_key(self, incomplete_key: IncompleteKey) -> Optional[datastore.Key]:
        if incomplete_key is None or isinstance(incomplete_key, NoneKey):
            return None

        project = self._gumo_config.google_cloud_project.value
        datastore_key = datastore.Key(*incomplete_key.flat_pairs(), project=project)

        return datastore_key

    def to_entity_key(self, datastore_key: Optional[datastore.Key]) -> EntityKey:
        if datastore_key is None:
            return NoneKey.get_instance()

        entity_key = self._entity_key_factory.build_from_pairs(pairs=datastore_key.path)
        return entity_key


class CachedKeyIDAllocator:
    ALLOCATE_BATCH_SIZE = 10

    _datastore_client = None

    @inject
    def __init__(
            self,
            key_mapper: _KeyMapper,
    ):
        self.key_mapper = key_mapper

        self._cache = {}

    @property
    def datastore_client(self) -> datastore.Client:
        if self._datastore_client is None:
            factory = injector.get(DatastoreClientFactory)  # type: DatastoreClientFactory
            self._datastore_client = factory.build()

        return self._datastore_client

    def allocate_keys(self, incomplete_key: IncompleteKey) -> List[EntityKey]:
        datastore_key = self.key_mapper.to_datastore_key(incomplete_key=incomplete_key)
        allocated_keys = self.datastore_client.allocate_ids(
            incomplete_key=datastore_key,
            num_ids=self.ALLOCATE_BATCH_SIZE
        )
        return [
            self.key_mapper.to_entity_key(datastore_key=key)
            for key in allocated_keys
        ]

    def fetch_cached_keys(self, incomplete_key: IncompleteKey) -> List[EntityKey]:
        return self._cache.get(incomplete_key.key_literal(), [])

    def allocate(self, incomplete_key: IncompleteKey) -> EntityKey:
        cached_keys = self.fetch_cached_keys(incomplete_key=incomplete_key)
        if len(cached_keys) == 0:
            cached_keys = self.allocate_keys(incomplete_key=incomplete_key)

        key = cached_keys[0]
        del cached_keys[0]
        self._cache[incomplete_key.key_literal()] = cached_keys

        return key


class DatastoreKeyIDAllocator(KeyIDAllocator):
    ALLOCATE_BATCH_SIZE = 10

    @inject
    def __init__(
            self,
            cached_allocator: CachedKeyIDAllocator,
    ):
        self._cached_allocator = cached_allocator

    def allocate(self, incomplete_key: IncompleteKey) -> EntityKey:
        return self._cached_allocator.allocate(incomplete_key=incomplete_key)
