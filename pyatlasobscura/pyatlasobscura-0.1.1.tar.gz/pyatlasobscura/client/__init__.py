from typing import Generator

from pyatlasobscura.client.base import BaseClient
from pyatlasobscura.models.query import Category, Point


class Client(BaseClient):
    _DEFAULT = None

    @classmethod
    def default(cls):
        if cls._DEFAULT is None:
            cls._DEFAULT = cls()
        return cls._DEFAULT

    def search_category(self, category):

        if "categories" not in self._cache:
            self._cache["categories"] = {}
        if category in self._cache["categories"]:
            return self._cache["categories"]

        cache = []
        for location in Category(self, category):
            cache.append(location)
            yield location

        # Don't store until we have the full set
        self._cache["categories"][category] = cache

    def search_location(self, location, nearby):
        return Point(self, location, nearby)

    def regions(self) -> Generator["pyatlasobscura.Region", None, None]:
        from pyatlasobscura import Region

        if "regions" not in self._cache:
            body = self.query("destinations")
            regions = body.findAll("li", {"class": "global-region-item"})
            self._cache["regions"] = regions
        else:
            regions = self._cache["regions"]
        for region in regions:
            yield Region(self, region)

    def find_country(self, country_name: str):
        for region in self.regions():
            for country in region.countries:
                if country.name == country_name:
                    return country
