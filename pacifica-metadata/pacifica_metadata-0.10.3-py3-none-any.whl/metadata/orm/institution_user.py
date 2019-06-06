#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Connects a User with an Institution."""
import uuid
from peewee import ForeignKeyField, UUIDField
from .users import Users
from .relationships import Relationships
from .institutions import Institutions
from .base import DB
from ..rest.orm import CherryPyAPI


class InstitutionUser(CherryPyAPI):
    """
    Relates persons and institution objects.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | user              | Link to the Users model             |
        +-------------------+-------------------------------------+
        | relationship      | Link to the Relationships model     |
        +-------------------+-------------------------------------+
        | institution       | Link to the Institutions model      |
        +-------------------+-------------------------------------+
    """

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    user = ForeignKeyField(Users, backref='institutions')
    institution = ForeignKeyField(Institutions, backref='users')
    relationship = ForeignKeyField(Relationships, backref='institution_user')

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the database and the primary key."""

        database = DB
        indexes = (
            (('user', 'institution', 'relationship'), True),
        )
    # pylint: enable=too-few-public-methods

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(InstitutionUser, self).to_hash(**flags)
        obj['uuid'] = str(self.__data__['uuid'])
        obj['user'] = int(self.__data__['user'])
        obj['institution'] = int(self.__data__['institution'])
        obj['relationship'] = str(self.__data__['relationship'])
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(InstitutionUser, self).from_hash(obj)
        self._set_only_if('uuid', obj, 'uuid',
                          lambda: uuid.UUID(obj['uuid']))
        self._set_only_if_by_name('relationship', obj, Relationships)
        self._set_only_if(
            'user', obj, 'user',
            lambda: Users.get(Users.id == obj['user'])
        )
        self._set_only_if(
            'institution', obj, 'institution',
            lambda: Institutions.get(Institutions.id == obj['institution'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(InstitutionUser, cls).where_clause(kwargs)
        attrs = ['uuid', 'user', 'institution', 'relationship']
        return cls._where_attr_clause(where_clause, kwargs, attrs)
