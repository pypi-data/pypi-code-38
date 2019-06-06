#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Transactions model."""
from peewee import TextField, Expression
from ..rest.orm import CherryPyAPI
from .utils import unicode_type, ExtendDateField, date_converts


class Transactions(CherryPyAPI):
    """
    Transactions model class.

    Attributes:
        +-------------------+--------------------------------------+
        | Name              | Description                          |
        +===================+======================================+
        | description       | Description of the transaction       |
        +-------------------+--------------------------------------+
        | suspense_date     | date the transaction is available    |
        +-------------------+--------------------------------------+
    """

    description = TextField(null=True)
    suspense_date = ExtendDateField(null=True, index=True)

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Transactions, self).to_hash(**flags)
        obj['_id'] = int(self.id) if self.id is not None else obj['_id']
        obj['description'] = unicode_type(self.__data__['description'])
        obj['suspense_date'] = str(self.suspense_date.isoformat(
        )) if self.suspense_date is not None else None
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(Transactions, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('description', obj, 'description',
                          lambda: unicode_type(obj['description']))
        self._set_date_part('suspense_date', obj)

    @classmethod
    def _where_date_clause(cls, where_clause, kwargs):
        for date in ['suspense_date']:
            if date in kwargs:
                date_obj, date_oper = cls._date_operator_compare(
                    date, kwargs, dt_converts=date_converts)
                where_clause &= Expression(
                    getattr(Transactions, date), date_oper, date_obj)
        return where_clause

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(Transactions, cls).where_clause(kwargs)
        where_clause = cls._where_date_clause(where_clause, kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs, ['description']
        )
