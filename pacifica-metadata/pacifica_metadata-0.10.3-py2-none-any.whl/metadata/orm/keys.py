#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains the model for metadata keys."""
from peewee import CharField, TextField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class Keys(CherryPyAPI):
    """
    Keys model class for metadata.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | key               | generic metadata key                |
        +-------------------+-------------------------------------+
        | display_name      | key display name                    |
        +-------------------+-------------------------------------+
        | description       | key long description                |
        +-------------------+-------------------------------------+
        | encoding          | encoding for the key                |
        +-------------------+-------------------------------------+
    """

    key = CharField(default='', index=True)
    display_name = CharField(default='', index=True)
    description = TextField(default='')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Keys, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        for attr in ['key', 'display_name', 'description']:
            obj[attr] = unicode_type(getattr(self, attr))
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(Keys, self).from_hash(obj)
        self._set_only_if(
            '_id', obj, 'id', lambda: obj['_id']
        )
        for attr in ['key', 'display_name', 'description']:
            self._set_only_if(
                attr, obj, attr, lambda o=obj, a=attr: unicode_type(o[a])
            )
        self._set_only_if(
            'encoding', obj, 'encoding', lambda: str(obj['encoding'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Keys, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs,
            ['key', 'display_name', 'description', 'encoding']
        )
