# -*- coding: utf-8 -*-

from .client import Client


class Bot(Client):
    def __init__(self, token):
        super().__init__()
        self.is_bot = True
