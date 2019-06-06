#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Instrument Data Source relationship."""
import uuid
from peewee import ForeignKeyField, CompositeKey
from .utils import index_hash
from .instruments import Instruments
from .data_sources import DataSources
from .relationships import Relationships
from .base import DB
from ..rest.orm import CherryPyAPI


class InstrumentDataSource(CherryPyAPI):
    """
    Relates instruments and data sources objects.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | instrument        | Link to the Instruments model       |
        +-------------------+-------------------------------------+
        | data_source       | Link to the DataSources model       |
        +-------------------+-------------------------------------+
        | relationship      | Link to the Relationships model     |
        +-------------------+-------------------------------------+
    """

    instrument = ForeignKeyField(Instruments, backref='data_sources')
    data_source = ForeignKeyField(DataSources, backref='instruments')
    relationship = ForeignKeyField(Relationships, backref='instrument_data_source')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('instrument', 'data_source', 'relationship')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(InstrumentDataSource, self).to_hash(**flags)
        obj['_id'] = index_hash(
            int(self.__data__['instrument']),
            str(self.__data__['data_source']),
            str(self.__data__['relationship']),
        )
        obj['instrument'] = int(self.__data__['instrument'])
        obj['data_source'] = str(self.__data__['data_source'])
        obj['relationship'] = str(self.__data__['relationship'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(InstrumentDataSource, self).from_hash(obj)
        self._set_only_if(
            'instrument', obj, 'instrument',
            lambda: Instruments.get(Instruments.id == int(obj['instrument']))
        )
        self._set_only_if_by_name('relationship', obj, Relationships)
        attr_rel_cls = [('data_source', DataSources)]
        for attr, rel_cls in attr_rel_cls:
            self._set_only_if(
                attr, obj, attr, lambda cls=rel_cls, o=obj, a=attr: cls.get(cls.uuid == uuid.UUID(o[a]))
            )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(InstrumentDataSource, cls).where_clause(kwargs)
        attrs = ['instrument', 'data_source', 'relationship']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
