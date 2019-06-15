from injector import inject

from typing import Optional
from typing import Union
from google.cloud import datastore

from gumo.core import GumoConfiguration

from gumo.core import EntityKey
from gumo.core import NoneKey
from gumo.core import EntityKeyFactory


class EntityKeyMapper:
    @inject
    def __init__(
            self,
            gumo_config: GumoConfiguration,
            entity_key_factory: EntityKeyFactory,
    ):
        self._gumo_config = gumo_config
        self._entity_key_factory = entity_key_factory

    def to_entity_key(self, datastore_key: Optional[datastore.Key]) -> EntityKey:
        if datastore_key is None:
            return NoneKey.get_instance()

        entity_key = self._entity_key_factory.build_from_pairs(pairs=datastore_key.path)
        return entity_key

    def to_datastore_key(self, entity_key: Union[EntityKey, NoneKey, None]) -> Optional[datastore.Key]:
        if entity_key is None or isinstance(entity_key, NoneKey):
            return None

        project = self._gumo_config.google_cloud_project.value
        datastore_key = datastore.Key(*entity_key.flat_pairs(), project=project)

        return datastore_key
