import sys


class RuntimeContext(object):

    """
    Handle runtime context as a singleton.
    """

    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._config = dict()
        self._bus = None

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def bus(self):
        return self._bus

    @bus.setter
    def bus(self, value):
        self._bus = value


sys.modules[__name__] = RuntimeContext.instance()
