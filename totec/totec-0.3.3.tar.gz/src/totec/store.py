from abc import ABC


class AbstractStore(ABC):
    """
    Interface for storing jobs that is used by :class:`JobClient` to keep track
    which jobs are outstanding.
    """

    def put(self, job):
        pass

    def get(self, tag):
        pass

    def list(self):
        pass


class InMemoryStore(AbstractStore):
    """Implementation that stores the jobs in memory.
    """

    def __init__(self):
        self._store = {}

    def put(self, job):
        self._store[job.tag] = job

    def get(self, tag):
        return self._store.get(tag)

    def list(self):
        for job in self._store.values():
            yield job
