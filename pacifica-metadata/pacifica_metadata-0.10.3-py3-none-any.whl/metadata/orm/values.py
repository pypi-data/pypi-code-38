#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains the model for metadata values."""
from peewee import CharField, TextField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class Values(CherryPyAPI):
    """
    Values model class for metadata.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | value             | generic value for some metadata     |
        +-------------------+-------------------------------------+
        | display_name      | value display name                  |
        +-------------------+-------------------------------------+
        | description       | value long description              |
        +-------------------+-------------------------------------+
        | encoding          | language encoding of the value      |
        +-------------------+-------------------------------------+
    """

    value = CharField(default='', index=True)
    display_name = CharField(default='', index=True)
    description = TextField(default='')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Values, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        for attr in ['value', 'display_name', 'description']:
            obj[attr] = unicode_type(getattr(self, attr))
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(Values, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: obj['_id'])
        for attr in ['value', 'display_name', 'description']:
            self._set_only_if(
                attr, obj, attr, lambda o=obj, a=attr: unicode_type(o[a])
            )
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Values, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs,
            ['value', 'display_name', 'description', 'encoding']
        )
