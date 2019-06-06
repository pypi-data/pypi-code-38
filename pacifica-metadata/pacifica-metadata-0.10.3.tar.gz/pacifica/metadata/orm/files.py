#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains the Files object model primary unit of metadata for Pacifica."""
from peewee import ForeignKeyField, CharField, BigIntegerField, Expression
from ..rest.orm import CherryPyAPI
from .transactions import Transactions
from .utils import datetime_now_nomicrosecond, ExtendDateTimeField
from .utils import unicode_type, ExtendDateField, date_converts


# pylint: disable=too-many-instance-attributes
class Files(CherryPyAPI):
    """
    Files metadata.

    This object contains various attributes describing a file and where
    it came from.

    Attributes:
        +---------------+-------------------------------------------+
        | Name          | Description                               |
        +===============+===========================================+
        | name          | Name of the file                          |
        +---------------+-------------------------------------------+
        | subdir        | Subdirectory the file is in               |
        +---------------+-------------------------------------------+
        | ctime         | Creation time for the file                |
        +---------------+-------------------------------------------+
        | mtime         | User modified time for the file           |
        +---------------+-------------------------------------------+
        | hashsum       | Hash sum string                           |
        +---------------+-------------------------------------------+
        | hashtype      | Hash sum type string                      |
        +---------------+-------------------------------------------+
        | size          | Size of the file in bytes                 |
        +---------------+-------------------------------------------+
        | transaction   | Link to the transaction model             |
        +---------------+-------------------------------------------+
        | mimetype      | mimetype of the file, if any              |
        +---------------+-------------------------------------------+
        | suspense_date | date the project is made available        |
        +---------------+-------------------------------------------+
        | encoding      | encoding in the file name or subdir field |
        +---------------+-------------------------------------------+
    """

    name = CharField(default='', index=True)
    subdir = CharField(default='', index=True)
    ctime = ExtendDateTimeField(default=datetime_now_nomicrosecond, index=True)
    mtime = ExtendDateTimeField(default=datetime_now_nomicrosecond, index=True)
    hashsum = CharField(default='', index=True)
    hashtype = CharField(default='sha1', index=True)
    size = BigIntegerField(default=-1)
    transaction = ForeignKeyField(Transactions, backref='files', index=True)
    mimetype = CharField(default='')
    encoding = CharField(default='UTF8')
    suspense_date = ExtendDateField(null=True, index=True)

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Files, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        obj['name'] = unicode_type(self.name)
        obj['subdir'] = unicode_type(self.subdir)
        obj['mimetype'] = str(self.mimetype)
        # pylint: disable=no-member
        obj['ctime'] = self.ctime.isoformat()
        obj['mtime'] = self.mtime.isoformat()
        obj['transaction'] = int(self.__data__['transaction'])
        # pylint: enable=no-member
        obj['size'] = int(self.size)
        obj['hashsum'] = str(self.hashsum)
        obj['hashtype'] = str(self.hashtype)
        obj['suspense_date'] = str(self.suspense_date.isoformat(
        )) if self.suspense_date is not None else None
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash to an object."""
        super(Files, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('name', obj, 'name',
                          lambda: unicode_type(obj['name']))
        self._set_only_if('subdir', obj, 'subdir',
                          lambda: unicode_type(obj['subdir']))
        self._set_only_if('mimetype', obj, 'mimetype',
                          lambda: str(obj['mimetype']))
        self._set_datetime_part('ctime', obj)
        self._set_datetime_part('mtime', obj)
        self._set_only_if('hashtype', obj, 'hashtype',
                          lambda: str(obj['hashtype']))
        self._set_only_if('hashsum', obj, 'hashsum',
                          lambda: str(obj['hashsum']))
        self._set_only_if('size', obj, 'size', lambda: int(obj['size']))
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))
        self._set_date_part('suspense_date', obj)

        def trans_func():
            """Return the transaction for the obj id."""
            return Transactions.get(Transactions.id == obj['transaction'])
        self._set_only_if('transaction', obj, 'transaction', trans_func)

    @classmethod
    def _where_date_clause(cls, where_clause, kwargs):
        if 'suspense_date' in kwargs:
            date_obj, date_oper = cls._date_operator_compare(
                'suspense_date',
                kwargs,
                dt_converts=date_converts
            )
            where_clause &= Expression(
                Files.suspense_date, date_oper, date_obj)
        for date in ['mtime', 'ctime']:
            if date in kwargs:
                date_obj, date_oper = cls._date_operator_compare(date, kwargs)
                where_clause &= Expression(
                    getattr(Files, date), date_oper, date_obj)
        return where_clause

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where expression."""
        where_clause = super(Files, cls).where_clause(kwargs)
        where_clause = cls._where_date_clause(where_clause, kwargs)
        where_clause = cls._where_attr_clause(
            where_clause,
            kwargs,
            [
                'name',
                'transaction',
                'subdir',
                'mimetype',
                'size',
                'encoding',
                'hashtype',
                'hashsum'
            ]
        )
        return where_clause
