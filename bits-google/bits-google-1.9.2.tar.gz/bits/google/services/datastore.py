"""Google Datastore API client."""

from bits.google.services.base import Base
from google.cloud import datastore


class Datastore(Base):
    """Datastore class."""

    def __init__(self, project, credentials=None):
        """Initialize a class instance."""
        # uses application default credentials.
        self.client = datastore.Client(project, credentials=credentials)
        self.datastore = datastore

    def list_entities(self, kind):
        """Return a list of all entities of a given kind."""
        query = self.client.query(kind=kind)
        return list(query.fetch())

    def list_entities_dict(self, kind):
        """Return a dict of all entities of a given kind."""
        entities = {}
        query = self.client.query(kind=kind)
        for entity in query.fetch():
            entity_key = entity.key.id
            if not entity_key:
                entity_key = entity.key.name
            entities[entity_key] = entity
        return entities
