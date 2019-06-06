from collections import OrderedDict

from .taglist import TagList


class TaskList:

    def __init__(self, tasks):
        self._items = OrderedDict()
        for task in tasks:
            self._items[self._parsenametag(task)] = task

    def add(self, task):
        self._items[TagList.qualnamefromtask(task.tags)] = task.dump()

    def index(self, key):
        """Return the index number of the given key."""
        return list(self._items.keys()).index(key)

    def _parsenametag(self, task):
        return TagList.qualnamefromtask(task.tags)

    def __getitem__(self, qualname):
        return self._items[qualname]

    def __iter__(self):
        return iter(self._items.values())
