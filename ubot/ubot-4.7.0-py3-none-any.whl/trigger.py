from abc import ABC, abstractmethod


class Trigger(ABC):
    callback = None

    @abstractmethod
    def match(self, update, update_type, update_flavor):
        """Returns True if update matches, any other value if it doesn't. Async supported."""
        pass

    @abstractmethod
    def handle(self, update, update_type, update_flavor):
        """Returns a tuple (url, endpoint, args, data, headers) or None. Async supported."""
        pass
