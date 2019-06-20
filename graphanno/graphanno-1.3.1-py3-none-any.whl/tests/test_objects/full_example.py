"""Full feature class definition."""
import datetime
import typing


class Owner:
    """Class that will be referenced in Example"""

    name: str

    def __init__(self, name):
        self.name = name


class Tag:
    """Class that will be referenced in Example"""

    name: str

    def __init__(self, name):
        self.name = name


class Example:
    """This class has annotations with all supported fields."""

    name: str
    amount_round: int
    amount: float
    useful: bool
    created: datetime.datetime
    expiration: datetime.date
    refresh_at: datetime.time
    owner: Owner
    tags: typing.List[Tag]
    redundant: str

    @property
    def double_amount(self) -> float:
        """Dynamic property."""
        return self.amount * 2

    @classmethod
    def create_instance(cls) -> "Example":
        """Return object instance with some data."""
        instance = cls()
        instance.name = "Full feature"
        instance.amount = 5.3
        instance.amount_round = 5
        instance.useful = True
        instance.created = datetime.datetime(2019, 2, 6, 15, 0)
        instance.expiration = datetime.date(2050, 12, 31)
        instance.refresh_at = datetime.time(12, 30)
        instance.owner = Owner("me")
        instance.tags = []
        instance.tags.append(Tag("graphene"))
        instance.tags.append(Tag("type annotations"))
        instance.redundant = "Full feature (again)"
        return instance
