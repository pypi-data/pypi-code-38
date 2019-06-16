# -*- coding: utf-8 -*-
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
Data models for employee work shifts
"""

from __future__ import unicode_literals, absolute_import

import six

import sqlalchemy as sa
from sqlalchemy import orm

from .core import Base, uuid_column
from rattail.time import localtime, make_utc


class ShiftMixin(object):
    """
    Mixin for logic common to both scheduled and worked shifts.
    """

    @property
    def length(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time

    def get_date(self, config):
        """
        Return the effective date for the shift, according to the given config
        (i.e. timezone).
        """
        time = self.end_time or self.start_time
        assert time
        time = make_utc(time, tzinfo=True)
        return localtime(config, time).date()

    def get_display(self, config):
        """
        Return a simple string for displaying the shift, according to the given
        config (i.e. timezone).
        """
        return '{} - {}'.format(self._format_punch(config, self.start_time),
                                self._format_punch(config, self.end_time))

    def _format_punch(self, config, time):
        if time is None:
            return '??'
        time = localtime(config, make_utc(time, tzinfo=True))
        return time.strftime('%I:%M %p')


class ScheduledShift(Base, ShiftMixin):
    """
    Represents a scheduled shift for an employee.
    """
    __tablename__ = 'employee_shift_scheduled'
    __table_args__ = (
        sa.ForeignKeyConstraint(['employee_uuid'], ['employee.uuid'], name='employee_shift_scheduled_fk_employee'),
        sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='employee_shift_scheduled_fk_store'),
    )

    uuid = uuid_column()

    employee_uuid = sa.Column(sa.String(length=32), nullable=False)

    employee = orm.relationship(
        'Employee',
        doc="""
        Reference to the :class:`rattail.db.model.Employee` instance whose
        shift this is.
        """,
        backref=orm.backref('scheduled_shifts', doc="""
        Sequence of :class:`rattail.db.model.ScheduledShift` instances for the
        employee.
        """))

    store_uuid = sa.Column(sa.String(length=32), nullable=True)

    store = orm.relationship(
        'Store',
        doc="""
        Reference to the :class:`rattail.db.model.Store` instance, representing
        the location at which the shift is scheduled, if applicable/known.
        """)

    start_time = sa.Column(sa.DateTime(), nullable=False, doc="""
    Date and time when the shift is scheduled to start.
    """)

    end_time = sa.Column(sa.DateTime(), nullable=False, doc="""
    Date and time when the shift is scheduled to end.
    """)


@six.python_2_unicode_compatible
class WorkedShift(Base, ShiftMixin):
    """
    Represents a shift actually *worked* by an employee.  (Either ``punch_in``
    or ``punch_out`` is generally assumed to be non-null.)
    """
    __tablename__ = 'employee_shift_worked'
    __table_args__ = (
        sa.ForeignKeyConstraint(['employee_uuid'], ['employee.uuid'], name='employee_shift_worked_fk_employee'),
        sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='employee_shift_worked_fk_store'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    employee_uuid = sa.Column(sa.String(length=32), nullable=False)

    employee = orm.relationship(
        'Employee',
        doc="""
        Reference to the :class:`rattail.db.model.Employee` instance whose
        shift this is.
        """,
        backref=orm.backref('worked_shifts', doc="""
        Sequence of :class:`rattail.db.model.WorkedShift` instances for the
        employee.
        """))

    store_uuid = sa.Column(sa.String(length=32), nullable=True)

    store = orm.relationship(
        'Store',
        doc="""
        Reference to the :class:`rattail.db.model.Store` instance, representing
        the location at which the shift was worked, if applicable/known.
        """)

    punch_in = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp representing the punch-in time for the shift.
    """)

    punch_out = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp representing the punch-out time for the shift.
    """)

    # TODO: These are needed to make WorkedShift interchangeable with
    # ScheduledShift for certain UI logic etc.  Perhaps should just rename the
    # 'punch' columns at some point..?
    start_time = orm.synonym('punch_in')
    end_time = orm.synonym('punch_out')

    def __str__(self):
        return str(self.employee or '')
