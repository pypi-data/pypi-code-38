"""ValueObject is a module providing ValueObject class."""

import abc
from .Identity import Identity


class ValueObject(metaclass=abc.ABCMeta):
    """ValueObject is an immutable class allowing to represent a value.

    All ValueObjects must implement `equals` method.

    """

    def __init__(self, identity: Identity):
        """Make this be a new ValueObject with the given identity.

        Requires:
            idenity have the following pattern : class_name-id

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

    def __eq__(self, other):
        """Compare self with the given object.

        Returns:
            True if the two objects are equals, False otherwise

        """
        if other is None:
            return False

        if not isinstance(other, ValueObject):
            return False

        if self.identity != other.identity:
            return False

        return self.equals(other)

    @abc.abstractmethod
    def equals(self, other):
        """Compare self with the given object.

        Returns:
            True if the two objects are equals, False otherwise

        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement method equals inherited from ValeObjects."
        )

    @classmethod
    def create_identity(cls):
        """Create an identity that is applicable to this entity type.

        The returned identity is formed by this format:
        class_name-random_uuid

        Returns:
            An identity object that is applicable for this object

        """
        ident = Identity.generate_unique_identifier()
        return Identity("{}-{}".format(cls.__name__, ident))
