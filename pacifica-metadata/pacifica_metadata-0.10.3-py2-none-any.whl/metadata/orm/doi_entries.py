#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Keywords linked to citations."""
from peewee import CharField, ForeignKeyField, BooleanField
from ..rest.orm import CherryPyAPI
from .users import Users
from .utils import unicode_type


class DOIEntries(CherryPyAPI):
    """
    DOI Entries Model.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | doi               | full DOI specifier                  |
        +-------------------+-------------------------------------+
        | status            | Current publishing status           |
        +-------------------+-------------------------------------+
        | released          | Has the data been released          |
        +-------------------+-------------------------------------+
        | site_url          | Linked landing page url             |
        +-------------------+-------------------------------------+
        | creator           | Link to Users table                 |
        +-------------------+-------------------------------------+
        | encoding          | encoding of the keyword             |
        +-------------------+-------------------------------------+
    """

    doi = CharField(primary_key=True)
    status = CharField(default='')
    released = BooleanField(default=False)
    site_url = CharField()
    encoding = CharField(default='UTF8')
    creator = ForeignKeyField(Users, backref='dois_created')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(DOIEntries, self).to_hash(**flags)
        obj['_id'] = int(self.id) if self.id is not None else obj['_id']
        obj['doi'] = unicode_type(self.doi)
        obj['status'] = unicode_type(self.status)
        obj['released'] = bool(self.released)
        obj['site_url'] = unicode_type(self.site_url)
        obj['creator'] = int(self.__data__['creator'])
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(DOIEntries, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('doi', obj, 'doi',
                          lambda: unicode_type(obj['doi']))
        self._set_only_if('status', obj, 'status',
                          lambda: unicode_type(obj['status']))
        self._set_only_if('released', obj, 'released',
                          lambda: bool(obj['released']))
        self._set_only_if('site_url', obj, 'site_url',
                          lambda: unicode_type(obj['site_url']))
        self._set_only_if('creator', obj, 'creator',
                          lambda: Users.get(Users.id == obj['creator']))
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(DOIEntries, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs,
            ['doi', 'status', 'released', 'encoding', 'creator']
        )
