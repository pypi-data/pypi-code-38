#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Project group relationship."""
from peewee import ForeignKeyField, CompositeKey
from .utils import index_hash, unicode_type
from .projects import Projects
from .groups import Groups
from .base import DB
from ..rest.orm import CherryPyAPI


class ProjectGroup(CherryPyAPI):
    """
    Relates projects and groups objects.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | group             | Link to the Group model             |
        +-------------------+-------------------------------------+
        | project           | Link to the Project model           |
        +-------------------+-------------------------------------+
    """

    group = ForeignKeyField(Groups, backref='projects')
    project = ForeignKeyField(Projects, backref='groups')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('group', 'project')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(ProjectGroup, self).to_hash(**flags)
        obj['_id'] = index_hash(unicode_type(
            self.__data__['project']), int(self.__data__['group']))
        obj['group'] = int(self.__data__['group'])
        obj['project'] = unicode_type(self.__data__['project'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(ProjectGroup, self).from_hash(obj)
        self._set_only_if(
            'project', obj, 'project',
            lambda: Projects.get(Projects.id == obj['project'])
        )
        self._set_only_if(
            'group', obj, 'group',
            lambda: Groups.get(Groups.id == obj['group'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(ProjectGroup, cls).where_clause(kwargs)
        attrs = ['group', 'project']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
