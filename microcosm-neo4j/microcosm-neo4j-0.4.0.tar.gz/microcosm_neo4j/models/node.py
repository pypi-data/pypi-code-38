from dataclasses import field
from typing import Sequence
from uuid import uuid4

from inflection import camelize

from microcosm_neo4j.models.entity import Entity
from microcosm_neo4j.models.index import Index


class NodeMeta(type):

    def __new__(cls, name, bases, dct):
        if name == "Node":
            return super().__new__(cls, name, bases, dct)

        # inject the id's type
        dct.setdefault("__annotations__", {}).update(
            id=str,
        )
        # inject the id's default factory
        dct.update(
            id=field(default_factory=lambda: str(uuid4())),
        )

        dct["__indexes__"] = [
            Index.unique(name, "id"),
        ] + dct.get("__indexes__", [])

        return super().__new__(cls, name, bases, dct)


class Node(Entity, metaclass=NodeMeta):
    """
    Base class for Neo4J nodes.

    """
    id: str

    __indexes__: Sequence[Index]

    @classmethod
    def label(cls) -> str:
        return camelize(cls.__name__)
