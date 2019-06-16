# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data Models for Users & Permissions
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import association_proxy

from rattail.db.model import Base, uuid_column, getset_factory, Person
 

@six.python_2_unicode_compatible
class Role(Base):
    """
    Represents a role within the system; used to manage permissions.
    """
    __tablename__ = 'role'
    __table_args__ = (
        sa.UniqueConstraint('name', name='role_uq_name'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    name = sa.Column(sa.String(length=100), nullable=False, doc="""
    Name for the role.  Each role must have a name, which must be unique.
    """)

    session_timeout = sa.Column(sa.Integer(), nullable=True, doc="""
    Optional session timeout value for the role, in seconds.  If this is set to
    zero, the role's users will have no session timeout.  A value of ``None``
    means the role has no say in the timeout.
    """)

    def __str__(self):
        return self.name or ''


@six.python_2_unicode_compatible
class Permission(Base):
    """
    Represents permission a role has to do a particular thing.
    """
    __tablename__ = 'permission'
    __table_args__ = (
        sa.ForeignKeyConstraint(['role_uuid'], ['role.uuid'], name='permission_fk_role'),
        )
    # __versioned__ = {}

    role_uuid = sa.Column(sa.String(length=32), primary_key=True)
    permission = sa.Column(sa.String(length=50), primary_key=True)

    def __str__(self):
        return self.permission or ''


Role._permissions = orm.relationship(
    Permission, backref='role',
    cascade='save-update, merge, delete, delete-orphan')

Role.permissions = association_proxy(
    '_permissions', 'permission',
    creator=lambda p: Permission(permission=p),
    getset_factory=getset_factory)


@six.python_2_unicode_compatible
class User(Base):
    """
    Represents a user of the system.

    This may or may not correspond to a real person, i.e. some users may exist
    solely for automated tasks.
    """
    __tablename__ = 'user'
    __table_args__ = (
        sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='user_fk_person'),
        sa.UniqueConstraint('username', name='user_uq_username'),
        )
    __versioned__ = {'exclude': ['password', 'salt', 'last_login']}

    uuid = uuid_column()
    username = sa.Column(sa.String(length=25), nullable=False)
    password = sa.Column(sa.String(length=60))
    salt = sa.Column(sa.String(length=29))

    person_uuid = sa.Column(sa.String(length=32))
    person = orm.relationship(
        Person,
        uselist=False,
        backref=orm.backref(
            'user',
            uselist=False))

    active = sa.Column(sa.Boolean(), nullable=False, default=True, doc="""
    Whether the user is active, e.g. allowed to log in via the UI.
    """)

    active_sticky = sa.Column(sa.Boolean(), nullable=True, doc="""
    Optional flag, motivation behind which is as follows: If you import user
    accounts from another system, esp. on a regular basis, you might be keeping
    the :attr:`active` flag in sync along with that.  But in some cases you
    might want to *not* keep the active flag in sync, for certain accounts.
    Hence this "active sticky" flag, which may be used to mark certain accounts
    as off-limits from the general active flag sync.
    """)

    last_login = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when user last logged into the system.
    """)

    def __str__(self):
        if self.person and str(self.person):
            return str(self.person)
        return self.username or ''

    @property
    def display_name(self):
        """
        Display name for the user.
        
        Returns :attr:`Person.display_name` if available; otherwise returns
        :attr:`username`.
        """
        if self.person and self.person.display_name:
            return self.person.display_name
        return self.username

    @property
    def employee(self):
        """
        Reference to the :class:`Employee` associated with the user, if any.
        """
        if self.person:
            return self.person.employee

    def get_short_name(self):
        """
        Returns "short name" for the user.  This is for convenience of mobile
        view, at least...
        """
        # TODO: this should reference employee.short_name
        employee = self.employee
        if employee and employee.display_name:
            return employee.display_name

        person = self.person
        if person:
            if person.first_name and person.last_name:
                return "{} {}.".format(person.first_name, person.last_name[0])
            if person.first_name:
                return person.first_name

        return self.username

    def get_email_address(self):
        """
        Returns the primary email address for the user (as unicode string), or
        ``None``.  Note that currently there is no direct association between a
        User and an EmailAddress, so the Person and Customer relationships are
        navigated in an attempt to locate an address.
        """
        if self.person:
            if self.person.email:
                return self.person.email.address
            for customer in self.person.customers:
                if customer.email:
                    return customer.email.address

    @property
    def email_address(self):
        """
        Convenience attribute which invokes :meth:`get_email_address()`.

        .. note::
           The implementation of this may change some day, e.g. if the User is
           given an association to EmailAddress in the data model.
        """
        return self.get_email_address()

    def is_admin(self):
        """
        Convenience method to determine if current user is a member of the
        Administrator role.
        """
        from rattail.db.auth import administrator_role

        session = orm.object_session(self)
        return administrator_role(session) in self.roles

    def record_event(self, type_code, **kwargs):
        kwargs['type_code'] = type_code
        self.events.append(UserEvent(**kwargs))


Person.make_proxy(User, 'person', 'first_name')
Person.make_proxy(User, 'person', 'last_name')
Person.make_proxy(User, 'person', 'display_name')


class UserRole(Base):
    """
    Represents the association between a :class:`User` and a :class:`Role`.
    """
    __tablename__ = 'user_x_role'
    __table_args__ = (
        sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], name='user_x_role_fk_user'),
        sa.ForeignKeyConstraint(['role_uuid'], ['role.uuid'], name='user_x_role_fk_role'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    user_uuid = sa.Column(sa.String(length=32), nullable=False)
    role_uuid = sa.Column(sa.String(length=32), nullable=False)


Role._users = orm.relationship(
    UserRole, backref='role',
    cascade='all, delete-orphan')

Role.users = association_proxy(
    '_users', 'user',
    creator=lambda u: UserRole(user=u),
    getset_factory=getset_factory)

User._roles = orm.relationship(
    UserRole, backref='user',
    cascade='all, delete-orphan')

User.roles = association_proxy(
    '_roles', 'role',
    creator=lambda r: UserRole(role=r),
    getset_factory=getset_factory)


class UserEvent(Base):
    """
    Represents an event associated with a user.
    """
    __tablename__ = 'user_event'
    __table_args__ = (
        sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], name='user_x_role_fk_user'),
    )

    uuid = uuid_column()

    user_uuid = sa.Column(sa.String(length=32), nullable=False)
    user = orm.relationship(
        User,
        doc="""
        Reference to the user whose event this is.
        """,
        backref=orm.backref(
            'events',
            cascade='all, delete-orphan',
            doc="""
            Sequence of events for the user.
            """))

    type_code = sa.Column(sa.Integer(), nullable=False, doc="""
    Type code for the event.
    """)

    occurred = sa.Column(sa.DateTime(), nullable=True, default=datetime.datetime.utcnow, doc="""
    Timestamp at which the event occurred.
    """)
