#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains the model for metadata analytical tools."""
from peewee import CharField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class AnalyticalTools(CherryPyAPI):
    """
    Keys model class for metadata.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | name              | generic tool name                   |
        +-------------------+-------------------------------------+
        | encoding          | encoding for the name               |
        +-------------------+-------------------------------------+
    """

    name = CharField(default='')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(AnalyticalTools, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        obj['name'] = unicode_type(self.name)
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(AnalyticalTools, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('name', obj, 'name',
                          lambda: unicode_type(obj['name']))
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(AnalyticalTools, cls).where_clause(kwargs)
        return cls._where_attr_clause(where_clause, kwargs, ['name', 'encoding'])
