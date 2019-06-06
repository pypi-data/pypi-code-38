#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains model for groups."""
from peewee import TextField, CharField, BooleanField, Expression, OP
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class Groups(CherryPyAPI):
    """
    Groups model and associated fields.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | name              | name of the group                   |
        +-------------------+-------------------------------------+
        | is_admin          | does the group has admin abilities  |
        +-------------------+-------------------------------------+
        | display_name      | group display name                  |
        +-------------------+-------------------------------------+
        | description       | group long description              |
        +-------------------+-------------------------------------+
        | encoding          | encoding for the group name         |
        +-------------------+-------------------------------------+
    """

    name = CharField(default='')
    is_admin = BooleanField(default=False)
    display_name = CharField(default='', index=True)
    description = TextField(default='')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Groups, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        for attr in ['name', 'display_name', 'description']:
            obj[attr] = unicode_type(getattr(self, attr))
        obj['encoding'] = str(self.encoding)
        obj['is_admin'] = bool(self.is_admin)
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(Groups, self).from_hash(obj)
        self._set_only_if(
            '_id', obj, 'id', lambda: obj['_id']
        )
        for attr in ['name', 'display_name', 'description']:
            self._set_only_if(
                attr, obj, attr, lambda o=obj, a=attr: unicode_type(o[a])
            )
        self._set_only_if(
            'encoding', obj, 'encoding', lambda: str(obj['encoding'])
        )
        self._set_only_if(
            'is_admin', obj, 'is_admin', lambda: self._bool_translate(obj['is_admin'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Groups, cls).where_clause(kwargs)
        if '_id' in kwargs:
            where_clause &= Expression(Groups.id, OP.EQ, kwargs['_id'])
        if 'is_admin' in kwargs:
            kwargs['is_admin'] = cls._bool_translate(kwargs['is_admin'])
        return cls._where_attr_clause(
            where_clause,
            kwargs,
            ['name', 'display_name', 'description', 'is_admin', 'encoding']
        )
