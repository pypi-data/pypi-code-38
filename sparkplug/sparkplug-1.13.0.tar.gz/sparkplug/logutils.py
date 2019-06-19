from logging import getLogger, Handler


class LazyLogger(object):
    def __init__(self, name):
        self.name = name
    
    def __getattr__(self, attr):
        logger = getLogger(self.name)
        return getattr(logger, attr)


class NullHandler(Handler):
    def emit(self, record):
        pass
