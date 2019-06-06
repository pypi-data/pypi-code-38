#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Project instrument relationship."""
import uuid
from peewee import ForeignKeyField, UUIDField
from .utils import unicode_type
from .projects import Projects
from .instruments import Instruments
from .relationships import Relationships
from .base import DB
from ..rest.orm import CherryPyAPI


class ProjectInstrument(CherryPyAPI):
    """
    Relates projects and instrument objects.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | instrument        | Link to the Instrument model        |
        +-------------------+-------------------------------------+
        | relationship      | Link to the Relationship model      |
        +-------------------+-------------------------------------+
        | project           | Link to the Project model           |
        +-------------------+-------------------------------------+
    """

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    project = ForeignKeyField(Projects, backref='instruments')
    instrument = ForeignKeyField(Instruments, backref='projects')
    relationship = ForeignKeyField(Relationships, backref='relationship')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        indexes = (
            (('project', 'instrument', 'relationship'), True),
        )
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(ProjectInstrument, self).to_hash(**flags)
        obj['uuid'] = str(self.__data__['uuid'])
        obj['instrument'] = int(self.__data__['instrument'])
        obj['project'] = unicode_type(self.__data__['project'])
        obj['relationship'] = str(self.__data__['relationship'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(ProjectInstrument, self).from_hash(obj)
        self._set_only_if('uuid', obj, 'uuid',
                          lambda: uuid.UUID(obj['uuid']))
        self._set_only_if_by_name('relationship', obj, Relationships)
        self._set_only_if(
            'instrument', obj, 'instrument',
            lambda: Instruments.get(Instruments.id == obj['instrument'])
        )
        self._set_only_if(
            'project', obj, 'project',
            lambda: Projects.get(Projects.id == obj['project'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(ProjectInstrument, cls).where_clause(kwargs)
        attrs = ['uuid', 'instrument', 'project', 'relationship']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
