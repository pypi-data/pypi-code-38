from typing import Optional
from datalogue.models.datastore import DatastoreDef
from datalogue.models.credentials import Credentials


class Datastore:
    def __init__(self, definition: DatastoreDef, credentials: Credentials):
        self.definition = definition
        self.credentials = credentials

    def _as_payload(self) -> dict:
        base = self.definition._as_payload().copy()
        if self.credentials is not None:
            base.update(self.credentials._as_payload())
        return base