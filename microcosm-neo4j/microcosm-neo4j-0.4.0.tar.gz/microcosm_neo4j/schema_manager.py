"""
Simplistic management of indexes and constraints.

"""
from typing import Set

from microcosm_neo4j.context import SessionContext, transaction
from microcosm_neo4j.models import Index, IndexType, Node


# XXX need to flesh out unit tests for schema management


class SchemaManager:
    """
    Manage Neo4J "schema" of indexes and constraints.

    See:

     -  https://neo4j.com/docs/cypher-manual/current/schema/index/
     -  https://neo4j.com/docs/cypher-manual/current/schema/constraints/

    """
    def __init__(self, graph):
        self.graph = graph

    @property
    def session(self):
        return SessionContext.session

    def recreate_all(self) -> None:
        """
        Reset the database.

        """
        self.drop_all()
        self.create_all()

    def create_all(self) -> None:
        """
        Create all indexes and constraints that do not exist.

        """
        with transaction():
            for index in self.desired_indexes() - self.existing_indexes():
                self.session.run(self._create_index(index))

    def drop_all(self, force=False) -> None:
        """
        Drop all indexes, constraints, and data.

        The technique used for droppin data is only suitable for unit tests and is disabled outside
        of tests unless `force` is set to True.

        Any use case with large numbers of nodes should implement mass deletion at the file system level.

        """
        with transaction():
            for index in self.existing_indexes():
                self.session.run(self._drop_index(index))

        if not self.graph.metadata.testing and not force:
            return

        # NB: data and index/constraint operations cannot run in the same transaction
        with transaction():
            self.session.run(self._drop_nodes())

    def desired_indexes(self) -> Set[Index]:
        return {
            index
            for model_class in Node.__subclasses__()
            for index in model_class.__indexes__
        }

    def existing_indexes(self) -> Set[Index]:
        records = list(self.session.run("CALL db.indexes"))
        return {
            Index(
                key=record.get("properties")[0],
                label=record.get("tokenNames")[0],
                type=IndexType(record.get("type")),
            )
            for record in records
        }

    def _create_index(self, index: Index) -> str:
        if index.is_unique:
            return f"CREATE CONSTRAINT ON (node:{index.label}) ASSERT node.{index.key} IS UNIQUE"
        else:
            return f"CREATE INDEX ON :{index.label}({index.key})"

    def _drop_index(self, index: Index) -> str:
        if index.is_unique:
            return f"DROP CONSTRAINT ON (node:{index.label}) ASSERT node.{index.key} IS UNIQUE"
        else:
            return f"DROP INDEX ON :{index.label}({index.key})"

    def _drop_nodes(self) -> str:
        return "MATCH (n) DETACH DELETE n"
