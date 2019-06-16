import json

from pyatlasobscura.models.base import Model
from pyatlasobscura.models.util import build_latlon, parse_ao_json


class Location(Model):
    def __init__(self, client, name, coordinates, country=None, region=None):
        super().__init__(client)
        self._lazy_load_all = lambda *a: None
        self["name"] = name
        self["coordinates"] = coordinates
        if country is not None:
            self["country"] = country

        if region is not None:
            self["region"] = region


class Region(Model):
    id_keys = ["name"]
    attributes = ['name']
    children = ['countries']

    def __init__(self, client, dom):
        self.name = dom.find("h2").get_text(strip=True)
        self.countries = [
            Country(client, self, d) for d in dom.findAll("a", {"class": "detail-md"})
        ]
        super().__init__(client)

    def _lazy_load_all(self):
        ...


class Country(Model):
    id_keys = ["name"]
    attributes = ['name', 'region']

    def __init__(self, client, region, a):
        super().__init__(client)
        self.name = a.get_text(strip=True)
        self.region = region.name
        self._href = a["href"]
        self._sort_by_recent = False

    def _lazy_load_all(self):
        ...

    @property
    def places(self):
        return self.place_pages(False, "1")

    def place_pages(self, sort_by_recent=False, page_num="1"):

        self._sort_by_recent = sort_by_recent

        for page_num in self._get_pages(page_num):
            if page_num == "Next":
                break
            for place in self._iterate_places(page_num):
                yield place

    def _iterate_places(self, page):
        for place in self._get_places(page):
            latlng = place.find("div", {"class": "lat-lng"}).get_text(strip=True)

            yield Place(
                client=self._client,
                country=self,
                title=place.find("h3").find("span").get_text(strip=True),
                description=place.find(
                    "div", {"class": "content-card-subtitle"}
                ).get_text(strip=True),
                href=place["href"],
                location={
                    "name": place.find(
                        "div", {"class": "place-card-location"}
                    ).get_text(strip=True),
                    "coordinates": build_latlon(latlng),
                    "country": self.name,
                    "region": self.region,
                },
            )

    def _get_places(self, page):
        return (
            self._get_place_list(page)
                .find("section", {"class": "geo-places"})
                .findAll("a", {"class": "content-card"})
        )

    def _get_pages(self, page):
        pages = self._get_place_list(page).find("nav", {"class": "pagination"})
        if pages is None:
            return "1"
        return [p.get_text(strip=True) for p in pages.findAll("span")]

    def _get_place_list(self, page):
        url = self._href + "/places"
        args = {}
        if int(page) > 1:
            args["page"] = page

        if self._sort_by_recent:
            args["sort"] = "recent"

        return self._client.query(url, args)

    def __repr__(self):
        return object.__repr__(self)


class Place(Model):
    lazy_load_facets = ["datePublished", "dateModified", "categories"]
    id_keys = ["title"]
    attributes = ['title', 'description', 'location', 'href', 'country', 'category']
    children = ['nearby_places']

    def __init__(
            self, client, title, description, location, href, country=None, category=None
    ):
        super().__init__(client)
        self.title = title
        self.description = description
        self.location = location

        self._href = href
        if country is not None:
            self.country = country

        if category is not None:
            self.category = category

        self._load_tags = self._load_place
        self._load_datePublished = self._load_tags
        self._load_dateModified = self._load_tags
        self._load_categories = self._load_tags

    def _lazy_load_all(self):
        self._load_tags()

    def _load_place(self):
        from pyatlasobscura.models.query import Category

        place_body = self._client.query(self._href)
        ld_raw_json = place_body.find(
            "script", {"type": "application/ld+json"}
        ).get_text()
        ld = json.loads(ld_raw_json)
        self.datePublished = ld["datePublished"]
        self.dateModified = ld["dateModified"]
        self.categories = [Category(self._client, t) for t in ld["keywords"]]

        place_metadata = parse_ao_json(place_body, "current_place")
        self.id = place_metadata["id"]
        country = self._client.find_country(place_metadata["country"])
        self.location["country"] = country.name
        self.location["region"] = country.region
        self.nearby_places = [
            Place(
                self._client,
                title=place["title"],
                description=place["subtitle"],
                href=place["url"].replace("https://www.atlasobscura.com", ""),
                country=self._client.find_country(place["country"]),
                location={
                    "name": place["location"],
                    "country": place["country"],
                    "coordinates": list(place["coordinates"].values()),
                    "region": self._client.find_country(place["country"]).region,
                },
            )
            for place in place_metadata["nearby_places"]
        ]
