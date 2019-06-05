import logging


class Inventory(object):
    def __init__(self, client, logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self.client = client

    def Get(self):
        raise NotImplementedError

    def Create(self):
        raise NotImplementedError
        pass

    def Update(self):
        raise NotImplementedError
        pass
