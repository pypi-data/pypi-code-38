#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains model for Journal."""
from peewee import CharField, FloatField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class Journals(CherryPyAPI):
    """
    Journal model and associated fields.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | name              | name of the journal                 |
        +-------------------+-------------------------------------+
        | author            | impact factor of the journal        |
        +-------------------+-------------------------------------+
        | website_url       | website for the journal (optional)  |
        +-------------------+-------------------------------------+
        | encoding          | language encoding for the name      |
        +-------------------+-------------------------------------+
    """

    name = CharField(default='')
    impact_factor = FloatField(default=-1.0)
    website_url = CharField(default='')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Journals, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        obj['name'] = unicode_type(self.name)
        obj['impact_factor'] = float(self.impact_factor)
        obj['website_url'] = str(self.website_url)
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(Journals, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('name', obj, 'name',
                          lambda: unicode_type(obj['name']))
        self._set_only_if('impact_factor', obj, 'impact_factor',
                          lambda: float(obj['impact_factor']))
        self._set_only_if('website_url', obj, 'website_url',
                          lambda: str(obj['website_url']))
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Journals, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs, ['name', 'impact_factor', 'website_url', 'encoding']
        )
