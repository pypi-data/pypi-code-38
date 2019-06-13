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
Data Models for Members
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list

from rattail.db.model import (
    Base, uuid_column,
    Person, Customer,
    PhoneNumber, EmailAddress, MailingAddress,
)


class Member(Base):
    """
    Represents a "member" account.
    """
    __tablename__ = 'member'
    __table_args__ = (
        sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='member_fk_person'),
        sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='member_fk_customer'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    id = sa.Column(sa.String(length=20), nullable=True, doc="""
    ID string for the member, if known/relevant.
    """)

    person_uuid = sa.Column(sa.String(length=32), nullable=True)
    person = orm.relationship(
        Person,
        doc="""
        Reference to the Person to which this Member record pertains, if applicable.
        """,
        backref=orm.backref(
            'member',
            uselist=False,
            doc="""
            Reference to the Member record for this Person, or ``None``.
            """),
    )

    customer_uuid = sa.Column(sa.String(length=32), nullable=True)
    customer = orm.relationship(
        Customer,
        doc="""
        Reference to the Customer to which this Member record pertains, if applicable.
        """,
        backref=orm.backref(
            'member',
            uselist=False,
            doc="""
            Reference to the Member record for this Customer, or ``None``.
            """),
    )

    joined = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the member first joined.
    """)

    active = sa.Column(sa.Boolean(), nullable=False, default=True, doc="""
    Flag indicating whether the member account is "active" (i.e. joined and not
    yet withdrawn etc.).
    """)

    equity_current = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the member account's equity is "current".
    """)

    equity_total = sa.Column(sa.Numeric(precision=5, scale=2), nullable=True, doc="""
    Current equity total for the member account.
    """)

    equity_payment_due = sa.Column(sa.Date(), nullable=True, doc="""
    Date by which the next equity payment must be made, if applicable.
    """)

    equity_last_paid = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the last equity payment was made, if applicable.
    """)

    equity_payment_credit = sa.Column(sa.Numeric(precision=5, scale=2), nullable=False, default=0, doc="""
    Current amount of equity which is treated as "credit" toward the member's
    next true (minimal) equity payment.
    """)

    withdrew = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which member withdrew, if applicable.
    """)

    def __str__(self):
        if six.PY2:
            return unicode(self).encode('utf_8')
        return str(self.person or self.customer or "")

    if six.PY2:
        def __unicode__(self):
            return unicode(self.person or self.customer or "")

    def add_email_address(self, address, type='Home'):
        email = MemberEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = MemberPhoneNumber(number=number, type=type)
        self.phones.append(phone)


class MemberPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a Member.
    """

    __mapper_args__ = {'polymorphic_identity': 'Member'}


Member.phones = orm.relationship(
    MemberPhoneNumber,
    backref='member',
    primaryjoin=MemberPhoneNumber.parent_uuid == Member.uuid,
    foreign_keys=[MemberPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=MemberPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Member.phone = orm.relationship(
    MemberPhoneNumber,
    primaryjoin=sa.and_(
        MemberPhoneNumber.parent_uuid == Member.uuid,
        MemberPhoneNumber.preference == 1),
    foreign_keys=[MemberPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class MemberEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Member`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Member'}


Member.emails = orm.relationship(
    MemberEmailAddress,
    backref='member',
    primaryjoin=MemberEmailAddress.parent_uuid == Member.uuid,
    foreign_keys=[MemberEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=MemberEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Member.email = orm.relationship(
    MemberEmailAddress,
    primaryjoin=sa.and_(
        MemberEmailAddress.parent_uuid == Member.uuid,
        MemberEmailAddress.preference == 1),
    foreign_keys=[MemberEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class MemberMailingAddress(MailingAddress):
    """
    Represents a mailing address for a member
    """
    __mapper_args__ = {'polymorphic_identity': 'Member'}


Member.addresses = orm.relationship(
    MemberMailingAddress,
    backref='member',
    primaryjoin=MemberMailingAddress.parent_uuid == Member.uuid,
    foreign_keys=[MemberMailingAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=MemberMailingAddress.preference,
    cascade='all, delete-orphan')

Member.address = orm.relationship(
    MemberMailingAddress,
    primaryjoin=sa.and_(
        MemberMailingAddress.parent_uuid == Member.uuid,
        MemberMailingAddress.preference == 1),
    foreign_keys=[MemberMailingAddress.parent_uuid],
    uselist=False,
    viewonly=True)
