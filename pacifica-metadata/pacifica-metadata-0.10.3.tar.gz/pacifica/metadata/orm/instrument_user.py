#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instrument user relationship."""
import uuid
from peewee import ForeignKeyField, UUIDField
from .users import Users
from .relationships import Relationships
from .instruments import Instruments
from .base import DB
from ..rest.orm import CherryPyAPI


class InstrumentUser(CherryPyAPI):
    """
    Relates users and instrument objects.

    Attributes:
        +--------------+--------------------------------------------+
        | Name         | Description                                |
        +==============+============================================+
        | instrument   | Link to the Instrument model               |
        +--------------+--------------------------------------------+
        | relationship | Link to the Relationship model             |
        +--------------+--------------------------------------------+
        | user         | User who is responsible for the instrument |
        +--------------+--------------------------------------------+
    """

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    instrument = ForeignKeyField(Instruments, backref='custodians')
    user = ForeignKeyField(Users, backref='instruments')
    relationship = ForeignKeyField(Relationships, backref='instrument_user')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        indexes = (
            (('user', 'instrument', 'relationship'), True),
        )
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(InstrumentUser, self).to_hash(**flags)
        obj['uuid'] = str(self.__data__['uuid'])
        obj['instrument'] = int(self.__data__['instrument'])
        obj['user'] = int(self.__data__['user'])
        obj['relationship'] = str(self.__data__['relationship'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(InstrumentUser, self).from_hash(obj)
        self._set_only_if('uuid', obj, 'uuid',
                          lambda: uuid.UUID(obj['uuid']))
        self._set_only_if_by_name('relationship', obj, Relationships)
        self._set_only_if(
            'instrument', obj, 'instrument',
            lambda: Instruments.get(Instruments.id == obj['instrument'])
        )
        self._set_only_if(
            'user', obj, 'user',
            lambda: Users.get(Users.id == obj['user'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(InstrumentUser, cls).where_clause(kwargs)
        attrs = ['uuid', 'instrument', 'user', 'relationship']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
