#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Citation project relationship."""
from peewee import ForeignKeyField, CompositeKey
from .utils import index_hash, unicode_type
from .projects import Projects
from .citations import Citations
from .base import DB
from ..rest.orm import CherryPyAPI


class CitationProject(CherryPyAPI):
    """
    Relates citations with projects.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | citation          | Link to the Citation model          |
        +-------------------+-------------------------------------+
        | project           | Link to the Project model           |
        +-------------------+-------------------------------------+
    """

    citation = ForeignKeyField(Citations, backref='projects')
    project = ForeignKeyField(Projects, backref='citations')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('citation', 'project')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(CitationProject, self).to_hash(**flags)
        obj['_id'] = index_hash(int(self.__data__['citation']),
                                unicode_type(self.__data__['project']))
        obj['citation'] = int(self.__data__['citation'])
        obj['project'] = unicode_type(self.__data__['project'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(CitationProject, self).from_hash(obj)
        self._set_only_if(
            'citation', obj, 'citation',
            lambda: Citations.get(Citations.id == obj['citation'])
        )
        self._set_only_if(
            'project', obj, 'project',
            lambda: Projects.get(Projects.id == obj['project'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(CitationProject, cls).where_clause(kwargs)
        attrs = ['citation', 'project']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
