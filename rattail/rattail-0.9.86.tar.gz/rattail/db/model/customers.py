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
Data Models for Customers
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from rattail.db.model import Base, uuid_column, getset_factory
from rattail.db.model import PhoneNumber, EmailAddress, MailingAddress, Person, Note


class Customer(Base):
    """
    Represents a customer account.

    Customer accounts may consist of more than one person, in some cases.
    """
    __tablename__ = 'customer'
    __versioned__ = {}

    uuid = uuid_column()

    id = sa.Column(sa.String(length=20), nullable=True, doc="""
    String ID for the customer, if known/relevant.  This may or may not
    correspond to the :attr:`number`, depending on your system.
    """)

    number = sa.Column(sa.Integer(), nullable=True, doc="""
    Customer number, if known/relevant.  This may or may not correspond to the
    :attr:`id`, depending on your system.
    """)

    name = sa.Column(sa.String(length=255))
    email_preference = sa.Column(sa.Integer())

    wholesale = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the customer is a "wholesale" account - whatever
    that happens to mean for your business logic.
    """)

    active_in_pos = sa.Column(sa.Boolean(), nullable=True, doc="""
    Whether or not the customer account should be "active" within the POS
    system, if applicable.  Whether/how this field is populated and/or
    leveraged are up to your system.
    """)

    active_in_pos_sticky = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether or not the customer account should *always* be "active" within the
    POS system.  This field may be useful if :attr:`active_in_pos` gets set
    dynamically.
    """)

    def __str__(self):
        if six.PY2:
            return unicode(self).encode('utf8')
        return self.name or ""

    if six.PY2:
        def __unicode__(self):
            return self.name or ""

    def add_email_address(self, address, type='Home'):
        email = CustomerEmailAddress(address=address, type=type)
        self.emails.append(email)
        return email

    def add_phone_number(self, number, type='Home'):
        phone = CustomerPhoneNumber(number=number, type=type)
        self.phones.append(phone)
        return phone

    def add_mailing_address(self, **kwargs):
        addr = CustomerMailingAddress(**kwargs)
        self.addresses.append(addr)
        return addr

    @property
    def employee(self):
        """
        Return the employee associated with the customer, if any.  Assumes a
        certain "typical" relationship path.
        """
        if self.person:
            return self.person.employee

    def only_person(self):
        """
        Convenience method to retrieve the one and only Person record which is
        associated with this customer.  An error will be raised if there is not
        exactly one person associated.
        """
        if len(self.people) != 1:
            raise ValueError("customer should have 1 person but instead has {}: {}".format(
                len(self.people), self))
        return self.people[0]


class CustomerPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Customer`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Customer'}


Customer.phones = orm.relationship(
    CustomerPhoneNumber,
    backref='customer',
    primaryjoin=CustomerPhoneNumber.parent_uuid == Customer.uuid,
    foreign_keys=[CustomerPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=CustomerPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Customer.phone = orm.relationship(
    CustomerPhoneNumber,
    primaryjoin=sa.and_(
        CustomerPhoneNumber.parent_uuid == Customer.uuid,
        CustomerPhoneNumber.preference == 1),
    foreign_keys=[CustomerPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class CustomerEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Customer`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Customer'}


