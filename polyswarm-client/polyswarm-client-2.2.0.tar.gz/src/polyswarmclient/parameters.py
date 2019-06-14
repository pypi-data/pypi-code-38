import aiorwlock


class Parameters(object):
    """Trivial wrapper around a dict but protected via a RWLock to allow updates"""

    def __init__(self, p):
        self.rwlock = aiorwlock.RWLock()
        self.inner = p

    async def update(self, new):
        async with self.rwlock.writer:
            self.inner.update(new)

    async def get(self, name):
        async with self.rwlock.reader:
            return self.inner.get(name)
