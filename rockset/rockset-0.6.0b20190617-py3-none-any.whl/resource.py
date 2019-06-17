""" Base class for Collection objects
"""

import time
import datetime

from rockset.cursor import Cursor
from rockset.exception import InputError
from rockset.query import Query

from rockset.swagger_client.api import CollectionsApi


class Resource(object):
    # instance methods
    def __init__(self, client, name, workspace='commons', **kwargs):
        """Represents a single Rockset collection"""
        self.client = client
        self.workspace = workspace
        self.name = name
        self.dropped = False
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return

    def __str__(self):
        """Converts the collection into a user friendly printable string"""
        return str(vars(self))

    def asdict(self):
        d = vars(self)
        d.pop('client')
        if not self.dropped:
            d.pop('dropped')
        return d

    def describe(self):
        kwargs = {}
        return CollectionsApi(self.client).get(
            workspace=self.workspace, collection=self.name
        )

    def setstate(self, newstate):
        kwargs = {}
        return CollectionsApi(self.client).get(
            workspace=self.workspace, collection=self.name, state=newstate
        )

    def drop(self):
        self.dropped = True
        CollectionsApi(self.client).delete(
            workspace=self.workspace, collection=self.name
        )
        return

    def query(self, q, **kwargs):
        return self.client.query(q=q, collection=self.name, **kwargs)


__all__ = [
    'Resource',
]
