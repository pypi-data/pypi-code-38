from dataclasses import dataclass
from enum import Enum, unique


@unique
class IndexType(Enum):
    """
    See: https://fossies.org/linux/neo4j/community/kernel/src/main/java/org/neo4j/kernel/builtinprocs/BuiltInProcedures.java  # noqa: E501

    """
    NODE_LABEL_PROPERTY = "node_label_property"
    NODE_UNIQUE_PROPERTY = "node_unique_property"


@dataclass(frozen=True)
class Index:
    label: str
    # NB: support for "Node Keys" is not implemented
    key: str
    type: IndexType = IndexType.NODE_LABEL_PROPERTY

    @property
    def is_unique(self) -> bool:
        return self.type == IndexType.NODE_UNIQUE_PROPERTY

    @classmethod
    def unique(cls, label: str, key: str) -> "Index":
        return cls(
            label=label,
            key=key,
            type=IndexType.NODE_UNIQUE_PROPERTY,
        )
