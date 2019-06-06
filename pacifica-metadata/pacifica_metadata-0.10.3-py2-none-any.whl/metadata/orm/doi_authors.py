#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Secondary author list for DOI entries."""
from peewee import CharField
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


class DOIAuthors(CherryPyAPI):
    """
    DOI Authors Model.

    Attributes:
        +-------------------+-----------------------------------------+
        | Name              | Description                             |
        +===================+=========================================+
        | last_name         | Author last name                        |
        +-------------------+-----------------------------------------+
        | first_name        | Author first name                       |
        +-------------------+-----------------------------------------+
        | email             | Author email address                    |
        +-------------------+-----------------------------------------+
        | affiliation       | Institutional affiliation               |
        +-------------------+-----------------------------------------+
        | orcid             | Author's ORCID ID                       |
        +-------------------+-----------------------------------------+
    """

    last_name = CharField()
    first_name = CharField()
    email = CharField(null=True)
    affiliation = CharField(null=True)
    orcid = CharField(null=True)

    def to_hash(self, **flags):
        """Convert the object to a hash."""
        obj = super(DOIAuthors, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        obj['last_name'] = unicode_type(self.last_name)
        obj['first_name'] = unicode_type(self.first_name)
        obj['email'] = unicode_type(self.email)
        obj['affiliation'] = unicode_type(self.affiliation)
        obj['orcid'] = unicode_type(self.orcid)
        return obj

    def from_hash(self, obj):
        """Convert the hash to the object."""
        super(DOIAuthors, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('last_name', obj, 'last_name',
                          lambda: unicode_type(obj['last_name']))
        self._set_only_if('first_name', obj, 'first_name',
                          lambda: unicode_type(obj['first_name']))
        self._set_only_if('email', obj, 'email',
                          lambda: unicode_type(obj['email']))
        self._set_only_if('affiliation', obj, 'affiliation',
                          lambda: unicode_type(obj['affiliation']))
        self._set_only_if('orcid', obj, 'orcid',
                          lambda: unicode_type(obj['orcid']))

    @classmethod
    def where_clause(cls, kwargs):
        """Where clause for the various elements."""
        where_clause = super(DOIAuthors, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause, kwargs,
            ['last_name', 'first_name', 'email', 'affiliation', 'orcid']
        )
