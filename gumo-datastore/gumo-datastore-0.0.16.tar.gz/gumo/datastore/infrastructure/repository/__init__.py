from injector import inject
from contextlib import contextmanager

from gumo.core.injector import injector

from gumo.core import GumoConfiguration
from gumo.datastore import DatastoreConfiguration

from gumo.datastore.infrastructure.entity_key_mapper import EntityKeyMapper

from google.cloud import datastore


class DatastoreClientFactory:
    @inject
    def __init__(
            self,
            gumo_config: GumoConfiguration,
            datastore_config: DatastoreConfiguration
    ):
        self._gumo_config = gumo_config
        self._datastore_config = datastore_config

    def build(self) -> datastore.Client:
        return datastore.Client(
            project=self._gumo_config.google_cloud_project.value,
            namespace=self._datastore_config.namespace,
        )


class DatastoreRepositoryMixin:
    _datastore_client = None
    _entity_key_mapper = None

    DatastoreEntity = datastore.Entity

    @property
    def datastore_client(self) -> datastore.Client:
        if self._datastore_client is None:
            factory = injector.get(DatastoreClientFactory)  # type: DatastoreClientFactory
            self._datastore_client = factory.build()

        return self._datastore_client

    @property
    def entity_key_mapper(self) -> EntityKeyMapper:
        if self._entity_key_mapper is None:
            self._entity_key_mapper = injector.get(EntityKeyMapper)  # type: EntityKeyMapper

        return self._entity_key_mapper


@contextmanager
def datastore_transaction():
    datastore_client = injector.get(DatastoreClientFactory).build()  # type: datastore.Client

    with datastore_client.transaction():
        yield
