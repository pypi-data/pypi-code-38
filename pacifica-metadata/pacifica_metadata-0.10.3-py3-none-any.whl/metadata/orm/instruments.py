#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instrument model describing data generators."""
from peewee import CharField, BooleanField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class Instruments(CherryPyAPI):
    """
    Instrument and associated fields.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | display_name      | Long display string for web sites   |
        +-------------------+-------------------------------------+
        | name              | Machine parsable display name       |
        +-------------------+-------------------------------------+
        | name_short        | Short version used in lists         |
        +-------------------+-------------------------------------+
        | active            | whether the instrument is active    |
        +-------------------+-------------------------------------+
        | encoding          | encoding for the various name attrs |
        +-------------------+-------------------------------------+
    """

    display_name = CharField(default='', index=True)
    name = CharField(default='', index=True)
    name_short = CharField(default='', index=True)
    active = BooleanField(default=False, index=True)
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Instruments, self).to_hash(**flags)
        obj['_id'] = self.id
        obj['name'] = unicode_type(self.name)
        obj['display_name'] = unicode_type(self.display_name)
        obj['name_short'] = unicode_type(self.name_short)
        obj['active'] = bool(self.active)
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(Instruments, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('name', obj, 'name',
                          lambda: unicode_type(obj['name']))
        self._set_only_if('display_name', obj, 'display_name',
                          lambda: unicode_type(obj['display_name']))
        self._set_only_if('name_short', obj, 'name_short',
                          lambda: unicode_type(obj['name_short']))
        self._set_only_if('active', obj, 'active',
                          lambda: self._bool_translate(obj['active']))
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Instruments, cls).where_clause(kwargs)
        if 'active' in kwargs:
            kwargs['active'] = cls._bool_translate(kwargs['active'])
        return cls._where_attr_clause(
            where_clause,
            kwargs,
            ['name', 'display_name', 'name_short', 'active', 'encoding']
        )
