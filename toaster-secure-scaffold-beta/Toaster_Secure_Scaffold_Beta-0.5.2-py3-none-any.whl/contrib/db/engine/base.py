class BaseEngine:
    _CLIENT = None

    def __init__(self, **kwargs):

        self.client = self._CLIENT(**kwargs)

    def get(self, model, id=None, **kwargs):
        raise NotImplementedError()

    def _create(self, model):
        """
        # Create document in the Firestore and return the ID
        Create document in the Datastore
        """
        raise NotImplementedError()

    def save(self, model):
        raise NotImplementedError()

    def get_all(self, model):
        """
        Get all documents in this collection as a list
        :return: List of docs, e.g. [User, ..] or User
        """
        raise NotImplementedError()

    def delete(self, model):
        raise NotImplementedError()
