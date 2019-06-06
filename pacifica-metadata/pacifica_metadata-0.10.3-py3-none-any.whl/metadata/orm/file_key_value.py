#!/usr/bin/python
# -*- coding: utf-8 -*-
"""FileKeyValue links Files and Keys and Values objects."""
from peewee import ForeignKeyField, CompositeKey
from .base import DB
from .utils import index_hash
from .files import Files
from .values import Values
from .keys import Keys
from ..rest.orm import CherryPyAPI


class FileKeyValue(CherryPyAPI):
    """
    FileKeyValue attributes are foreign keys.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | file              | Link to the File model              |
        +-------------------+-------------------------------------+
        | key               | Link to the Key model               |
        +-------------------+-------------------------------------+
        | value             | Link to the Value model             |
        +-------------------+-------------------------------------+
    """

    file = ForeignKeyField(Files, backref='metadata')
    key = ForeignKeyField(Keys, backref='file_links')
    value = ForeignKeyField(Values, backref='file_links')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('file', 'key', 'value')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(FileKeyValue, self).to_hash(**flags)
        obj['_id'] = index_hash(int(self.__data__['key']),
                                int(self.__data__['file']),
                                int(self.__data__['value']))
        obj['file'] = int(self.__data__['file'])
        obj['key'] = int(self.__data__['key'])
        obj['value'] = int(self.__data__['value'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(FileKeyValue, self).from_hash(obj)
        self._set_only_if('file', obj, 'file',
                          lambda: Files.get(Files.id == obj['file']))
        self._set_only_if('key', obj, 'key',
                          lambda: Keys.get(Keys.id == obj['key']))
        self._set_only_if('value', obj, 'value',
                          lambda: Values.get(Values.id == obj['value']))

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(FileKeyValue, cls).where_clause(kwargs)
        attrs = ['file', 'key', 'value']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
