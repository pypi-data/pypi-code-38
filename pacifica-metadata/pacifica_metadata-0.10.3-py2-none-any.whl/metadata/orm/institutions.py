#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Describes an institution and its attributes."""
from peewee import BooleanField, TextField, CharField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class Institutions(CherryPyAPI):
    """
    Institution model scribes an institute.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | name              | Name of the institution             |
        +-------------------+-------------------------------------+
        | association_cd    | Type of institution (TBD)           |
        +-------------------+-------------------------------------+
        | is_foreign        | Is the institution foreign or not   |
        +-------------------+-------------------------------------+
        | encoding          | Any encoding for the name           |
        +-------------------+-------------------------------------+
    """

    name = TextField(default='')
    association_cd = CharField(default='UNK')
    is_foreign = BooleanField(default=False)
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Institutions, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        obj['name'] = unicode_type(self.name)
        obj['association_cd'] = str(self.association_cd)
        obj['is_foreign'] = bool(self.is_foreign)
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(Institutions, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('name', obj, 'name',
                          lambda: unicode_type(obj['name']))
        self._set_only_if('association_cd', obj, 'association_cd',
                          lambda: str(obj['association_cd']))
        self._set_only_if('is_foreign', obj, 'is_foreign',
                          lambda: self._bool_translate((obj['is_foreign'])))
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Institutions, cls).where_clause(kwargs)
        if 'is_foreign' in kwargs:
            kwargs['is_foreign'] = cls._bool_translate(kwargs['is_foreign'])
        return cls._where_attr_clause(
            where_clause,
            kwargs,
            ['name', 'is_foreign', 'association_cd', 'encoding']
        )
