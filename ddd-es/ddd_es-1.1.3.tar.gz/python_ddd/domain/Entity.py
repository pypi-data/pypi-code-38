"""Entity is a module providing the entity class."""

import abc
from typing import Any
from .Identity import Identity


class Entity(metaclass=abc.ABCMeta):
    """Entity is a class representing a mutable object connected to an Aggregate.

    Entities are mutable object that must redefine `equals` method.
    Each entity must be initialized with an identity that is used to compare them.

    """

    def __init__(self, identity: Identity):
        """Make this be a new entity with the given identity.

        Effects:
            Initializes this

        """
        assert identity is not None
        assert isinstance(identity, Identity)
        assert identity.value.startswith(
            self.__class__.__name__
        ), "This identity is not appropriate for this class"

        self.__identity = identity

    @property
    def identity(self) -> Identity:
        """Return the identity of this entity.

        Returns:
            This entity identity

        """
        return self.__identity

    def __eq__(self, other: Any) -> bool:
        """Compare self with the given object.

        Returns:
            True if the two objects are equals, False otherwise

        """
        if other is None:
            return False

        if not isinstance(other, Entity):
            return False

        if not self.identity == other.identity:
            return False

        return self.equals(other)

    @abc.abstractmethod
    def equals(self, other: Any) -> bool:
        """Compare self with the given object.

        Returns:
            True if the two objects are equals, False otherwise

        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement method equals inherited from Entity."
        )

    @classmethod
    def create_identity(cls) -> Identity:
        """Create an identity that is applicable to this entity type.

        The returned identity is formed by this format:
        class_name-random_uuid

        Returns:
            An identity object that is applicable for this object

        """
        ident = Identity.generate_unique_identifier()
        return Identity("{}-{}".format(cls.__name__, ident))
