import gzip
import os
from pathlib import Path

from bs4 import BeautifulSoup


class DataCache(object):
    def __init__(self):
        self._path = Path(os.path.join(os.path.expanduser("~"), ".cache"))
        if not self._path.exists():
            self._path.mkdir(exist_ok=True)
        self._path = self._path / "pyatlasobscura"
        if not self._path.exists():
            self._path.mkdir(exist_ok=True)

    def __call__(self, identifier):
        cache_file = self._path / (identifier + ".gz")

        def func_wrapper(func):
            def cache_handler(*args, **kwargs):
                return self._serialise(
                    cache_file=cache_file, callback=lambda *a: func(*args, **kwargs)
                )

            return cache_handler

        return func_wrapper

    def _serialise(self, cache_file, callback):
        if cache_file.exists():
            with gzip.open(cache_file, "rb") as f:
                dom = BeautifulSoup(
                    markup=f.read().decode("utf-8", "ignore"), features="html.parser"
                )
        else:
            dom = callback()
            with gzip.open(cache_file, "w") as f:
                f.write(dom.prettify().encode())
        return dom


class PluginCache(DataCache):
    def __call__(self):
        def func_wrapper(func):
            def cache_handler(*args, **kwargs):
                response = func(*args, **kwargs)
                return response(self._path)

            return cache_handler

        return func_wrapper


cache = DataCache()
plugin_cache = PluginCache()
