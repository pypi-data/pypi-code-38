from dataclasses import asdict, fields
from inspect import isclass
from typing import Mapping, Set
from uuid import UUID

from microcosm_neo4j.models.types import PropertyType


class Entity:
    """
    Base class for Neo4J entities.

    Default implementation assumes use of `@dataclass`.

    """
    @classmethod
    def matching_properties(cls, **kwargs) -> Mapping[str, PropertyType]:
        return {
            key: str(kwargs[key]) if isinstance(kwargs[key], UUID) else kwargs[key]
            for key in cls.property_names().intersection(kwargs.keys())
        }

    def properties(self) -> Mapping[str, PropertyType]:
        """
        Return the properties of this entity.

        Do not return null properties.

        See: https://neo4j.com/docs/cypher-manual/current/syntax/working-with-null/

        """
        return {
            key: value
            for key, value in asdict(self).items()
            # NB: nested dataclasses will be converted to dicts
            if value is not None and not isinstance(value, dict)
        }

    @classmethod
    def property_names(cls) -> Set[str]:
        """
        Return the property names of this entity type.

        """
        return {
            field.name
            for field in fields(cls)
            if not isclass(field.type) or not issubclass(field.type, Entity)
        }
