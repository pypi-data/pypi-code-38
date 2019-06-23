# -*- coding: utf-8 -*-

# Internal Imports
from .client import Client


class Bot(Client):
    """Represents a Typetalk bot"""

    def __init__(self, token=None, run_async=False):
        super().__init__(token=token, run_async=run_async, is_bot=True)
        self.is_bot = True
        self.run_async = run_async
