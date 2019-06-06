#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TransactionKeyValue links Transactions and Keys and Values objects."""
from peewee import ForeignKeyField, CompositeKey
from .base import DB
from .utils import index_hash
from .instruments import Instruments
from .values import Values
from .keys import Keys
from .relationships import Relationships
from ..rest.orm import CherryPyAPI


class InstrumentKeyValue(CherryPyAPI):
    """
    InstrumentKeyValue attributes are foreign keys.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | instrument        | Link to the Instruments model       |
        +-------------------+-------------------------------------+
        | key               | Link to the Keys model              |
        +-------------------+-------------------------------------+
        | value             | Link to the Values model            |
        +-------------------+-------------------------------------+
        | relationship      | Link to the Relationships model     |
        +-------------------+-------------------------------------+
    """

    instrument = ForeignKeyField(Instruments, backref='metadata')
    key = ForeignKeyField(Keys, backref='instrument_links')
    value = ForeignKeyField(Values, backref='instrument_links')
    relationship = ForeignKeyField(Relationships, backref='instrument_kvp')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('instrument', 'key', 'value', 'relationship')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(InstrumentKeyValue, self).to_hash(**flags)
        obj['_id'] = index_hash(int(self.__data__['key']),
                                int(self.__data__['instrument']),
                                int(self.__data__['value']),
                                str(self.__data__['relationship']))
        obj['instrument'] = int(self.__data__['instrument'])
        obj['key'] = int(self.__data__['key'])
        obj['value'] = int(self.__data__['value'])
        obj['relationship'] = str(self.__data__['relationship'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(InstrumentKeyValue, self).from_hash(obj)
        attr_rel_cls = [
            ('instrument', Instruments),
            ('key', Keys),
            ('value', Values)
        ]
        for attr, rel_cls in attr_rel_cls:
            self._set_only_if(
                attr, obj, attr,
                lambda cls=rel_cls, a=attr: cls.get(cls.id == obj[a])
            )
        self._set_only_if_by_name('relationship', obj, Relationships)

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(InstrumentKeyValue, cls).where_clause(kwargs)
        attrs = ['instrument', 'key', 'value', 'relationship']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
