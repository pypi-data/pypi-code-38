#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contains the model for metadata keys."""
import uuid
from peewee import CharField, TextField, UUIDField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class Relationships(CherryPyAPI):
    """
    Relationships model class for metadata.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | uuid              | relationship unique ID              |
        +-------------------+-------------------------------------+
        | name              | relationship name                   |
        +-------------------+-------------------------------------+
        | display_name      | relationship display name           |
        +-------------------+-------------------------------------+
        | description       | relationship long description       |
        +-------------------+-------------------------------------+
        | encoding          | encoding for the name               |
        +-------------------+-------------------------------------+
    """

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    name = CharField(default='', unique=True, index=True)
    display_name = CharField(default='', index=True)
    description = TextField(default='')
    encoding = CharField(default='UTF8')

    @classmethod
    def create_table(cls, safe=True, **options):
        """Create the table and populate it with initial relationships."""
        super(Relationships, cls).create_table()
        static_relationships = [
            {
                'name': 'upload_required',
                'display_name': 'Required for Upload',
                'description': 'This relationship means that the objects are required for upload to be asserted.'
            },
            {
                'name': 'search_required',
                'display_name': 'Required for Search',
                'description': 'This relationship means that the objects are required for search to be asserted.'
            },
            {
                'name': 'member_of',
                'display_name': 'Member of',
                'description': 'subject is a member of the object'
            },
            {
                'name': 'co_principle_investigator',
                'display_name': 'Co-Principle Investigator',
                'description': 'subject is the co-principle investigator of the object'
            },
            {
                'name': 'principle_investigator',
                'display_name': 'Principle Investigator',
                'description': 'subject is the principle investigator of the object'
            },
            {
                'name': 'custodian',
                'display_name': 'Custodian',
                'description': 'subject is the custodian of the object'
            },
            {
                'name': 'point_of_contact',
                'display_name': 'Point of Contact',
                'description': 'subject is the point of contact for the object'
            },
            {
                'name': 'authorized_releaser',
                'display_name': 'Authorized Releaser',
                'description': 'subject is the authorized releaser of the object'
            }
        ]
        for static_rel in static_relationships:
            Relationships.get_or_create(**static_rel)

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(Relationships, self).to_hash(**flags)
        obj['uuid'] = str(self.uuid)
        for attr in ['name', 'display_name', 'description']:
            obj[attr] = unicode_type(getattr(self, attr))
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(Relationships, self).from_hash(obj)
        self._set_only_if(
            'uuid', obj, 'uuid', lambda: uuid.UUID(obj['uuid'])
        )
        for attr in ['name', 'display_name', 'description']:
            self._set_only_if(
                attr, obj, attr, lambda o=obj, a=attr: unicode_type(o[a])
            )
        self._set_only_if(
            'encoding', obj, 'encoding', lambda: str(obj['encoding'])
        )

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Relationships, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs,
            ['uuid', 'name', 'description', 'display_name', 'encoding']
        )
