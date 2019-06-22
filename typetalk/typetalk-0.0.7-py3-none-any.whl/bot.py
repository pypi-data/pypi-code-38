# -*- coding: utf-8 -*-

from .client import Client


class Bot(Client):
    def __init__(self):
        self.is_bot = True
