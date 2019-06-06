#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains the model for metadata transaction user."""
import uuid
from peewee import ForeignKeyField, UUIDField
from ..rest.orm import CherryPyAPI
from .users import Users
from .relationships import Relationships
from .transactions import Transactions
from .base import DB


class TransactionUser(CherryPyAPI):
    """
    TransactionUser model class for transaction user relationships.

    Attributes:
        +-------------------+-----------------------------------------------+
        | Name              | Description                                   |
        +===================+===============================================+
        | uuid              | uuid for the relationship                     |
        +-------------------+-----------------------------------------------+
        | transaction       | transaction to be acted upon                  |
        +-------------------+-----------------------------------------------+
        | relationship      | relationship to transaction                   |
        +-------------------+-----------------------------------------------+
        | user              | user reference                                |
        +-------------------+-----------------------------------------------+
    """

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    user = ForeignKeyField(Users, backref='transactions')
    transaction = ForeignKeyField(Transactions, backref='users')
    relationship = ForeignKeyField(Relationships, backref='transaction_user')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        indexes = (
            (('user', 'transaction', 'relationship'), True),
        )
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(TransactionUser, self).to_hash(**flags)
        obj['uuid'] = str(self.__data__['uuid'])
        obj['relationship'] = str(self.__data__['relationship'])
        obj['transaction'] = int(self.__data__['transaction'])
        obj['user'] = int(self.__data__['user'])
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(TransactionUser, self).from_hash(obj)
        self._set_only_if('uuid', obj, 'uuid',
                          lambda: uuid.UUID(obj['uuid']))
        self._set_only_if_by_name('relationship', obj, Relationships)
        self._set_only_if('transaction', obj, 'transaction',
                          lambda: Transactions.get(Transactions.id == obj['transaction']))
        self._set_only_if('user', obj, 'user',
                          lambda: Users.get(Users.id == obj['user']))

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(TransactionUser, cls).where_clause(kwargs)
        return cls._where_attr_clause(where_clause, kwargs, ['uuid', 'user', 'relationship', 'transaction'])
