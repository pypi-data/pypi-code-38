"""A module provides access to the public polka.academy API.bo"""
import json
import re
from html import unescape
from typing import NamedTuple, Optional
from urllib.parse import urlencode
from urllib.request import urlopen


__all__ = [
    "rawbooks",
    "rawbook",
    "rawsearch",
    "rawlists",
    "rawlist",
    "rawpundits",
    "rawpunditposts",
    "rawpunditfavs",
    "books",
    "pundits",
    "lists",
    "search",
    "Book",
    "Pundit",
    "Compilation",
]

_BASE = "https://api.polka.academy/"
_BOOKS = f"{_BASE}books?"
_POST = f"{_BASE}posts/{{post_id}}"
_SEARCH = f"{_BASE}search?"
_LISTS = f"{_BASE}compilations"
_LIST_POST = f"{_BASE}compilations/{{post_id}}"
_PEOPLE = f"{_BASE}people?"
_PEOPLE_POST = f"{_BASE}people/{{post_id}}/posts"
_PEOPLE_FAVS = f"{_BASE}people/{{post_id}}/favs"


_NOTES = re.compile(r"\{([^\|]*)\s*\|\s*([^\}]*)\}")
_SOURCES = re.compile(r"\[([^\|]*)\s*\|\s*(\d+)\s*\|([^\]]*)\]")
_HTMLTAG = re.compile(r"<\s*[^>]*>")


def __dir__():
    return sorted(__all__)


def _get(url, **params):
    response = urlopen(url + urlencode(params))
    response = response.read().decode("utf-8")
    return json.loads(response)


def _clean_text(text):
    text = re.sub(_HTMLTAG, "", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    text = text.strip()
    return text


def _importance():
    return {b["id"]: b["importance"] for b in rawbooks()["books"]}


def rawbooks(sort_column="rating", sort_direction="desc"):
    params = {"sort_column": sort_column, "sort_direction": sort_direction}
    return _get(_BOOKS, **params)


def rawbook(book_id):
    return _get(_POST.format(post_id=book_id))


def rawsearch(query):
    return _get(_SEARCH, **{"q": query})


def rawlists():
    return _get(_LISTS)


def rawlist(list_id):
    return _get(_LIST_POST.format(post_id=list_id))


def rawpundits(type_="all"):
    return _get(_PEOPLE, **{"type": type_})


def rawpunditposts(pundit_id):
    return _get(_PEOPLE_POST.format(post_id=pundit_id))


def rawpunditfavs(pundit_id):
    return _get(_PEOPLE_FAVS.format(post_id=pundit_id))


def books(sort_column="rating", sort_direction="desc"):
    """Returns a list of `Book` instances that has an article.
    Valid values for `sort_column` are "rating" (default), "year",
    "title" and "authors". Valid values for `sort_direction` are
    "desc" (default) and "asc"."""
    books = []
    for data in rawbooks(sort_column, sort_direction)["books"]:
        books.append(Book(data["id"], rawdata=data))
    return books


def pundits(type_="all"):
    """Returns a list of `Pundit` instances. Valid values for
    `type_` are "all" (default), "authors" and "experts"."""
    pundits = []
    for data in rawpundits(type_)["people"]:
        pundits.append(Pundit(data["id"], rawdata=data))
    return pundits


def lists():
    """Returns a list of `Compilation` instances."""
    lists = []
    for data in rawlists()["compilations"]:
        lists.append(Compilation(data["id"], rawdata=data))
    return lists


def search(query):
    """Looks for a `query` and returns a list of 3-tuples like
    `(title, description, object)`."""
    results = []
    for item in rawsearch(query):
        category = item["category"]
        description = _clean_text(item["desc"])
        if category == "articles":
            Object = Book
        elif category == "lists":
            Object = Compilation
        elif category == "experts":
            Object = Pundit
        results.append((item["title"], description, Object(item["id"])))
    return results


class Book:
    """Represents a book."""

    _importance = {}

    def __init__(self, id: Optional[int], *, rawdata=None):
        self.id = id
        self.rawdata = rawdata if rawdata is not None else {}
        self._n_requests = 0

    def _getdata(self, key):
        if key not in self.rawdata:
            if key == "author" and "authors" in self.rawdata:
                key = "authors"
            elif key == "date_start":
                if "start_year" in self.rawdata:
                    key = "start_year"
                elif "year" in self.rawdata:
                    key = "year"
                else:
                    data = rawbook(self.id)
                    self.rawdata.update(data)
                    self._n_requests += 1
            elif key == "date_end":
                if "end_year" in self.rawdata:
                    key = "start_year"
                else:
                    data = rawbook(self.id)
                    self.rawdata.update(data)
                    self._n_requests += 1
            elif key == "lead" and "description" in self.rawdata:
                key = "description"
            elif key == "lead" and not self.has_article and self.in_lists:
                books = rawlist(self.in_lists[0].id)["books"]
                data = [d for d in books if d["id"] == self.id][0]
                self.rawdata.update(data)
                self._n_requests += 1
                key = "description"
            elif key == "importance" and self.has_article:
                Book._importance = _importance()
                self._n_requests += 1
                self.rawdata.update({"importance": Book._importance[self.id]})
            elif key == "compilations" and self.has_article:
                books = rawbooks()["books"]
                data = [b for b in books if b["id"] == self.id][0]
                self.rawdata.update(data)
            elif self.has_article:
                data = rawbook(self.id)
                self.rawdata.update(data)
                self._n_requests += 1
        return self.rawdata.get(key)

    @property
    def importance(self):
        importance = self._getdata("importance")
        return float(importance) if importance is not None else None

    @property
    def title(self):
        return _clean_text(self._getdata("title"))

    @property
    def authors(self):
        return self._getdata("author")

    @property
    def description(self):
        lead = self._getdata("lead")
        return _clean_text(lead) if lead is not None else lead

    @property
    def pundit(self):
        if not self.has_article:
            return None
        data = self._getdata("pundit")
        return Pundit(data["id"], rawdata=data)

    @property
    def year(self):
        start = self._getdata("date_start")
        end = self._getdata("date_end")
        return Year(start, end)

    @property
    def has_article(self):
        return self.id is not None

    @property
    def questions(self):
        """Returns a list of `Question` instances (just named
        tuples). Each item has `question`, `answer`  and
        `answer_with_notes` attributes.
        """
        if not self.has_article:
            return None
        questions = []
        for block in self._getdata("blocks") or []:
            if block["type"] != "question_template":
                continue
            question = _clean_text(block["question"].strip())
            answer_with_notes = _clean_text(block["html"].strip())
            answer = re.sub(_NOTES, r"\1", answer_with_notes)
            answer = re.sub(_SOURCES, r"\1", answer)
            questions.append(Question(question, answer, answer_with_notes))
        return questions

    @property
    def sources(self):
        if not self.has_article:
            return None
        sources = self._getdata("list")
        return [source["title"] for source in sources]

    @property
    def in_lists(self):
        lists = []
        for data in self._getdata("compilations"):
            lists.append(Compilation(data["id"], rawdata=data))
        return lists

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(title={self.title!r}, authors={self.authors!r})"
        )

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (self.id, self.title) == (other.id, other.title)
        return NotImplemented

    def __lt__(self, other):
        if other.__class__ is self.__class__:
            return self.importance < other.importance
        return NotImplemented

    def __hash__(self):
        return hash((self.id, self.title))


