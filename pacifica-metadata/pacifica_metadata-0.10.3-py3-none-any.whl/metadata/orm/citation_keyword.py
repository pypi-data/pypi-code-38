#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Keywords linked to citations."""
from peewee import ForeignKeyField, CompositeKey
from .utils import index_hash
from .citations import Citations
from .keywords import Keywords
from .base import DB
from ..rest.orm import CherryPyAPI


class CitationKeyword(CherryPyAPI):
    """
    CitationKeywords Model.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | citation          | Link to the Citation model          |
        +-------------------+-------------------------------------+
        | keyword           | Link to the Keyword model           |
        +-------------------+-------------------------------------+
    """

    citation = ForeignKeyField(Citations, backref='keywords')
    keyword = ForeignKeyField(Keywords, backref='citations')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('citation', 'keyword')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(CitationKeyword, self).to_hash(**flags)
        # pylint: disable=no-member
        obj['_id'] = index_hash(
            int(self.__data__['citation']),
            int(self.__data__['keyword'])
        )
        obj['citation'] = int(self.__data__['citation'])
        obj['keyword'] = int(self.__data__['keyword'])
        # pylint: enable=no-member
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(CitationKeyword, self).from_hash(obj)
        self._set_only_if(
            'citation', obj, 'citation',
            lambda: Citations.get(Citations.id == obj['citation'])
        )
        self._set_only_if(
            'keyword', obj, 'keyword',
            lambda: Keywords.get(Keywords.id == obj['keyword'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(CitationKeyword, cls).where_clause(kwargs)
        attrs = ['citation', 'keyword']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
