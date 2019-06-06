#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Contributors model describes an author to a journal article."""
from peewee import CharField, ForeignKeyField
from .users import Users
from .institutions import Institutions
from ..rest.orm import CherryPyAPI
from .utils import unicode_type


# pylint: disable=too-many-instance-attributes
class Contributors(CherryPyAPI):
    """
    Contributors object and associated fields.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | user              | Link to the User model              |
        +-------------------+-------------------------------------+
        | institution       | Link to the Institution model       |
        +-------------------+-------------------------------------+
        | first_name        | Users first name as it appears in   |
        |                   | the citation                        |
        +-------------------+-------------------------------------+
        | middle_initial    | Users middle initial as it appears  |
        |                   | in the citation                     |
        +-------------------+-------------------------------------+
        | last_name         | Users last name as it appears in    |
        |                   | the citation                        |
        +-------------------+-------------------------------------+
        | dept_code         | Department of the institution the   |
        |                   | User was a member of at the time of |
        |                   | the citation                        |
        +-------------------+-------------------------------------+
        | encoding          | Language encoding of the attributes |
        |                   | above                               |
        +-------------------+-------------------------------------+
    """

    user = ForeignKeyField(Users, backref='contributions')
    first_name = CharField(default='')
    middle_initial = CharField(default='')
    last_name = CharField(default='')
    dept_code = CharField(default='')
    institution = ForeignKeyField(Institutions, backref='contributors')
    encoding = CharField(default='UTF8')

    def to_hash(self, **flags):
        """Convert the object fields into a serializable hash."""
        obj = super(Contributors, self).to_hash(**flags)
        obj['_id'] = int(self.id)
        obj['first_name'] = unicode_type(self.first_name)
        obj['middle_initial'] = unicode_type(self.middle_initial)
        obj['last_name'] = unicode_type(self.last_name)
        obj['dept_code'] = unicode_type(self.dept_code)
        # pylint: disable=no-member
        obj['user'] = int(self.__data__['user'])
        obj['institution'] = int(self.__data__['institution'])
        # pylint: enable=no-member
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object fields."""
        super(Contributors, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        for attr in ['first_name', 'middle_initial', 'last_name', 'dept_code']:
            self._set_only_if(
                attr, obj, attr, lambda k=attr: unicode_type(obj[k]))
        self._set_only_if('user', obj, 'user',
                          lambda: Users.get(Users.id == int(obj['user'])))
        self._set_only_if('institution', obj, 'institution',
                          lambda: Institutions.get(Institutions.id == int(obj['institution'])))
        self._set_only_if('encoding', obj, 'encoding',
                          lambda: str(obj['encoding']))

    @classmethod
    def where_clause(cls, kwargs):
        """Generate the PeeWee where clause used in searching."""
        where_clause = super(Contributors, cls).where_clause(kwargs)
        return cls._where_attr_clause(
            where_clause,
            kwargs,
            [
                'user',
                'institution',
                'first_name',
                'last_name',
                'encoding',
                'middle_initial',
                'dept_code'
            ]
        )
