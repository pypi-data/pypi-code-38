from gumo.datastore.infrastructure.repository import DatastoreRepositoryMixin


class DatastoreRepositoryMixinForTest(DatastoreRepositoryMixin):
    KIND = None

    def cleanup_entities(self):
        if self.KIND is None:
            raise RuntimeError('KIND must be present.')

        query = self.datastore_client.query(kind=self.KIND)
        query.keys_only()
        self.datastore_client.delete_multi(keys=[entity.key for entity in query.fetch()])

    def count_entities(self) -> int:
        if self.KIND is None:
            raise RuntimeError('KIND must be present.')

        query = self.datastore_client.query(kind=self.KIND)
        query.keys_only()
        return len(list(query.fetch()))
