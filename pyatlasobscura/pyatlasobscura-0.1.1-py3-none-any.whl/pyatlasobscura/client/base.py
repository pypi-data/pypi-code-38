import hashlib
from abc import ABC

import requests
from bs4 import BeautifulSoup

from pyatlasobscura.cache import cache


class BaseClient(ABC):
    _endpoint = "https://www.atlasobscura.com/"

    def __init__(self):
        self._cache = {}

    def query(self, path, args=None) -> BeautifulSoup:
        if args is None:
            args = {}

        def query_callback():
            body = requests.get(self._build_url(path), params=args)
            return BeautifulSoup(
                markup=body.content.decode("utf-8", "ignore"), features="html.parser"
            )

        try:
            query_callback = cache(hashlib.md5(f"{path}{args}".encode()).hexdigest())(
                query_callback
            )
        except Exception as e:
            pass
        finally:
            return query_callback()

    def _build_url(self, path: str):
        return f"{self._endpoint}{path}"
