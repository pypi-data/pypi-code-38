# -*- coding: utf-8 -*-

from .http import HTTPClient


class Client:
    def __init__(self):
        self.http = HTTPClient()
