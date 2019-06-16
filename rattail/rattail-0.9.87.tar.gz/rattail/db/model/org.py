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
Data Models for Organization etc.
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db.model import Base, uuid_column


@six.python_2_unicode_compatible
class Department(Base):
    """
    Represents an organizational department.
    """
    __tablename__ = 'department'
    __versioned__ = {}

    uuid = uuid_column()

    number = sa.Column(sa.Integer(), nullable=True, doc="""
    Presumably unique number for the department, as integer.
    """)

    name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name for the department.
    """)

    product = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the department may be used for product
    organization, irrespective of its :attr:`personnel` flag.
    """)

    personnel = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the department may be used for personnel
    organization, irrespective of its :attr:`product` flag.
    """)

    exempt_from_gross_sales = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether items in this department should (not) contribute to
    gross sales figures.  The SIL book says this about it:

       Dollar sales are not to be included in gross sales. (i.e., Postage
       Stamps, Lottery Tickets, etc.).
    """)

    def __str__(self):
        return self.name or ''


@six.python_2_unicode_compatible
class Subdepartment(Base):
    """
    Represents an organizational subdepartment.
    """
    __tablename__ = 'subdepartment'
    __table_args__ = (
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='subdepartment_fk_department'),
    )
    __versioned__ = {}

    uuid = uuid_column()
    number = sa.Column(sa.Integer())
    name = sa.Column(sa.String(length=30))
    department_uuid = sa.Column(sa.String(length=32))

    def __str__(self):
        return self.name or ''


Department.subdepartments = orm.relationship(
    Subdepartment,
    backref='department',
    order_by=Subdepartment.name)


@six.python_2_unicode_compatible
class Category(Base):
    """
    Represents an organizational category for products.
    """
    __tablename__ = 'category'
    __table_args__ = (
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='category_fk_department'),
        sa.UniqueConstraint('code', name='category_uq_code'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    code = sa.Column(sa.String(length=20), nullable=True, doc="""
    Unique code for the category, as string.
    """)

    number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number for the category.  NOTE: Most code leverages the :attr:`code`
    instead of this number, which is essentially ignored.
    """)

    name = sa.Column(sa.String(length=50), nullable=True, doc="""
    Descriptive name for the category.
    """)

    department_uuid = sa.Column(sa.String(length=32))
    department = orm.relationship(Department, doc="""
    Reference to the :class:`Department` to which this category belongs, if
    applicable.
    """)

    def __str__(self):
        return self.name or ''


@six.python_2_unicode_compatible
class Family(Base):
    """
    Represents an organizational family for products.
    """
    __tablename__ = 'family'
    __versioned__ = {}

    uuid = uuid_column()
    code = sa.Column(sa.Integer())
    name = sa.Column(sa.String(length=50))

    def __str__(self):
        return self.name or ''


@six.python_2_unicode_compatible
class ReportCode(Base):
    """
    Represents an organizational "report code" for products.
    """
    __tablename__ = 'report_code'
    __table_args__ = (
        sa.UniqueConstraint('code', name='report_code_uq_code'),
    )
    __versioned__ = {}

    uuid = uuid_column()
    code = sa.Column(sa.Integer(), nullable=False)
    name = sa.Column(sa.String(length=100), nullable=True)

    def __str__(self):
        if not self.code:
            return ''
        return "{} - {}".format(self.code, self.name or '')


@six.python_2_unicode_compatible
class DepositLink(Base):
    """
    Represents a bottle or similar deposit, to which an item may be linked.
    """
    __tablename__ = 'deposit_link'
    __table_args__ = (
        sa.UniqueConstraint('code', name='deposit_link_uq_code'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    code = sa.Column(sa.String(length=20), nullable=False, doc="""
    Unique "code" for the deposit link.
    """)

    description = sa.Column(sa.String(length=255), nullable=True)
    amount = sa.Column(sa.Numeric(precision=5, scale=2), nullable=False)

    def __str__(self):
        if self.description:
            return self.description
        return "${:0.2f}".format(self.amount)
