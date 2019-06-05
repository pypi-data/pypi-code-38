from typing import (
    Mapping,
    Set,
    Type,
    TypeVar,
)

from opencypher.api import (
    expr,
    func,
    match,
    merge,
    node,
    parameters,
)
from opencypher.ast import Cypher

from microcosm_neo4j.models.node import Node
from microcosm_neo4j.models.types import PropertyType
from microcosm_neo4j.stores.base import Store


N = TypeVar("N", bound=Node)


class NodeStore(Store[N]):
    """
    Expose node persistence operations using `neo4j-driver`.

    """
    def __init__(self, graph, model_class: Type[N]):
        super().__init__(graph, model_class, "nodes_deleted")

    @property
    def variable(self) -> str:
        return "n"

    def _count(self, **kwargs) -> int:
        return match(
            node(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(**kwargs),
            ),
        ).ret(
            func.count(self.variable).as_("count"),
        )

    def _create(self, instance: N) -> Cypher:
        assignments = parameters(
            key_prefix=self.variable,
            name_prefix=self.variable,
            **self._value_properties(instance),
        )
        return merge(
            node(
                self.variable,
                instance.__class__.label(),
                properties=self._unique_properties(instance),
            ),
        ).set(
            assignments[0],
            *assignments[1:],
        ).ret(
            expr(self.variable),
        )

    def _delete(self, identifier: str) -> Cypher:
        return match(
            node(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(
                    id=str(identifier),
                ),
            ),
        ).delete(
            self.variable,
        )

    def _retrieve(self, identifier: str) -> Cypher:
        return match(
            node(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(
                    id=str(identifier),
                ),
            ),
        ).ret(
            expr(self.variable),
        )

    def _search(self, limit=None, offset=None, **kwargs) -> Cypher:
        return match(
            node(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(**kwargs),
            ),
        ).ret(
            expr(self.variable),
            limit=limit,
            skip=offset,
        )

    def _unique_properties(self, instance: N) -> Mapping[str, PropertyType]:
        keys = self._unique_keys(instance)
        return {
            key: value
            for key, value in instance.properties().items()
            if key in keys
        }

    def _value_properties(self, instance: N) -> Mapping[str, PropertyType]:
        keys = self._unique_keys(instance)
        return {
            key: value
            for key, value in instance.properties().items()
            if key not in keys
        }

    def _unique_keys(self, instance: N) -> Set[str]:
        return {
            index.key
            for index in instance.__indexes__
            if index.unique and "id" != index.key
        }
