from typing import Type, TypeVar

from opencypher.api import (
    expr,
    func,
    match,
    node,
)
from opencypher.ast import Cypher

from microcosm_neo4j.models.relationship import Relationship
from microcosm_neo4j.stores.base import Store


R = TypeVar("R", bound=Relationship)


class RelationshipStore(Store[R]):
    """
    Expose persistence operations using `neo4j-driver`.

    """
    def __init__(self, graph, model_class: Type[R]):
        super().__init__(graph, model_class, "relationships_deleted")

    @property
    def variable(self) -> str:
        return "r"

    def _count(self, **kwargs) -> Cypher:
        return match(
            node(
                "in",
                self.model_class.in_class().label(),
            ).rel_in(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(**kwargs),
            ).node(
                "out",
                self.model_class.out_class().label(),
            ),
        ).ret(
            func.count(self.variable).as_("count"),
        )

    def _create(self, instance: R) -> Cypher:
        return match(
            node(
                "in",
                instance.in_class().label(),
                properties=dict(
                    id=instance.in_id,
                ),
            ),
        ).match(
            node(
                "out",
                instance.out_class().label(),
                properties=dict(
                    id=instance.out_id,
                ),
            ),
        ).merge(
            node(
                "in",
            ).rel_in(
                self.variable,
                instance.__class__.label(),
                properties=instance.properties(),
            ).node(
                "out",
            ),
        ).ret(
            expr(self.variable),
        )

    def _delete(self, identifier: str) -> Cypher:
        return match(
            node(
                "in",
                self.model_class.in_class().label(),
            ).rel_in(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(
                    id=str(identifier),
                ),
            ).node(
                "out",
                self.model_class.out_class().label(),
            ),
        ).delete(
            self.variable,
        )

    def _retrieve(self, identifier: str) -> Cypher:
        return match(
            node(
                "in",
                self.model_class.in_class().label(),
            ).rel_in(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(
                    id=str(identifier),
                ),
            ).node(
                "out",
                self.model_class.out_class().label(),
            ),
        ).ret(
            self.variable,
        )

    def _search(self, limit=None, offset=None, **kwargs) -> Cypher:
        return match(
            node(
                "in",
                self.model_class.in_class().label(),
            ).rel_in(
                self.variable,
                self.model_class.label(),
                properties=self.model_class.matching_properties(**kwargs),
            ).node(
                "out",
                self.model_class.out_class().label(),
            ),
        ).ret(
            self.variable,
            limit=limit,
            skip=offset,
        )
