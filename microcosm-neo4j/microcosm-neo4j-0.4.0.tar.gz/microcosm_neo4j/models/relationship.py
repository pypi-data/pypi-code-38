from dataclasses import dataclass, field
from typing import Type, TypeVar
from uuid import uuid4

from inflection import underscore

from microcosm_neo4j.models.entity import Entity
from microcosm_neo4j.models.node import Node


# XXX should try to simplify the relationship interface


In = TypeVar("In", bound=Node)
Out = TypeVar("Out", bound=Node)


class RelationshipMeta(type):

    def __new__(cls, name, bases, dct):
        if name == "Relationship":
            return super().__new__(cls, name, bases, dct)

        # inject the id's type
        dct.setdefault("__annotations__", {}).update(
            id=str,
        )
        # inject the id's default factory
        dct.update(
            id=field(default_factory=lambda: str(uuid4())),
        )
        return super().__new__(cls, name, bases, dct)


@dataclass(frozen=False)
class Relationship(Entity, metaclass=RelationshipMeta):
    """
    Base class for Neo4J relationships.

    """
    in_id: str
    out_id: str

    @classmethod
    def label(cls) -> str:
        return underscore(cls.__name__).upper()

    @classmethod
    def in_class(cls) -> Type[Node]:
        raise NotImplementedError("Relationship subclasses must implement in_class() classmethod")

    @classmethod
    def out_class(cls) -> Type[Node]:
        raise NotImplementedError("Relationship subclasses must implement out_class() classmethod")
