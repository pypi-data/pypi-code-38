from pyatlasobscura.models.base import Model
from pyatlasobscura.models.destinations import Place
from pyatlasobscura.models.util import build_latlon, parse_ao_json


class Point(Model):
    id_keys = ["coordinates"]

    def __init__(self, client, location, nearby):
        self.nearby = nearby
        self.location = location
        super().__init__(client)

    def __iter__(self):
        return self.places()

    def places(self, page_num="1"):
        for page in self._paginator(page_num):
            for place in page:
                yield Place(
                    client=self._client,
                    title=place["title"],
                    description=place["subtitle"],
                    location={
                        "name": place["location"],
                        "coordinates": place["coordinates"].keys(),
                    },
                    href=place["url"],
                )

    def _paginator(self, page_num="1"):
        page_counter = int(page_num)
        for page in self._paginate(str(page_counter)):
            yield page
            page_counter += 1

    def _paginate(self, page_num):
        args = {"page": page_num}
        page = self._client.query("/search", args)
        search_results = parse_ao_json(page, "place_search")
        yield search_results["results"]


class Category(Model):
    id_keys = ["name"]

    def __init__(self, client, name):
        super().__init__(client)
        self.name = name
        self._dom = {}

    def __iter__(self):
        return self.places()

    def _lazy_load_all(self):
        ...

    def places(self, page_num="1"):

        for page_num in self._get_pages(page_num):
            if page_num == "Next":
                break
            for place in self._iterate_places(page_num):
                yield place

    def _iterate_places(self, page):
        for place in self._get_places(page):
            latlng = place.find("div", {"class": "lat-lng"})
            if latlng is None:
                continue
            else:
                latlng = latlng.get_text(strip=True)

            yield Place(
                self._client,
                category=self,
                title=place.find("h3").find("span").get_text(strip=True),
                description=place.find("div", {"class": "subtitle-sm"}).get_text(
                    strip=True
                ),
                href=place.find("a", {"class": "content-card"})["href"],
                location={
                    "name": place.find(
                        "div", {"class": "place-card-location"}
                    ).get_text(strip=True),
                    "coordinates": build_latlon(latlng),
                },
            )

    def _get_pages(self, page):
        pages = self._get_place_list(page).find("nav", {"class": "pagination"})
        if pages is None:
            return "1"
        spans = pages.findAll("span")
        pages = [p.get_text(strip=True) for p in spans]

        return [page for page in pages if len(page)]

    def _get_places(self, page):
        grid = self._get_place_list(page).find(
            "div", {"data-component-type": "categories-places"}
        )
        places = grid.findAll("div", {"class": "index-card-wrap"})
        return places

    def _get_place_list(self, page):
        if page not in self._dom:
            url = "/categories/" + self.name
            args = {}
            if int(page) > 1:
                args["page"] = page

            self._dom[page] = self._client.query(url, args)
        return self._dom[page]
