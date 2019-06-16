from enum import auto, Enum
from typing import Generator

from pyatlasobscura.models.destinations import Region
from pyatlasobscura.client import Client


def destinations() -> Generator[Region, None, None]:
    return Client.default().regions()


class SearchType(Enum):
    CATEGORY = auto()
    LOCATION = auto()


def search(search_type: SearchType, value: str, attrs=None):
    attrs = {} if attrs is None else attrs
    client = Client.default()

    return {
        SearchType.CATEGORY: client.search_category,
        SearchType.LOCATION: client.search_location,
    }[search_type](value, **attrs)
