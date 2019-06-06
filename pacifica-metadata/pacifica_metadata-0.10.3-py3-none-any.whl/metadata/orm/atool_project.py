#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TransactionKeyValue links Transactions and Keys and Values objects."""
from peewee import ForeignKeyField, CompositeKey
from .base import DB
from .utils import index_hash, unicode_type
from .projects import Projects
from .analytical_tools import AnalyticalTools
from ..rest.orm import CherryPyAPI


class AToolProject(CherryPyAPI):
    """
    TransactionKeyValue attributes are foreign keys.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | project           | Link to the Projects model          |
        +-------------------+-------------------------------------+
        | analytical_tool   | Link to the AnalyticalTools model   |
        +-------------------+-------------------------------------+
    """

    project = ForeignKeyField(Projects, backref='atools')
    analytical_tool = ForeignKeyField(AnalyticalTools, backref='projects')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('analytical_tool', 'project')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(AToolProject, self).to_hash(**flags)
        obj['_id'] = index_hash(unicode_type(self.__data__['project']),
                                int(self.__data__['analytical_tool']))
        obj['project'] = unicode_type(self.__data__['project'])
        obj['analytical_tool'] = int(self.__data__['analytical_tool'])

        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(AToolProject, self).from_hash(obj)
        self._set_only_if('project', obj, 'project',
                          lambda: Projects.get(Projects.id == obj['project']))
        self._set_only_if('analytical_tool', obj, 'analytical_tool',
                          lambda: AnalyticalTools.get(
                              AnalyticalTools.id == obj['analytical_tool']))

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(AToolProject, cls).where_clause(kwargs)
        attrs = ['project', 'analytical_tool']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
