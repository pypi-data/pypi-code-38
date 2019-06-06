#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Keywords linked to citations."""
from peewee import ForeignKeyField, CompositeKey
from .base import DB
from .citations import Citations
from .transaction_user import TransactionUser
from ..rest.orm import CherryPyAPI
from .utils import index_hash


class CitationTransaction(CherryPyAPI):
    """
    CitationTransaction Model.

    Attributes:
        +-------------------+--------------------------------------------+
        | Name              | Description                                |
        +===================+============================================+
        | transaction       | Link to the TransactionUser model          |
        +-------------------+--------------------------------------------+
        | citation          | Link to the Citations model                |
        +-------------------+--------------------------------------------+
    """

    citation = ForeignKeyField(Citations, backref='release_entries')
    transaction = ForeignKeyField(TransactionUser, backref='citations')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('citation', 'transaction')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(CitationTransaction, self).to_hash(**flags)
        obj['_id'] = index_hash(
            str(self.__data__['transaction']),
            int(self.__data__['citation'])
        )
        obj['transaction'] = str(self.__data__['transaction'])
        obj['citation'] = int(self.__data__['citation'])
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(CitationTransaction, self).from_hash(obj)
        self._set_only_if(
            'citation', obj, 'citation',
            lambda: Citations.get(Citations.id == obj['citation'])
        )
        self._set_only_if(
            'transaction', obj, 'transaction',
            lambda: TransactionUser.get(TransactionUser.uuid == obj['transaction'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(CitationTransaction, cls).where_clause(kwargs)
        return cls._where_attr_clause(where_clause, kwargs, ['citation', 'transaction'])