class Pundit:
    "Represents an expert."

    def __init__(self, id: int, *, rawdata=None):
        self.id = id
        self.rawdata = rawdata if rawdata is not None else {}
        self._n_requests = 0

    def _getdata(self, key):
        if key not in self.rawdata:
            if key == "posts":
                posts = rawpunditposts(self.id)["books"]
                self.rawdata.update({"posts": posts})
            elif key == "favs":
                favs = rawpunditfavs(self.id)["books"]
                self.rawdata.update({"favs": favs})
            else:
                people = rawpundits()["people"]
                data = [p for p in people if p["id"] == self.id][0]
                self.rawdata.update(data)
            self._n_requests += 1
        return self.rawdata.get(key)

    @property
    def name(self):
        first = self._getdata("first").strip()
        last = self._getdata("last").strip()
        return f"{first} {last}"

    @property
    def credit(self):
        return _clean_text(self._getdata("credit"))

    @property
    def description(self):
        return _clean_text(self._getdata("description"))

    @property
    def wrote_about(self):
        posts = self._getdata("posts")
        return [Book(d["id"], rawdata=d) for d in posts] if posts else []

    @property
    def favorites(self):
        favs = self._getdata("favs")
        return [Book(d["id"], rawdata=d) for d in favs] if favs else []

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (self.id, self.name) == (other.id, other.name)
        return NotImplemented

    def __hash__(self):
        return hash((self.id, self.name))


class Compilation:
    """Represents a compilation"""

    def __init__(self, id: int, *, rawdata=None):
        self.id = id
        self.rawdata = rawdata if rawdata is not None else {}
        self._n_requests = 0

    def _getdata(self, key):
        if key not in self.rawdata:
            if key in ["short_desc", "max_year", "min_year"]:
                compilations = rawlists()["compilations"]
                data = [c for c in compilations if c["id"] == self.id][0]
                self.rawdata.update(data)
            else:
                self.rawdata.update(rawlist(self.id))
            self._n_requests += 1
        return self.rawdata.get(key)

    @property
    def title(self):
        return self._getdata("title")

    @property
    def description(self):
        return _clean_text(self._getdata("description"))

    @property
    def short_description(self):
        return _clean_text(self._getdata("short_desc"))

    @property
    def max_year(self):
        return int(self._getdata("max_year"))

    @property
    def min_year(self):
        return int(self._getdata("min_year"))

    @property
    def books(self):
        books = []
        for data in self._getdata("books"):
            books.append(Book(data["id"], rawdata=data))
        return books

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title!r})"

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (self.id, self.title) == (other.id, other.title)
        return NotImplemented

    def __hash__(self):
        return hash((self.id, self.title))


class Year(NamedTuple):
    start: Optional[int]
    end: Optional[int]


class Question(NamedTuple):
    question: str
    answer: str
    answer_with_notes: str
