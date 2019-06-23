# -*- coding: utf-8 -*-

from .client import Client


class Bot(Client):
    """Represents a Typetalk bot"""

    def __init__(self, token=None, run_async=False):
        super().__init__(token=token, run_async=run_async)
        self.is_bot = True
        self.run_async = run_async
