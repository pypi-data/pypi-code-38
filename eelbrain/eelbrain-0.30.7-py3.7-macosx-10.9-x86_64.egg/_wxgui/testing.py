from contextlib import ContextDecorator

from .._config import CONFIG


class ConfigContext(ContextDecorator):

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.old = None

    def __enter__(self):
        self.old = CONFIG[self.key]
        CONFIG[self.key] = self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        CONFIG[self.key] = self.old


hide_plots = ConfigContext('show', False)
