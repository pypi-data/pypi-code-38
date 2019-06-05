from typing import (
    Generic,
    Sequence,
    Type,
    TypeVar,
)

from neo4j import Session
from opencypher.ast import Cypher

from microcosm_neo4j.context import SessionContext
from microcosm_neo4j.errors import MissingDependencyError
from microcosm_neo4j.models.entity import Entity
from microcosm_neo4j.query import all_records, one_record, run


T = TypeVar("T", bound=Entity)


class Store(Generic[T]):

    def __init__(self, graph, model_class: Type[T], deleted_count_property: str):
        self.graph = graph
        self.model_class = model_class
        self.deleted_count_property = deleted_count_property

    @property
    def session(self) -> Session:
        return SessionContext.session

    def make(self, **kwargs) -> T:
        return self.model_class(**kwargs)  # type: ignore

    def count(self, **kwargs) -> int:
        """
        Count matching entities.

        May not be efficient.

        See: https://neo4j.com/developer/kb/fast-counts-using-the-count-store/

        """
        query = self._count(**kwargs)
        value = run(self.session, query).single()
        return value["count"]

    def create(self, instance: T) -> T:
        query = self._create(instance)

        records = all_records(self.session, query)
        if not records:
            raise MissingDependencyError()

        # NB: It's possible for a MERGE to find multiple results if there isn't an underlying
        # uniqueness constraint (which there cannot be in Neo4J for relationships).
        # If previous CREATE operations inserted multiple matchin entities the result set will
        # include multiple records.
        #
        # We arbitrarily take the first such record.
        record = records[0]
        return self.make(**record)

    def delete(self, identifier: str) -> bool:
        query = self._delete(identifier)
        result = run(self.session, query)
        counters = result.summary().counters
        return getattr(counters, self.deleted_count_property)

    def retrieve(self, identifier: str) -> T:
        query = self._retrieve(identifier)
        record = one_record(self.session, query)
        return self.make(**record)

    def search(self, **kwargs) -> Sequence[T]:
        query = self._search(**kwargs)
        records = all_records(self.session, query)
        return [
            self.make(**record)
            for record in records
        ]

    def _count(self, **kwargs) -> Cypher:
        raise NotImplementedError

    def _create(self, instance: T) -> Cypher:
        raise NotImplementedError

    def _delete(self, identifier: str) -> Cypher:
        raise NotImplementedError

    def _retrieve(self, identifier: str) -> Cypher:
        raise NotImplementedError

    def _search(self, **kwargs) -> Cypher:
        raise NotImplementedError
