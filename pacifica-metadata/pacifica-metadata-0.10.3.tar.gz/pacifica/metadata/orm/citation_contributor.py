#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CitationContributor links citations and their authors."""
from peewee import IntegerField, ForeignKeyField, CompositeKey
from .utils import index_hash
from .base import DB
from .citations import Citations
from .contributors import Contributors
from ..rest.orm import CherryPyAPI


class CitationContributor(CherryPyAPI):
    """
    CitationsContributors data model.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | citation          | Link to the Citation model          |
        +-------------------+-------------------------------------+
        | author            | Link to the Contributor model       |
        +-------------------+-------------------------------------+
        | author_precedence | Order of the Author in the Citation |
        +-------------------+-------------------------------------+
    """

    citation = ForeignKeyField(Citations, backref='authors')
    author = ForeignKeyField(Contributors, backref='citations')
    author_precedence = IntegerField(default=1)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains database and primary keys."""

        database = DB
        primary_key = CompositeKey('citation', 'author')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(CitationContributor, self).to_hash(**flags)
        obj['_id'] = index_hash(
            int(self.__data__['citation']), int(self.__data__['author']))
        obj['citation'] = int(self.__data__['citation'])
        obj['author'] = int(self.__data__['author'])
        obj['author_precedence'] = int(self.author_precedence)
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(CitationContributor, self).from_hash(obj)
        self._set_only_if(
            'citation', obj, 'citation',
            lambda: Citations.get(Citations.id == obj['citation'])
        )
        self._set_only_if(
            'author', obj, 'author',
            lambda: Contributors.get(Contributors.id == obj['author'])
        )
        self._set_only_if(
            'author_precedence', obj, 'author_precedence',
            lambda: int(obj['author_precedence'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(CitationContributor, cls).where_clause(kwargs)
        attrs = ['citation', 'author', 'author_precedence']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
