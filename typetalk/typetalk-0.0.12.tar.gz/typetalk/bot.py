# -*- coding: utf-8 -*-

from .client import Client


class Bot(Client):
    """Represents a Typetalk bot"""

    def __init__(self, token=None):
        super().__init__(token=token)
        self.is_bot = True
