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
Data Models for Employees
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column, getset_factory
from .people import Person
from .contact import PhoneNumber, EmailAddress
from .stores import Store
from .org import Department


class Employee(Base):
    """
    Represents an employee within the organization.
    """
    __tablename__ = 'employee'
    __table_args__ = (
        sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='employee_fk_person'),
        sa.UniqueConstraint('person_uuid', name='employee_uq_person'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    id = sa.Column(sa.Integer(), nullable=True, doc="""
    Numeric ID for the employee, if applicable/known.
    """)

    person_uuid = sa.Column(sa.String(length=32), nullable=False)
    person = orm.relationship(Person, back_populates='employee', doc="""
    Reference to the person to whom this employee record pertains.
    """)

    status = sa.Column(sa.Integer(), nullable=True, doc="""
    Status code for the employee, e.g. current vs. former.
    """)

    display_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Display name for the employee.  Whereas the *person's* display name is
    generally their full name, this *employee* display name is often an
    abbreviated version which is visible on printed receipts, etc.
    """)

    full_time = sa.Column(sa.Boolean(), nullable=True, doc="""
    Simple flag to indicate if employee is considered full-time.  This flag
    should theoretically only be relevant if employee is also *current*.
    """)

    full_time_start = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which employee became full time, if known/relevant.
    """)

    first_name = association_proxy('person', 'first_name',
                                   getset_factory=getset_factory,
                                   creator=lambda n: Person(first_name=n))
    last_name = association_proxy('person', 'last_name',
                                  getset_factory=getset_factory,
                                  creator=lambda n: Person(last_name=n))
    user = association_proxy('person', 'user')

    def __str__(self):
        if six.PY2:
            return unicode(self).encode('utf8')
        return str(self.person or "")

    if six.PY2:
        def __unicode__(self):
            return unicode(self.person or "")

    @property
    def customers(self):
        return self.person.customers

    def add_email_address(self, address, type='Home'):
        email = EmployeeEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = EmployeePhoneNumber(number=number, type=type)
        self.phones.append(phone)

    def get_current_history(self):
        """
        Returns the "current" history record for the employee, if found.
        """
        if self.history:
            history = sorted(self.history, key=lambda h: (h.start_date, h.end_date))
            return history[-1]


Person.employee = orm.relationship(
    Employee,
    back_populates='person',
    uselist=False,
    doc="""
    Reference to the :class:`Employee` record for the person, if there is one.
    """)


class EmployeePhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Employee`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Employee'}


Employee.phones = orm.relationship(
    EmployeePhoneNumber,
    backref='employee',
    primaryjoin=EmployeePhoneNumber.parent_uuid == Employee.uuid,
    foreign_keys=[EmployeePhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=EmployeePhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Employee.phone = orm.relationship(
    EmployeePhoneNumber,
    primaryjoin=sa.and_(
        EmployeePhoneNumber.parent_uuid == Employee.uuid,
        EmployeePhoneNumber.preference == 1),
    foreign_keys=[EmployeePhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class EmployeeEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Employee`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Employee'}


Employee.emails = orm.relationship(
    EmployeeEmailAddress,
    backref='employee',
    primaryjoin=EmployeeEmailAddress.parent_uuid == Employee.uuid,
    foreign_keys=[EmployeeEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=EmployeeEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Employee.email = orm.relationship(
    EmployeeEmailAddress,
    primaryjoin=sa.and_(
        EmployeeEmailAddress.parent_uuid == Employee.uuid,
        EmployeeEmailAddress.preference == 1),
    foreign_keys=[EmployeeEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class EmployeeStore(Base):
    """
    Represents the association between an employee and a store.
    """
    __tablename__ = 'employee_x_store'
    __table_args__ = (
        sa.ForeignKeyConstraint(['employee_uuid'], ['employee.uuid'], name='employee_x_store_fk_employee'),
        sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='employee_x_store_fk_store'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    employee_uuid = sa.Column(sa.String(length=32), nullable=False)
    store_uuid = sa.Column(sa.String(length=32), nullable=False)

    employee = orm.relationship(
        Employee,
        backref=orm.backref('_stores', cascade='all, delete-orphan'))

    store = orm.relationship(
        Store,
        order_by=Store.name,
        backref=orm.backref('_employees', cascade='all, delete-orphan'))

Employee.stores = association_proxy(
    '_stores', 'store',
    creator=lambda x: EmployeeStore(store=x),
    getset_factory=getset_factory)

Store.employees = association_proxy(
    '_employees', 'employee',
    creator=lambda x: EmployeeStore(employee=x),
    getset_factory=getset_factory)


class EmployeeDepartment(Base):
    """
    Represents the association between an employee and a department.
    """
    __tablename__ = 'employee_x_department'
    __table_args__ = (
        sa.ForeignKeyConstraint(['employee_uuid'], ['employee.uuid'], name='employee_x_department_fk_employee'),
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='employee_x_department_fk_department'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    employee_uuid = sa.Column(sa.String(length=32), nullable=False)
    department_uuid = sa.Column(sa.String(length=32), nullable=False)

    employee = orm.relationship(
        Employee,
        backref=orm.backref('_departments', cascade='all, delete-orphan'))

    department = orm.relationship(
        Department,
        order_by=Department.name,
        backref=orm.backref('_employees', cascade='all, delete-orphan'))

Employee.departments = association_proxy(
    '_departments', 'department',
    creator=lambda x: EmployeeDepartment(department=x),
    getset_factory=getset_factory)

Department.employees = association_proxy(
    '_employees', 'employee',
    creator=lambda x: EmployeeDepartment(employee=x),
    getset_factory=getset_factory)


class EmployeeHistory(Base):
    """
    Represents a period of time for which a person was employed by the organization.
    """
    __tablename__ = 'employee_history'
    __table_args__ = (
        sa.ForeignKeyConstraint(['employee_uuid'], ['employee.uuid'], name='employee_history_fk_employee'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    employee_uuid = sa.Column(sa.String(length=32), nullable=False)
    employee = orm.relationship(
        Employee, doc="""
        Reference to the employee to which this history record pertains.
        """,
        backref=orm.backref(
            'history',
            order_by='EmployeeHistory.start_date',
            doc="""
            Sequence of history records for the employee.
            """))

    start_date = sa.Column(sa.Date(), nullable=False, doc="""
    Date on which the employee became active in the organization.
    """)

    end_date = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the employee became *inactive*.
    """)
