#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains the model for metadata keys."""
import uuid
from peewee import CharField, TextField, UUIDField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class DataSources(CherryPyAPI):
    """
    DataSources model class for metadata.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | uuid              | data source unique id               |
        +-------------------+-------------------------------------+
        | name              | data source name                    |
        +-------------------+-------------------------------------+
        | uri               | data source location URI            |
        +-------------------+-------------------------------------+
        | display_name      | data source display name            |
        +-------------------+-------------------------------------+
        | description       | data source long description        |
        +-------------------+-------------------------------------+
        | encoding          | encoding for the fields             |
        +-------------------+-------------------------------------+
    """

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    name = CharField(default='', index=True)
    uri = CharField(default='', index=True)
    display_name = CharField(default='', index=True)
    description = TextField(default='')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(DataSources, self).to_hash(**flags)
        obj['uuid'] = str(self.uuid)
        for attr in ['name', 'uri', 'display_name', 'description']:
            obj[attr] = unicode_type(getattr(self, attr))
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(DataSources, self).from_hash(obj)
        self._set_only_if(
            'uuid', obj, 'uuid', lambda: uuid.UUID(obj['uuid'])
        )
        for attr in ['name', 'uri', 'display_name', 'description']:
            self._set_only_if(
                attr, obj, attr, lambda o=obj, a=attr: unicode_type(o[a])
            )
        self._set_only_if(
            'encoding', obj, 'encoding', lambda: str(obj['encoding'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(DataSources, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs,
            ['uuid', 'name', 'uri', 'description', 'display_name', 'encoding']
        )
