#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TransSIP model."""
from peewee import ForeignKeyField, Expression, OP
from ..rest.orm import CherryPyAPI
from .transactions import Transactions
from .users import Users
from .projects import Projects
from .instruments import Instruments
from .utils import unicode_type


class TransSIP(CherryPyAPI):
    """
    TransSIP model class.

    Attributes:
        +-------------------+--------------------------------------+
        | Name              | Description                          |
        +===================+======================================+
        | submitter         | User who submitted the transaction   |
        +-------------------+--------------------------------------+
        | instrument        | Instrument the transaction came from |
        +-------------------+--------------------------------------+
        | project           | Project the transaction is for       |
        +-------------------+--------------------------------------+
        | suspense_date     | date the transaction is available    |
        +-------------------+--------------------------------------+
    """

    id = ForeignKeyField(
        Transactions, index=True, primary_key=True,
        unique=True, backref='transsip'
    )
    submitter = ForeignKeyField(Users, backref='transsip')
    instrument = ForeignKeyField(Instruments, backref='transsip')
    project = ForeignKeyField(Projects, backref='transsip')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(TransSIP, self).to_hash(**flags)
        obj['_id'] = int(self.__data__['id'])
        obj['submitter'] = int(self.__data__['submitter'])
        obj['instrument'] = int(self.__data__['instrument'])
        obj['project'] = unicode_type(self.__data__['project'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(TransSIP, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        attr_cls_map = [
            ('submitter', Users),
            ('instrument', Instruments),
            ('project', Projects)
        ]
        for key, obj_cls in attr_cls_map:
            self._set_only_if(
                key, obj, key, lambda o=obj_cls, k=key: o.get(o.id == obj[k]))

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(TransSIP, cls).where_clause(kwargs)
        if '_id' in kwargs:
            where_clause &= Expression(TransSIP.id, OP.EQ, kwargs['_id'])
        return cls._where_attr_clause(
            where_clause,
            kwargs,
            [
                'submitter',
                'instrument',
                'project'
            ]
        )
