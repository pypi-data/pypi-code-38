"""Services

A collection of interfaces built for extending ontology transformations.
"""

from abc import ABC, abstractmethod
from typing import List

from termlink.models import Relationship


class RelationshipService(ABC):
    """
    An interface for actions related to the `Relationship` model
    """

    @abstractmethod
    def get_relationships(self) -> List[Relationship]:
        """
        Gets a `List` of `Relationship` objects

        Returns:
            A `List` of `Relationship` objects
        """
        pass
