from collections import OrderedDict
from datetime import datetime
from typing import Optional


class CachedItem:
    """Container for cached items."""

    __slots__ = ('value', 'time')

    def __init__(self, value):
        self.value = value
        self.time = datetime.utcnow()


class Cache:
    """In-memory cache implementation."""

    __slots__ = ('_bag', 'max_size', 'expiration_policy')

    def __init__(self, max_size=500, expiration_policy=None):
        self._bag = OrderedDict()
        self.max_size = max_size
        self.expiration_policy = expiration_policy

    def __len__(self):
        """Returns the count of items contained in this cache, without checking for expiration."""
        return len(self._bag)

    def __contains__(self, key):
        """
        Returns a value indicating whether this cache
        contains an item with the given key, checking for expiration.
        """
        return self.get(key) is not None

    def __iter__(self):
        """Returns all items contained in this cache, without checking for expiration."""
        yield from self._bag.items()

    def _is_full(self):
        return 0 < self.max_size < len(self._bag)

    def set(self, key, value):
        self._set(key, CachedItem(value))

    def _set(self, key, item: CachedItem):
        self._bag[key] = item

        if self._is_full():
            self._check_expired()

            if self._is_full():
                self._bag.popitem(last=False)

    def _check_expired(self):
        if not self.expiration_policy:
            return

        to_remove = []

        for key, item in self._bag.items():
            if self.expired(item):
                to_remove.append(key)

        for key in to_remove:
            self.remove(key)

    def expired(self, item):
        if not self.expiration_policy:
            return False

        return self.expiration_policy(item)

    def remove(self, key):
        del self._bag[key]

    def get(self, key) -> Optional[CachedItem]:
        cached_item = self._bag.get(key, None)

        if cached_item:
            if self.expired(cached_item):
                self.remove(key)
            else:
                return cached_item

        return None
