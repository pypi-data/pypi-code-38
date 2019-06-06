#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TransactionKeyValue links Transactions and Keys and Values objects."""
from peewee import ForeignKeyField, CompositeKey
from .base import DB
from .utils import index_hash
from .transactions import Transactions
from .analytical_tools import AnalyticalTools
from ..rest.orm import CherryPyAPI


class AToolTransaction(CherryPyAPI):
    """
    TransactionKeyValue attributes are foreign keys.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | transaction       | Link to the Transactions model      |
        +-------------------+-------------------------------------+
        | analytical_tool   | Link to the AnalyticalTools model   |
        +-------------------+-------------------------------------+
    """

    transaction = ForeignKeyField(Transactions, backref='atools')
    analytical_tool = ForeignKeyField(AnalyticalTools, backref='transactions')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('analytical_tool', 'transaction')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(AToolTransaction, self).to_hash(**flags)
        obj['_id'] = index_hash(int(self.__data__['transaction']),
                                int(self.__data__['analytical_tool']))
        obj['transaction'] = int(self.__data__['transaction'])
        obj['analytical_tool'] = int(self.__data__['analytical_tool'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(AToolTransaction, self).from_hash(obj)
        self._set_only_if(
            'analytical_tool', obj, 'analytical_tool',
            lambda: AnalyticalTools.get(AnalyticalTools.id == obj['analytical_tool'])
        )
        self._set_only_if(
            'transaction', obj, 'transaction',
            lambda: Transactions.get(Transactions.id == obj['transaction'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(AToolTransaction, cls).where_clause(kwargs)
        attrs = ['analytical_tool', 'transaction']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
