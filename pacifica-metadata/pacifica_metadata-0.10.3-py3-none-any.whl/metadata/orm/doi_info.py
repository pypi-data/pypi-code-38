#!/usr/bin/python
# -*- coding: utf-8 -*-
"""DOIInfo stores return info from the minting service about the DOI entry."""
from peewee import ForeignKeyField, CharField, CompositeKey
from .base import DB
from .utils import index_hash
from .doi_entries import DOIEntries
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class DOIInfo(CherryPyAPI):
    """
    DOI Info keys and values for return info from minting service.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | doi               | Link to the DOIEntries model        |
        +-------------------+-------------------------------------+
        | key               | Key name                            |
        +-------------------+-------------------------------------+
        | value             | Value                               |
        +-------------------+-------------------------------------+
    """

    doi = ForeignKeyField(DOIEntries, backref='metadata', column_name='doi')
    key = CharField()
    value = CharField()

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('doi', 'key')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(DOIInfo, self).to_hash(**flags)
        obj['_id'] = index_hash(
            unicode_type(self.__data__['doi']),
            unicode_type(self.__data__['key'])
        )
        obj['doi'] = unicode_type(self.__data__['doi'])
        obj['key'] = unicode_type(self.__data__['key'])
        obj['value'] = unicode_type(self.__data__['value'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(DOIInfo, self).from_hash(obj)
        self._set_only_if(
            'doi', obj, 'doi',
            lambda: DOIEntries.get(DOIEntries.doi == obj['doi'])
        )
        self._set_only_if(
            'value', obj, 'value', lambda: unicode_type(obj['value'])
        )
        self._set_only_if(
            'key', obj, 'key', lambda: unicode_type(obj['key'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(DOIInfo, cls).where_clause(kwargs)
        attrs = ['doi', 'key', 'value']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
