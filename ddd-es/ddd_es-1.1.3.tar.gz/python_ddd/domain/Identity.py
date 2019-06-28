"""Identity is a module providing Identity class."""

import uuid


class Identity:
    """Identity is a class representing a unique identifier for objects.

    Identities are unmutable objects

    """

    def __init__(self, ident: str):
        """Make this be a new identity with the given value.

        Params:
            ident: a string representing the unique identity

        Requires:
            len(ident) > 0

        Effects:
            Initializes this
        """
        assert isinstance(ident, str)
        assert len(ident) > 0
        assert ident is not None

        self.__id = ident

    @property
    def value(self) -> str:
        """Return the value of this identity.

        Returns:
            a string containing the value of this identity

        """
        return self.__id

    def __eq__(self, other) -> bool:
        """Compare this object with another.

        Returns:
            True if the two object are of the same type and value
            False otherwise

        """
        if other is None:
            return False

        if not isinstance(other, Identity):
            return False

        return self.value == other.value

    @staticmethod
    def generate_unique_identifier() -> str:
        """Generate a unique identifier that may be used as part of an identity value.

        Returns:
            A string identity value

        """
        return str(uuid.uuid4())
