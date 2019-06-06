#!/usr/bin/python
# -*- coding: utf-8 -*-
"""UserGroup links Groups and Users and objects."""
from peewee import ForeignKeyField, CompositeKey
from .utils import index_hash
from .base import DB
from ..rest.orm import CherryPyAPI
from .groups import Groups
from .users import Users


class UserGroup(CherryPyAPI):
    """
    UserGroup attributes are foreign keys.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | person            | Link to the Users model             |
        +-------------------+-------------------------------------+
        | group             | Link to the Groups model            |
        +-------------------+-------------------------------------+
    """

    person = ForeignKeyField(Users, backref='groups')
    group = ForeignKeyField(Groups, backref='members')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        primary_key = CompositeKey('person', 'group')
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(UserGroup, self).to_hash(**flags)
        obj['_id'] = index_hash(
            int(self.__data__['person']), int(self.__data__['group']))
        obj['person'] = int(self.__data__['person'])
        obj['group'] = int(self.__data__['group'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(UserGroup, self).from_hash(obj)
        self._set_only_if(
            'person', obj, 'person',
            lambda: Users.get(Users.id == obj['person'])
        )
        self._set_only_if(
            'group', obj, 'group',
            lambda: Groups.get(Groups.id == obj['group'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(UserGroup, cls).where_clause(kwargs)
        attrs = ['person', 'group']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
