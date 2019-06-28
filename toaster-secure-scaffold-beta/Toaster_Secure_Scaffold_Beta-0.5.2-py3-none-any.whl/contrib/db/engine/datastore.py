from datetime import datetime

from google.cloud import datastore

from secure_scaffold.contrib.db.engine.base import BaseEngine


class DatastoreEngine(BaseEngine):
    CLIENT = datastore.Client

    def _key(self, model):
        return self.client.key(model.collection, model.id)

    def _create(self, model):
        """
        # Create document in the Firestore and return the ID
        Create document in the Datastore
        """
        entity = datastore.Entity(self._key(model))
        data = model.to_dict()
        data['_created_at'] = datetime.now()
        data['_id'] = model.id
        entity.update(data)
        self.client.put(entity)
        model.created_time = data['_created_at']

        return model.id

    def save(self, model):
        """
        Save document to the Firestore using ID
        if the ID is not defined then create it instead
        """
        if not model._created_at:
            return self._create(model)
        data = model.to_dict()
        data['_id'] = model.id
        entity = datastore.Entity(
            self._key(model)
        )
        entity.update(data)
        self.client.put(entity)
        return model.id

    def get(self, model, id=None, **kwargs):
        if id:
            key = self.client.key(model.collection, id)
            entity = self.client.get(key)
            yield model(id=id, **entity)

        else:
            query = self.client.query(kind=model.collection)

            for key, value in kwargs.items():
                query = query.add_filter(key, '=', value)

            for doc in query.fetch():
                yield model(id=doc['_id'], **doc)

    def get_all(self, model):
        """
        Get all documents in this collection as a list
        :return: List of docs, e.g. [User, ..] or User
        """
        docs = self.client.query(kind=model.collection).fetch()
        for doc in docs:
            yield model(id=doc['_id'], **doc)

    def delete(self, model):
        self.client.delete(self._key(model))
