#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Authors linked to DOI's."""
from peewee import ForeignKeyField, CompositeKey, IntegerField
from .base import DB
from ..rest.orm import CherryPyAPI
from .doi_entries import DOIEntries
from .doi_authors import DOIAuthors
from .utils import index_hash, unicode_type


class DOIAuthorMapping(CherryPyAPI):
    """
    DOI Author Mapping Model.

    Attributes:
        +-------------------+-----------------------------------------+
        | Name              | Description                             |
        +===================+=========================================+
        | author            | ID from DOI_authors table               |
        +-------------------+-----------------------------------------+
        | doi               | Full DOI Specifier                      |
        +-------------------+-----------------------------------------+
        | author_order      | where does this author go in the order? |
        +-------------------+-----------------------------------------+
    """

    author = ForeignKeyField(DOIAuthors, backref='doi_authorships')
    doi = ForeignKeyField(DOIEntries, backref='authors', field='doi')
    author_order = IntegerField(default=1)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('author', 'doi', 'author_order')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(DOIAuthorMapping, self).to_hash(**flags)
        obj['_id'] = index_hash(
            int(self.__data__['author']),
            unicode_type(self.__data__['doi']),
            int(self.__data__['author_order'])
        )
        obj['author'] = int(self.__data__['author'])
        obj['doi'] = unicode_type(self.__data__['doi'])
        obj['author_order'] = int(self.author_order)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(DOIAuthorMapping, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('author', obj, 'author',
                          lambda: DOIAuthors.get(DOIAuthors.id == obj['author']))
        self._set_only_if('doi', obj, 'doi',
                          lambda: DOIEntries.get(DOIEntries.doi == obj['doi']))
        self._set_only_if('author_order', obj, 'author_order',
                          lambda: int(obj['author_order']))

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(DOIAuthorMapping, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs, ['doi', 'author_order', 'author']
        )
