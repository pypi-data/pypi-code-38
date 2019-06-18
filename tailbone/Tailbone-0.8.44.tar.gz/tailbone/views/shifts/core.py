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
Views for employee shifts
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six

from rattail.db import model
from rattail.time import localtime
from rattail.util import pretty_hours, hours_as_decimal

from webhelpers2.html import tags, HTML

from tailbone.views import MasterView


def render_shift_length(shift, field):
    if not shift.start_time or not shift.end_time:
        return ""
    if shift.end_time < shift.start_time:
        return "??"
    length = shift.end_time - shift.start_time
    return HTML.tag('span', title="{} hrs".format(hours_as_decimal(length)), c=[pretty_hours(length)])


class ScheduledShiftsView(MasterView):
    """
    Master view for employee scheduled shifts.
    """
    model_class = model.ScheduledShift
    url_prefix = '/shifts/scheduled'

    grid_columns = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    form_fields = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    def configure_grid(self, g):
        g.joiners['employee'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['employee'] = g.make_filter('employee', model.Person.display_name,
                                              default_active=True, default_verb='contains')

        g.set_sort_defaults('start_time', 'desc')

        g.set_renderer('length', render_shift_length)

        g.set_label('employee', "Employee Name")

    def configure_form(self, f):
        super(ScheduledShiftsView, self).configure_form(f)

        f.set_renderer('length', render_shift_length)


class WorkedShiftsView(MasterView):
    """
    Master view for employee worked shifts.
    """
    model_class = model.WorkedShift
    url_prefix = '/shifts/worked'
    results_downloadable_xlsx = True
    has_versions = True

    grid_columns = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    form_fields = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    def configure_grid(self, g):
        super(WorkedShiftsView, self).configure_grid(g)

        g.joiners['employee'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['employee'] = g.make_filter('employee', model.Person.display_name)
        g.sorters['employee'] = g.make_sorter(model.Person.display_name)

        g.joiners['store'] = lambda q: q.join(model.Store)
        g.filters['store'] = g.make_filter('store', model.Store.name)
        g.sorters['store'] = g.make_sorter(model.Store.name)

        # TODO: these sorters should be automatic once we fix the schema
        g.sorters['start_time'] = g.make_sorter(model.WorkedShift.punch_in)
        g.sorters['end_time'] = g.make_sorter(model.WorkedShift.punch_out)
        # TODO: same goes for these renderers
        g.set_type('start_time', 'datetime')
        g.set_type('end_time', 'datetime')
        # (but we'll still have to set this)
        g.set_sort_defaults('start_time', 'desc')

        g.set_renderer('length', render_shift_length)

        g.set_label('employee', "Employee Name")
        g.set_label('store', "Store Name")
        g.set_label('punch_in', "Start Time")
        g.set_label('punch_out', "End Time")

    def get_instance_title(self, shift):
        time = shift.start_time or shift.end_time
        date = localtime(self.rattail_config, time).date()
        return "WorkedShift: {}, {}".format(shift.employee, date)

    def configure_form(self, f):
        super(WorkedShiftsView, self).configure_form(f)

        f.set_readonly('employee')
        f.set_renderer('employee', self.render_employee)

        f.set_renderer('length', render_shift_length)
        if self.editing:
            f.remove('length')

    def render_employee(self, shift, field):
        employee = shift.employee
        if not employee:
            return ""
        text = six.text_type(employee)
        url = self.request.route_url('employees.view', uuid=employee.uuid)
        return tags.link_to(text, url)

    def get_xlsx_fields(self):
        fields = super(WorkedShiftsView, self).get_xlsx_fields()

        # add employee name
        i = fields.index('employee_uuid')
        fields.insert(i + 1, 'employee_name')

        # add hours
        fields.append('hours')

        return fields

    def get_xlsx_row(self, shift, fields):
        row = super(WorkedShiftsView, self).get_xlsx_row(shift, fields)

        # localize start and end times (Excel requires time with no zone)
        if shift.punch_in:
            row['punch_in'] = localtime(self.rattail_config, shift.punch_in, from_utc=True, tzinfo=False)
        if shift.punch_out:
            row['punch_out'] = localtime(self.rattail_config, shift.punch_out, from_utc=True, tzinfo=False)

        # add employee name
        row['employee_name'] = shift.employee.person.display_name

        # add hours
        if shift.punch_in and shift.punch_out:
            if shift.punch_in <= shift.punch_out:
                row['hours'] = hours_as_decimal(shift.punch_out - shift.punch_in, places=4)
            else:
                row['hours'] = "??"
        elif shift.punch_in or shift.punch_out:
            row['hours'] = "??"
        else:
            row['hours'] = None

        return row


def includeme(config):
    ScheduledShiftsView.defaults(config)
    WorkedShiftsView.defaults(config)