Customer.emails = orm.relationship(
    CustomerEmailAddress,
    backref='customer',
    primaryjoin=CustomerEmailAddress.parent_uuid == Customer.uuid,
    foreign_keys=[CustomerEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=CustomerEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Customer.email = orm.relationship(
    CustomerEmailAddress,
    primaryjoin=sa.and_(
        CustomerEmailAddress.parent_uuid == Customer.uuid,
        CustomerEmailAddress.preference == 1),
    foreign_keys=[CustomerEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class CustomerMailingAddress(MailingAddress):
    """
    Represents a mailing address for a customer
    """
    __mapper_args__ = {'polymorphic_identity': 'Customer'}

Customer.addresses = orm.relationship(
    CustomerMailingAddress,
    backref='customer',
    primaryjoin=CustomerMailingAddress.parent_uuid == Customer.uuid,
    foreign_keys=[CustomerMailingAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=CustomerMailingAddress.preference,
    cascade='all, delete-orphan')

Customer.address = orm.relationship(
    CustomerMailingAddress,
    primaryjoin=sa.and_(
        CustomerMailingAddress.parent_uuid == Customer.uuid,
        CustomerMailingAddress.preference == 1),
    foreign_keys=[CustomerMailingAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class CustomerNote(Note):
    """
    Represents a note attached to a customer.
    """
    __mapper_args__ = {'polymorphic_identity': 'Customer'}

    customer = orm.relationship(
        Customer,
        primaryjoin='Customer.uuid == CustomerNote.parent_uuid',
        foreign_keys='CustomerNote.parent_uuid',
        doc="""
        Reference to the customer to which this note is attached.
        """,
        backref=orm.backref(
            'notes',
            primaryjoin='CustomerNote.parent_uuid == Customer.uuid',
            foreign_keys='CustomerNote.parent_uuid',
            order_by='CustomerNote.created',
            cascade='all, delete-orphan',
            doc="""
            Sequence of notes which belong to the customer.
            """))


@six.python_2_unicode_compatible
class CustomerGroup(Base):
    """
    Represents an arbitrary group to which customers may belong.
    """
    __tablename__ = 'customer_group'
    __versioned__ = {}

    uuid = uuid_column()
    id = sa.Column(sa.String(length=20))
    name = sa.Column(sa.String(length=255))

    def __str__(self):
        return self.name or ''


class CustomerGroupAssignment(Base):
    """
    Represents the assignment of a customer to a group.
    """
    __tablename__ = 'customer_x_group'
    __table_args__ = (
        sa.ForeignKeyConstraint(['group_uuid'], ['customer_group.uuid'], name='customer_x_group_fk_group'),
        sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='customer_x_group_fk_customer'),
    )
    __versioned__ = {}

    uuid = uuid_column()
    customer_uuid = sa.Column(sa.String(length=32), nullable=False)
    group_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)

    group = orm.relationship(CustomerGroup)


Customer._groups = orm.relationship(
    CustomerGroupAssignment, backref='customer',
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=CustomerGroupAssignment.ordinal,
    cascade='save-update, merge, delete, delete-orphan')

Customer.groups = association_proxy(
    '_groups', 'group',
    getset_factory=getset_factory,
    creator=lambda g: CustomerGroupAssignment(group=g))


class CustomerPerson(Base):
    """
    Represents the association between a person and a customer account.
    """
    __tablename__ = 'customer_x_person'
    __table_args__ = (
        sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='customer_x_person_fk_customer'),
        sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='customer_x_person_fk_person'),
    )
    __versioned__ = {}

    uuid = uuid_column()
    customer_uuid = sa.Column(sa.String(length=32), nullable=False)
    person_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)

    customer = orm.relationship(Customer, back_populates='_people')

    person = orm.relationship(Person, back_populates='_customers')


Customer._people = orm.relationship(
    CustomerPerson, back_populates='customer',
    primaryjoin=CustomerPerson.customer_uuid == Customer.uuid,
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=CustomerPerson.ordinal,
    cascade='save-update, merge, delete, delete-orphan')

Customer.people = association_proxy(
    '_people', 'person',
    getset_factory=getset_factory,
    creator=lambda p: CustomerPerson(person=p))

Customer._person = orm.relationship(
    CustomerPerson,
    primaryjoin=sa.and_(
        CustomerPerson.customer_uuid == Customer.uuid,
        CustomerPerson.ordinal == 1),
    uselist=False,
    viewonly=True)

Customer.person = association_proxy(
    '_person', 'person',
    getset_factory=getset_factory)

Person._customers = orm.relationship(
    CustomerPerson, back_populates='person',
    primaryjoin=CustomerPerson.person_uuid == Person.uuid,
    cascade='all, delete-orphan',
    viewonly=True)

Person.customers = association_proxy('_customers', 'customer',
                                     getset_factory=getset_factory,
                                     creator=lambda c: CustomerPerson(customer=c))
