class Component(object):
    def __init__(self):
        super(Component, self).__init__()
        self.loop = None
        self.app = None
        self.db = None
        self.config = None

    async def prepare(self):
        raise NotImplementedError()

    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()
