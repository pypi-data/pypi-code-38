#!/usr/bin/python
# -*- coding: utf-8 -*-
"""DOI transaction relationship."""
from peewee import ForeignKeyField
from .utils import index_hash, unicode_type
from .transaction_user import TransactionUser
from .doi_entries import DOIEntries
from ..rest.orm import CherryPyAPI


class DOITransaction(CherryPyAPI):
    """
    Relates DOI entries with transaction release entries.

    Attributes:
        +-------------------+--------------------------------------------+
        | Name              | Description                                |
        +===================+============================================+
        | doi               | Link to the DOI model                      |
        +-------------------+--------------------------------------------+
        | transaction       | Link to the TransactionRelease model       |
        +-------------------+--------------------------------------------+
    """

    doi = ForeignKeyField(
        DOIEntries, backref='transactions', field='doi', column_name='doi', primary_key=True)
    transaction = ForeignKeyField(TransactionUser, backref='doi_releases')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(DOITransaction, self).to_hash(**flags)
        obj['_id'] = index_hash(
            unicode_type(self.__data__['doi']),
            str(self.__data__['transaction'])
        )
        obj['doi'] = unicode_type(self.__data__['doi'])
        obj['transaction'] = str(self.__data__['transaction'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(DOITransaction, self).from_hash(obj)
        self._set_only_if('doi', obj, 'doi',
                          lambda: DOIEntries.get(DOIEntries.doi == obj['doi']))
        self._set_only_if('transaction', obj, 'transaction',
                          lambda: TransactionUser.get(TransactionUser.uuid == obj['transaction']))

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(DOITransaction, cls).where_clause(kwargs)
        return cls._where_attr_clause(where_clause, kwargs, ['doi', 'transaction'])
