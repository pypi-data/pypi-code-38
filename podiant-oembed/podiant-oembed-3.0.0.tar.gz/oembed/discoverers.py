from urllib.parse import urlparse
import logging


class AlreadyRegisteredError(Exception):
    pass


class DiscovererList(object):
    def __init__(self):
        self._list = []
        self._logger = logging.getLogger('podiant.oembed')

    def register(self):
        def wrapper(func):
            if func in self._list:  # pragma: no cover
                raise AlreadyRegisteredError(
                    '%s is already registered.' % func.__name__
                )

            self._list.append(func)
            return func

        return wrapper

    def discover(self, url, **kwargs):
        urlparts = urlparse(url)
        for func in self._list:
            discovered = func(
                urlparts.netloc,
                urlparts.path,
                urlparts.query,
                **kwargs
            )

            if discovered:
                return discovered
