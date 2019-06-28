from google.cloud import firestore

from secure_scaffold.contrib.db.engine.base import BaseEngine


class FirestoreEngine(BaseEngine):
    CLIENT = firestore.Client

    def _create(self, model):
        """
        # Create document in the Firestore and return the ID
        Create document in the Datastore
        """

        doc = self.client.collection(model.collection).add(model.to_dict())
        model.id = doc[1].id
        model._created_at = doc[0].ToDatetime()

        return model.id

    def save(self, model):
        """
        Save document to the Firestore using ID
        if the ID is not defined then create it instead
        """
        if model.id:
            self.client.collection(model.collection).document(model.id).set(model.to_dict())
        else:
            self._create(model)

    def get(self, model, id=None, **kwargs):
        if id:
            doc = self.client.collection(model.collection).document(id).get()
            yield model(id=doc.id, date=doc.create_time.ToDatetime(), **doc.to_dict())
        else:
            doc = self.client.collection(model.collection)
            for key, value in kwargs.items():
                doc = doc.where(key, '==', value)
            docs = doc.get()

            for doc in docs:
                yield model(id=doc.id, date=doc.create_time.ToDatetime(), **doc.to_dict())

    def get_all(self, model):
        """
        Yield all the documents in this collection.

        :yield: List of docs, e.g. [User, ..] or
        """
        docs = self.client.collection(model.collection).get()
        for doc in docs:
            yield model(id=doc['_id'], **doc)

    def delete(self, model):
        raise NotImplementedError()
