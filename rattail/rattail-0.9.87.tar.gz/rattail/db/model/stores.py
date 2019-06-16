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
Data Models for Stores
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column
from .contact import PhoneNumber, EmailAddress


@six.python_2_unicode_compatible
class Store(Base):
    """
    Represents a store (physical or otherwise) within the organization.
    """
    __tablename__ = 'store'
    __versioned__ = {}

    uuid = uuid_column()
    id = sa.Column(sa.String(length=10))
    name = sa.Column(sa.String(length=100))
    database_key = sa.Column(sa.String(length=30))

    def __str__(self):
        return str(self.name or '')

    def add_email_address(self, address, type='Info'):
        email = StoreEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Voice'):
        phone = StorePhoneNumber(number=number, type=type)
        self.phones.append(phone)


class StorePhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a store.
    """

    __mapper_args__ = {'polymorphic_identity': 'Store'}


Store.phones = relationship(
    StorePhoneNumber,
    backref='store',
    primaryjoin=StorePhoneNumber.parent_uuid == Store.uuid,
    foreign_keys=[StorePhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=StorePhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Store.phone = relationship(
    StorePhoneNumber,
    primaryjoin=sa.and_(
        StorePhoneNumber.parent_uuid == Store.uuid,
        StorePhoneNumber.preference == 1),
    foreign_keys=[StorePhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class StoreEmailAddress(EmailAddress):
    """
    Represents an email address associated with a store.
    """

    __mapper_args__ = {'polymorphic_identity': 'Store'}


Store.emails = relationship(
    StoreEmailAddress,
    backref='store',
    primaryjoin=StoreEmailAddress.parent_uuid == Store.uuid,
    foreign_keys=[StoreEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=StoreEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Store.email = relationship(
    StoreEmailAddress,
    primaryjoin=sa.and_(
        StoreEmailAddress.parent_uuid == Store.uuid,
        StoreEmailAddress.preference == 1),
    foreign_keys=[StoreEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)
