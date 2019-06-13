# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Data Models for People
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column, Note
from .contact import PhoneNumber, EmailAddress, MailingAddress
from rattail.db.util import normalize_full_name


# TODO: deprecate/remove this
def get_person_display_name(first_name, last_name):
    return normalize_full_name(first_name, last_name)

# TODO: rename this?
def get_person_display_name_from_context(context):
    first_name = context.current_parameters.get('first_name')
    last_name = context.current_parameters.get('last_name')
    return normalize_full_name(first_name, last_name)


class Person(Base):
    """
    Represents a real, living and breathing person.

    (Or, at least was previously living and breathing, in the case of the
    deceased.)
    """
    __tablename__ = 'person'
    __versioned__ = {
        'exclude': ['modified'],
    }

    uuid = uuid_column()
    first_name = sa.Column(sa.String(length=50), nullable=True)
    middle_name = sa.Column(sa.String(length=50), nullable=True)
    last_name = sa.Column(sa.String(length=50), nullable=True)
    # TODO: rename this to 'full_name' at some point...?
    display_name = sa.Column(sa.String(length=100), nullable=True)
    modified = sa.Column(sa.DateTime(), nullable=True, onupdate=datetime.datetime.utcnow)

    users = orm.relationship(
        'User', doc="""
        List of user accounts associated with this person.
        """)

    def __str__(self):
        if six.PY2:
            return unicode(self).encode('utf8')
        return self.display_name or ""

    if six.PY2:
        def __unicode__(self):
            return self.display_name or ""

    def add_email_address(self, address, type='Home'):
        email = PersonEmailAddress(address=address, type=type)
        self.emails.append(email)
        return email

    def add_phone_number(self, number, type='Home'):
        phone = PersonPhoneNumber(number=number, type=type)
        self.phones.append(phone)
        return phone

    def first_valid_email(self):
        """
        Returns the first :class:`Email` which has not been marked invalid, or ``None``.
        """
        for email in self.emails:
            if not email.invalid:
                return email

    def first_valid_email_address(self):
        """
        Returns the first email address which has not been marked invalid, or ``None``.
        """
        email = self.first_valid_email()
        if email:
            return email.address

    def only_customer(self):
        """
        Convenience method to retrieve the one and only ``Customer`` record
        which is associated with this person.  An error will be raised if there
        is not exactly one customer associated.
        """
        if len(self.customers) != 1:
            raise ValueError("person should have 1 customer but instead has {}: {}".format(
                len(self.customers), self))
        return self.customers[0]


class PersonPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a person.
    """

    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person.phones = orm.relationship(
    PersonPhoneNumber,
    primaryjoin=PersonPhoneNumber.parent_uuid == Person.uuid,
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan',
    doc="""
    Sequence of :class:`PersonPhoneNUmber` instances which belong to the
    person.
    """,
    backref=orm.backref(
        'person',
        doc="""
        Reference to the :class:`Person` instance to which the phone number
        belongs.
        """),
)

Person.phone = orm.relationship(
    PersonPhoneNumber,
    primaryjoin=sa.and_(
        PersonPhoneNumber.parent_uuid == Person.uuid,
        PersonPhoneNumber.preference == 1,
        ),
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class PersonEmailAddress(EmailAddress):
    """
    Represents an email address associated with a person.
    """

    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person.emails = orm.relationship(
    PersonEmailAddress,
    primaryjoin=PersonEmailAddress.parent_uuid == Person.uuid,
    foreign_keys=[PersonEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan',
    doc="""
    Sequence of :class:`PersonEmailAddress` instances which belong to the
    person.
    """,
    backref=orm.backref(
        'person',
        doc="""
        Reference to the :class:`Person` instance to which the email address
        belongs.
        """),
)

Person.email = orm.relationship(
    PersonEmailAddress,
    primaryjoin=sa.and_(
        PersonEmailAddress.parent_uuid == Person.uuid,
        PersonEmailAddress.preference == 1,
        ),
    foreign_keys=[PersonEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class PersonMailingAddress(MailingAddress):
    """
    Represents a physical / mailing address associated with a person.
    """

    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person.addresses = orm.relationship(
    PersonMailingAddress,
    backref='person',
    primaryjoin=PersonMailingAddress.parent_uuid == Person.uuid,
    foreign_keys=[PersonMailingAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonMailingAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Person.address = orm.relationship(
    PersonMailingAddress,
    primaryjoin=sa.and_(
        PersonMailingAddress.parent_uuid == Person.uuid,
        PersonMailingAddress.preference == 1,
        ),
    foreign_keys=[PersonMailingAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class PersonNote(Note):
    """
    Represents a note attached to a person.
    """
    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person.notes = orm.relationship(
    PersonNote,
    primaryjoin=PersonNote.parent_uuid == Person.uuid,
    foreign_keys=[PersonNote.parent_uuid],
    order_by=PersonNote.created,
    cascade='all, delete-orphan',
    doc="""
    Sequence of notes which belong to the person.
    """,
    backref=orm.backref(
        'person',
        doc="""
        Reference to the person to which the note is attached.
        """))
