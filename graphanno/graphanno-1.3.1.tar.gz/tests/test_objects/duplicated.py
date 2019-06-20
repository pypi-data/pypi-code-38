"""Definition of the classes used for duplicates verification."""


class Duplicated:
    """This class will have own schema..."""

    name: str
    to_exclude: bool  # this field will be excluded in annotated class


class DuplicateUser:
    """... but this class will reference Duplicated and also will have own schema."""

    name: str
    duplicate: Duplicated


class Duplicated2:
    """Another duplicated class used for another example."""

    name: str
    to_exclude: bool  # this field will be excluded in annotated class


class DuplicateUser2:
    """Another duplicate user equivalent, used in another example wiht Duplicated2"""

    name: str
    duplicate: Duplicated2
