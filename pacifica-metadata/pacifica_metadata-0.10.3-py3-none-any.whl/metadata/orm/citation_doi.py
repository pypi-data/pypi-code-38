#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Keywords linked to citations."""
from peewee import ForeignKeyField, CompositeKey
from .base import DB
from .citations import Citations
from .doi_entries import DOIEntries
from ..rest.orm import CherryPyAPI
from .utils import index_hash, unicode_type


class CitationDOI(CherryPyAPI):
    """
    CitationDOI Model.

    Attributes:
        +-------------------+--------------------------------------------+
        | Name              | Description                                |
        +===================+============================================+
        | doi               | Link to the DOI model                      |
        +-------------------+--------------------------------------------+
        | citation          | Link to the Citations model                |
        +-------------------+--------------------------------------------+
    """

    doi = ForeignKeyField(DOIEntries, backref='doi_citations', field='doi')
    citation = ForeignKeyField(Citations, backref='doi_entries')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('citation', 'doi')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(CitationDOI, self).to_hash(**flags)
        obj['_id'] = index_hash(
            int(self.__data__['citation']),
            unicode_type(self.__data__['doi'])
        )
        obj['doi'] = unicode_type(self.__data__['doi'])
        obj['citation'] = int(self.__data__['citation'])
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(CitationDOI, self).from_hash(obj)
        self._set_only_if(
            'citation', obj, 'citation',
            lambda: Citations.get(Citations.id == obj['citation'])
        )
        self._set_only_if(
            'doi', obj, 'doi',
            lambda: DOIEntries.get(DOIEntries.doi == obj['doi'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(CitationDOI, cls).where_clause(kwargs)
        return cls._where_attr_clause(where_clause, kwargs, ['citation', 'doi'])
