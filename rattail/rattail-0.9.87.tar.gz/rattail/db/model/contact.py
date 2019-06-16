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
Data Models for Contact Info
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa

from .core import Base, uuid_column


@six.python_2_unicode_compatible
class PhoneNumber(Base):
    """
    Represents a phone (or fax) number associated with a contactable entity.
    """
    __tablename__ = 'phone'
    __versioned__= {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15))
    number = sa.Column(sa.String(length=20), nullable=False)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __str__(self):
        return self.number or ""


@six.python_2_unicode_compatible
class EmailAddress(Base):
    """
    Represents an email address associated with a contactable entity.
    """
    __tablename__ = 'email'
    __versioned__= {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15))
    address = sa.Column(sa.String(length=255), nullable=False)

    invalid = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the email address is *known* to be invalid.
    Defaults to NULL, meaning the validity is "not known".
    """)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __str__(self):
        return self.address or ""


@six.python_2_unicode_compatible
class MailingAddress(Base):
    """
    Represents a physical / mailing address associated with a contactable entity.
    """
    __tablename__ = 'address'
    __versioned__= {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15), nullable=True)

    street = sa.Column(sa.String(length=100), nullable=True)
    street2 = sa.Column(sa.String(length=100), nullable=True)
    city = sa.Column(sa.String(length=60), nullable=True)
    state = sa.Column(sa.String(length=2), nullable=True)
    zipcode = sa.Column(sa.String(length=10), nullable=True)
    invalid = sa.Column(sa.Boolean(), nullable=True)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __str__(self):

        if self.street and self.street2:
            street = '{}, {}'.format(self.street, self.street2)
        else:
            street = self.street or ''

        if self.city and self.state:
            city = '{}, {}'.format(self.city, self.state)
        else:
            city = self.city or self.state or ''

        if street and city and self.zipcode:
            text = '{}, {}  {}'.format(street, city, self.zipcode)
        elif street and city:
            text = '{}, {}'.format(street, city)
        elif street and self.zipcode:
            text = '{}  {}'.format(street, self.zipcode)
        elif city and self.zipcode:
            text = '{}  {}'.format(city, self.zipcode)
        else:
            text = self.zipcode or ''

        return text
